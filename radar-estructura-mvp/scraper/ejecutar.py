"""Ejecuta una pasada de lectura para una fuente y una zona.

Uso:
    python -m scraper.ejecutar --fuente plantilla --zona Barquisimeto            # simulación
    python -m scraper.ejecutar --fuente plantilla --zona Barquisimeto --guardar  # guarda en BD

Protecciones:
  * Por defecto es una SIMULACIÓN: lee y muestra, no guarda.
  * La zona y la fuente deben estar activas en la base de datos (activarlas = aprobación).
  * Límite de páginas y pausa entre peticiones definidos en .env.
"""
import argparse
import os
from datetime import datetime, timezone

from dotenv import load_dotenv

from .cliente import BloqueoDetectado, ClienteRespetuoso, LimiteAlcanzado
from .fuentes import FUENTES
from . import guardar as g


def main() -> None:
    load_dotenv()
    p = argparse.ArgumentParser()
    p.add_argument("--fuente", required=True, choices=FUENTES.keys())
    p.add_argument("--zona", required=True)
    p.add_argument("--guardar", action="store_true", help="Guardar en la base de datos")
    args = p.parse_args()

    fuente = FUENTES[args.fuente]()
    cliente = ClienteRespetuoso()
    inicio = datetime.now(timezone.utc)
    leidos = []
    pasada_completa = True

    try:
        for url in fuente.urls_listado(args.zona):
            leidos.extend(fuente.parsear_listado(cliente.obtener(url)))
    except (BloqueoDetectado, PermissionError) as e:
        print(f"DETENIDO: {e}")
        return
    except LimiteAlcanzado as e:
        print(f"Aviso: {e}. Se guarda lo leído, pero no se marca nada como 'no_visto'.")
        pasada_completa = False

    print(f"{len(leidos)} anuncios leídos en {cliente.paginas} páginas.")
    if not args.guardar:
        for a in leidos[:10]:
            print(f"  - {a.id_externo} | {a.titulo or 'DATO NO DISPONIBLE'} | "
                  f"{a.precio if a.precio is not None else 'DATO NO DISPONIBLE'} {a.moneda or ''}")
        print("Simulación: no se guardó nada. Usa --guardar para escribir en la base de datos.")
        return

    import psycopg
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM fuentes WHERE nombre = %s AND activa", (fuente.nombre,))
            f = cur.fetchone()
            cur.execute("SELECT id FROM zonas WHERE nombre = %s AND activa", (args.zona,))
            z = cur.fetchone()
        if not f or not z:
            print("DETENIDO: la fuente o la zona no están activas (requieren aprobación).")
            return
        resumen: dict[str, int] = {}
        for a in leidos:
            r = g.guardar(conn, f[0], z[0], a, inicio)
            resumen[r] = resumen.get(r, 0) + 1
        if pasada_completa and leidos:
            resumen["no_visto"] = g.marcar_no_vistos(conn, f[0], z[0], inicio)
    print(f"Guardado: {resumen}")


if __name__ == "__main__":
    main()
