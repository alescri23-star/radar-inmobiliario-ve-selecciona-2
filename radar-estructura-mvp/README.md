# radar-venezuela-2026-2030

Plataforma tecnológica para Venezuela que integra geolocalización, inteligencia inmobiliaria y gestión de reformas. Conecta propietarios, compradores, agencias y profesionales mediante mapas interactivos, análisis de oportunidades y herramientas digitales, facilitando la inversión, la transparencia y el desarrollo empresarial.

No es otro portal de anuncios. El objetivo es construir **una base de datos histórica propia de la oferta real** para:

- detectar inmuebles con **potencial de reforma** (cocinas, baños, cerámica, pisos…);
- estudiar la **demanda de venezolanos en el exterior** y de compradores internacionales.

**Piloto:** Lara (Barquisimeto). **Tesis principal:** Isla de Margarita y los cayos (Los Roques, Morrocoy, Tucacas, Chichiriviche).

## Estructura

```
db/
  schema.sql          Tablas, histórico inmutable y vistas
  seed_zonas.sql      Zonas iniciales (solo Barquisimeto activa)
scraper/
  cliente.py          HTTP respetuoso: robots.txt, pausas, se detiene ante CAPTCHA/login
  fuentes/            Una clase por fuente (plantilla incluida)
  guardar.py          Inserta anuncios y observaciones sin sobrescribir nada
  senales_reforma.py  Puntuación de potencial de reforma (ESTIMACIÓN)
  ejecutar.py         Ejecuta una pasada (simulación por defecto)
docs/
  principios-datos.md Reglas que sigue el proyecto
  hoja-de-ruta.md     Fases del MVP
tests/                Pruebas automáticas
```

## Puesta en marcha

Requisitos: Docker y Python 3.11+.

```bash
cp .env.example .env              # y cambia la contraseña
docker compose up -d              # PostgreSQL + PostGIS con el esquema cargado
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest                            # pruebas
python -m scraper.ejecutar --fuente plantilla --zona Barquisimeto   # simulación
```

La plantilla apunta a un dominio de ejemplo: hay que implementar la primera fuente real antes de ejecutar nada (ver `docs/hoja-de-ruta.md`).

## Principios

El histórico nunca se sobrescribe, nunca se infiere "vendido", los datos ausentes se muestran como `DATO NO DISPONIBLE` y las estimaciones van etiquetadas. Detalle completo en [`docs/principios-datos.md`](docs/principios-datos.md).
