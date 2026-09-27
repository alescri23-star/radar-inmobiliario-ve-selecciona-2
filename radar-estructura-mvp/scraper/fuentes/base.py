"""Interfaz que debe cumplir cada fuente de anuncios.

Para añadir una fuente: copiar `plantilla.py`, implementar los dos métodos y
registrarla en `fuentes/__init__.py`. La fuente queda inactiva hasta aprobarla.
"""
from dataclasses import dataclass, field


@dataclass
class AnuncioLeido:
    id_externo: str
    url: str
    titulo: str | None = None
    descripcion: str | None = None
    precio: float | None = None
    moneda: str | None = None            # 'USD', 'VES', 'EUR'
    tipo_inmueble: str | None = None
    operacion: str | None = None         # 'venta' | 'alquiler'
    m2_construccion: float | None = None
    m2_terreno: float | None = None
    habitaciones: int | None = None
    banos: int | None = None
    lat: float | None = None
    lon: float | None = None
    ubicacion_precision: str | None = None  # 'exacta' | 'aproximada' | 'zona'
    extra: dict = field(default_factory=dict)
    # Sin nombres, teléfonos ni correos de particulares: datos personales mínimos.


class Fuente:
    nombre: str = ""
    url_base: str = ""

    def urls_listado(self, zona: str) -> list[str]:
        """URLs de páginas de resultados para una zona."""
        raise NotImplementedError

    def parsear_listado(self, html: str) -> list[AnuncioLeido]:
        """Extrae los anuncios de una página de resultados."""
        raise NotImplementedError
