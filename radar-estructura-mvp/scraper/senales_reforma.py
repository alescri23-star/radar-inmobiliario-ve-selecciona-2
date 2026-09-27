"""Detección de señales de potencial de reforma en el texto de un anuncio.

El resultado es siempre una ESTIMACIÓN: indica que el anuncio merece revisión,
no que el inmueble necesite reforma con certeza.
"""
import re
import unicodedata

METODO = "palabras_clave_v1"

# Señal -> peso. Pesos altos = mención explícita de reforma o mal estado.
SENALES = {
    "para remodelar": 30,
    "para reformar": 30,
    "a remodelar": 30,
    "a reformar": 30,
    "requiere remodelacion": 30,
    "necesita remodelacion": 30,
    "necesita reparaciones": 25,
    "requiere reparaciones": 25,
    "para restaurar": 25,
    "para actualizar": 20,
    "necesita mantenimiento": 20,
    "para estrenar a su gusto": 20,
    "ideal para inversionistas": 10,
    "oportunidad de inversion": 10,
    "precio negociable": 5,
    "cocina original": 15,
    "banos originales": 15,
    "pisos originales": 10,
    "ceramica original": 10,
    "construccion antigua": 10,
    "casa vieja": 15,
    "venta urgente": 5,
}


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", texto)


def evaluar(titulo: str | None, descripcion: str | None) -> dict:
    """Devuelve puntuación 0-100 y señales detectadas, etiquetado como ESTIMACIÓN."""
    texto = _normalizar(f"{titulo or ''} {descripcion or ''}")
    if not texto.strip():
        return {"valor": None, "senales": [], "metodo": METODO, "etiqueta": "ESTIMACIÓN",
                "nota": "DATO NO DISPONIBLE: anuncio sin texto"}
    detectadas = [s for s in SENALES if re.search(rf"\b{re.escape(s)}\b", texto)]
    valor = min(100, sum(SENALES[s] for s in detectadas))
    return {"valor": valor, "senales": detectadas, "metodo": METODO, "etiqueta": "ESTIMACIÓN"}
