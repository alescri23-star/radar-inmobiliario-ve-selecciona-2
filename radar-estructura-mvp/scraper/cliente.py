"""Cliente HTTP respetuoso para leer anuncios públicos.

Reglas que aplica siempre:
  * Respeta robots.txt; si no permite la ruta, no la visita.
  * Pausa entre peticiones (RADAR_PAUSA_SEG, mínimo 3 s).
  * Límite de páginas por ejecución (RADAR_MAX_PAGINAS).
  * Si detecta CAPTCHA, login o bloqueo, se detiene. Nunca intenta evitarlos.
"""
import os
import time
import urllib.robotparser
from urllib.parse import urlparse

import requests

USER_AGENT = "RadarVenezuelaBot/0.1 (investigacion de mercado; contacto: ver README)"
SENALES_BLOQUEO = ("captcha", "recaptcha", "hcaptcha", "cf-challenge", "iniciar sesion", "inicia sesión", "log in")


class BloqueoDetectado(Exception):
    """La fuente pide CAPTCHA/login o nos bloquea: se detiene la ejecución."""


class LimiteAlcanzado(Exception):
    """Se alcanzó el máximo de páginas permitido en esta ejecución."""


class ClienteRespetuoso:
    def __init__(self, pausa_seg: float | None = None, max_paginas: int | None = None):
        self.pausa = max(3.0, float(pausa_seg or os.getenv("RADAR_PAUSA_SEG", 5)))
        self.max_paginas = int(max_paginas or os.getenv("RADAR_MAX_PAGINAS", 20))
        self.paginas = 0
        self._robots: dict[str, urllib.robotparser.RobotFileParser] = {}
        self._ultima = 0.0
        self.sesion = requests.Session()
        self.sesion.headers["User-Agent"] = USER_AGENT

    def _permitido(self, url: str) -> bool:
        base = "{0.scheme}://{0.netloc}".format(urlparse(url))
        if base not in self._robots:
            rp = urllib.robotparser.RobotFileParser(base + "/robots.txt")
            rp.read()
            self._robots[base] = rp
        return self._robots[base].can_fetch(USER_AGENT, url)

    def obtener(self, url: str) -> str:
        if self.paginas >= self.max_paginas:
            raise LimiteAlcanzado(f"Máximo de {self.max_paginas} páginas alcanzado")
        if not self._permitido(url):
            raise PermissionError(f"robots.txt no permite: {url}")
        espera = self.pausa - (time.monotonic() - self._ultima)
        if espera > 0:
            time.sleep(espera)
        resp = self.sesion.get(url, timeout=30)
        self._ultima = time.monotonic()
        self.paginas += 1
        if resp.status_code in (401, 403, 429):
            raise BloqueoDetectado(f"HTTP {resp.status_code} en {url}")
        resp.raise_for_status()
        html_min = resp.text[:20000].lower()
        if any(s in html_min for s in SENALES_BLOQUEO):
            raise BloqueoDetectado(f"Posible CAPTCHA/login en {url}")
        return resp.text
