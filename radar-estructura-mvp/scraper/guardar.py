"""Guarda anuncios leídos en PostgreSQL respetando el histórico.

  * Anuncio nuevo -> se crea en `anuncios`.
  * Siempre se actualiza `ultima_vez_visto`.
  * Solo se inserta una nueva observación si el contenido cambió (hash distinto).
  * Las observaciones nunca se modifican ni se borran.
"""
import hashlib
import json

from .fuentes.base import AnuncioLeido
from . import senales_reforma

CAMPOS_OBS = ("precio", "moneda", "m2_construccion", "m2_terreno", "habitaciones",
              "banos", "titulo", "descripcion")


def hash_contenido(a: AnuncioLeido) -> str:
    datos = {c: getattr(a, c) for c in CAMPOS_OBS}
    return hashlib.sha256(json.dumps(datos, sort_keys=True, default=str).encode()).hexdigest()


def guardar(conn, fuente_id: int, zona_id: int | None, a: AnuncioLeido, visto_en) -> str:
    """Devuelve 'nuevo', 'cambio' o 'sin_cambios'. `visto_en` = marca de tiempo de la pasada."""
    h = hash_contenido(a)
    punto = f"SRID=4326;POINT({a.lon} {a.lat})" if a.lat is not None and a.lon is not None else None
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO anuncios (fuente_id, id_externo, url, zona_id, tipo_inmueble, operacion,
                                  ubicacion, ubicacion_precision, primera_vez_visto, ultima_vez_visto)
            VALUES (%s, %s, %s, %s, %s, %s, %s::geography, %s, %s, %s)
            ON CONFLICT (fuente_id, id_externo) DO UPDATE
                SET ultima_vez_visto = EXCLUDED.ultima_vez_visto, estado_seguimiento = 'activo'
            RETURNING id, (xmax = 0) AS es_nuevo
            """,
            (fuente_id, a.id_externo, a.url, zona_id, a.tipo_inmueble, a.operacion,
             punto, a.ubicacion_precision, visto_en, visto_en),
        )
        anuncio_id, es_nuevo = cur.fetchone()

        cur.execute(
            "SELECT hash_contenido FROM observaciones WHERE anuncio_id = %s "
            "ORDER BY observado_en DESC, id DESC LIMIT 1",
            (anuncio_id,),
        )
        fila = cur.fetchone()
        if fila and fila[0] == h:
            return "sin_cambios"

        cur.execute(
            f"INSERT INTO observaciones (anuncio_id, {', '.join(CAMPOS_OBS)}, hash_contenido) "
            f"VALUES (%s, {', '.join(['%s'] * len(CAMPOS_OBS))}, %s) RETURNING id",
            (anuncio_id, *[getattr(a, c) for c in CAMPOS_OBS], h),
        )
        obs_id = cur.fetchone()[0]

        est = senales_reforma.evaluar(a.titulo, a.descripcion)
        if est["valor"] is not None:
            cur.execute(
                "INSERT INTO estimaciones (anuncio_id, observacion_id, tipo, valor, senales, metodo, etiqueta) "
                "VALUES (%s, %s, 'potencial_reforma', %s, %s, %s, %s)",
                (anuncio_id, obs_id, est["valor"], est["senales"], est["metodo"], est["etiqueta"]),
            )
    return "nuevo" if es_nuevo else "cambio"


def marcar_no_vistos(conn, fuente_id: int, zona_id: int, visto_en) -> int:
    """Anuncios de la zona que no aparecieron en esta pasada -> 'no_visto' (nunca 'vendido')."""
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE anuncios SET estado_seguimiento = 'no_visto' "
            "WHERE fuente_id = %s AND zona_id = %s AND ultima_vez_visto < %s "
            "AND estado_seguimiento = 'activo'",
            (fuente_id, zona_id, visto_en),
        )
        return cur.rowcount
