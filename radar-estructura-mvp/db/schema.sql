-- Radar Venezuela — esquema base (PostgreSQL 16 + PostGIS)
-- Principios:
--   * El histórico de precios NUNCA se sobrescribe: cada lectura es una fila nueva en `observaciones`.
--   * Nunca se infiere "vendido" porque un anuncio desaparezca: solo se marca "no_visto".
--   * Dato ausente = NULL en la base; las vistas lo muestran como 'DATO NO DISPONIBLE'.
--   * Las estimaciones se guardan separadas y etiquetadas como tales.

CREATE EXTENSION IF NOT EXISTS postgis;

-- Fuentes de anuncios (portales, redes, agencias)
CREATE TABLE IF NOT EXISTS fuentes (
    id              SERIAL PRIMARY KEY,
    nombre          TEXT NOT NULL UNIQUE,
    url_base        TEXT NOT NULL,
    activa          BOOLEAN NOT NULL DEFAULT FALSE,   -- activar requiere aprobación
    notas_legales   TEXT,                             -- robots.txt, términos de uso revisados
    creada_en       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Zonas de interés (piloto + tesis)
CREATE TABLE IF NOT EXISTS zonas (
    id          SERIAL PRIMARY KEY,
    nombre      TEXT NOT NULL UNIQUE,
    estado_ve   TEXT NOT NULL,                        -- estado venezolano (Lara, Nueva Esparta, Falcón...)
    tipo        TEXT NOT NULL CHECK (tipo IN ('piloto', 'tesis', 'expansion')),
    activa      BOOLEAN NOT NULL DEFAULT FALSE,       -- solo Lara activa en el piloto
    centro      GEOGRAPHY(POINT, 4326),               -- centroide aproximado
    poligono    GEOGRAPHY(MULTIPOLYGON, 4326)         -- límite real, cuando se tenga
);

-- Identidad estable de cada anuncio (una fila por anuncio y fuente)
CREATE TABLE IF NOT EXISTS anuncios (
    id               BIGSERIAL PRIMARY KEY,
    fuente_id        INT NOT NULL REFERENCES fuentes(id),
    id_externo       TEXT NOT NULL,                   -- id del anuncio en la fuente
    url              TEXT NOT NULL,
    zona_id          INT REFERENCES zonas(id),
    tipo_inmueble    TEXT,                            -- casa, apartamento, terreno, local...
    operacion        TEXT CHECK (operacion IN ('venta', 'alquiler')),
    ubicacion        GEOGRAPHY(POINT, 4326),
    ubicacion_precision TEXT CHECK (ubicacion_precision IN ('exacta', 'aproximada', 'zona')),
    primera_vez_visto TIMESTAMPTZ NOT NULL DEFAULT now(),
    ultima_vez_visto  TIMESTAMPTZ NOT NULL DEFAULT now(),
    estado_seguimiento TEXT NOT NULL DEFAULT 'activo'
        CHECK (estado_seguimiento IN ('activo', 'no_visto')),  -- NUNCA 'vendido' por inferencia
    UNIQUE (fuente_id, id_externo)
);

-- Observaciones: append-only. Cada visita al anuncio genera una fila.
CREATE TABLE IF NOT EXISTS observaciones (
    id              BIGSERIAL PRIMARY KEY,
    anuncio_id      BIGINT NOT NULL REFERENCES anuncios(id),
    observado_en    TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    precio          NUMERIC(14,2),
    moneda          TEXT CHECK (moneda IN ('USD', 'VES', 'EUR')),
    m2_construccion NUMERIC(10,2),
    m2_terreno      NUMERIC(10,2),
    habitaciones    SMALLINT,
    banos           SMALLINT,
    titulo          TEXT,
    descripcion     TEXT,
    hash_contenido  TEXT NOT NULL                     -- para detectar cambios reales
);
CREATE INDEX IF NOT EXISTS idx_obs_anuncio_fecha ON observaciones (anuncio_id, observado_en DESC);

-- Bloquear UPDATE y DELETE en observaciones: el histórico es inmutable
CREATE OR REPLACE FUNCTION bloquear_modificacion() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'La tabla % es de solo inserción: el histórico no se modifica', TG_TABLE_NAME;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_observaciones_inmutables ON observaciones;
CREATE TRIGGER trg_observaciones_inmutables
    BEFORE UPDATE OR DELETE ON observaciones
    FOR EACH ROW EXECUTE FUNCTION bloquear_modificacion();

-- Estimaciones e hipótesis (potencial de reforma, etc.), siempre etiquetadas
CREATE TABLE IF NOT EXISTS estimaciones (
    id              BIGSERIAL PRIMARY KEY,
    anuncio_id      BIGINT NOT NULL REFERENCES anuncios(id),
    observacion_id  BIGINT REFERENCES observaciones(id),
    tipo            TEXT NOT NULL,                    -- 'potencial_reforma', ...
    valor           NUMERIC(5,2),                     -- p. ej. puntuación 0-100
    senales         TEXT[],                           -- palabras clave detectadas
    metodo          TEXT NOT NULL,                    -- versión del algoritmo
    etiqueta        TEXT NOT NULL DEFAULT 'ESTIMACIÓN' CHECK (etiqueta IN ('ESTIMACIÓN', 'HIPÓTESIS')),
    creada_en       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Vista: último estado conocido de cada anuncio, con datos ausentes explícitos
CREATE OR REPLACE VIEW v_anuncios_ultimo AS
SELECT
    a.id,
    f.nombre AS fuente,
    z.nombre AS zona,
    a.url,
    COALESCE(a.tipo_inmueble, 'DATO NO DISPONIBLE') AS tipo_inmueble,
    COALESCE(o.precio::text || ' ' || o.moneda, 'DATO NO DISPONIBLE') AS precio,
    COALESCE(o.m2_construccion::text, 'DATO NO DISPONIBLE') AS m2_construccion,
    COALESCE(o.habitaciones::text, 'DATO NO DISPONIBLE') AS habitaciones,
    COALESCE(o.banos::text, 'DATO NO DISPONIBLE') AS banos,
    a.estado_seguimiento,
    a.primera_vez_visto,
    a.ultima_vez_visto,
    o.observado_en AS ultima_observacion
FROM anuncios a
JOIN fuentes f ON f.id = a.fuente_id
LEFT JOIN zonas z ON z.id = a.zona_id
LEFT JOIN LATERAL (
    SELECT * FROM observaciones ob
    WHERE ob.anuncio_id = a.id
    ORDER BY ob.observado_en DESC, ob.id DESC
    LIMIT 1
) o ON TRUE;

-- Vista: cambios de precio a lo largo del tiempo
CREATE OR REPLACE VIEW v_historial_precios AS
SELECT
    anuncio_id,
    observado_en,
    precio,
    moneda,
    precio - LAG(precio) OVER (PARTITION BY anuncio_id ORDER BY observado_en, id) AS variacion
FROM observaciones
WHERE precio IS NOT NULL;
