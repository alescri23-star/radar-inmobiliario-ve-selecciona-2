"""Plantilla de fuente. Pendiente: elegir la primera fuente para Barquisimeto.

Antes de activarla:
  1. Revisar robots.txt y términos de uso, y anotarlo en `fuentes.notas_legales`.
  2. Confirmar que los anuncios son públicos (sin login).
  3. Aprobación de Alessandro.
"""
from bs4 import BeautifulSoup

from .base import AnuncioLeido, Fuente


class FuentePlantilla(Fuente):
    nombre = "plantilla"
    url_base = "https://ejemplo.invalid"

    def urls_listado(self, zona: str) -> list[str]:
        return [f"{self.url_base}/inmuebles/{zona.lower()}?pagina=1"]

    def parsear_listado(self, html: str) -> list[AnuncioLeido]:
        soup = BeautifulSoup(html, "html.parser")
        anuncios = []
        for tarjeta in soup.select("[data-anuncio-id]"):  # ajustar selectores a la fuente real
            titulo = tarjeta.select_one(".titulo")
            precio = tarjeta.select_one(".precio")
            anuncios.append(AnuncioLeido(
                id_externo=tarjeta["data-anuncio-id"],
                url=tarjeta.select_one("a")["href"],
                titulo=titulo.get_text(strip=True) if titulo else None,
                precio=_numero(precio.get_text()) if precio else None,
                moneda="USD" if precio and "$" in precio.get_text() else None,
            ))
        return anuncios


def _numero(texto: str) -> float | None:
    limpio = "".join(c for c in texto if c.isdigit())
    return float(limpio) if limpio else None
