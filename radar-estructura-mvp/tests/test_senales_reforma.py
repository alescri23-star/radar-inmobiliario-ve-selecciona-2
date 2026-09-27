from scraper import senales_reforma


def test_detecta_senales_con_acentos():
    r = senales_reforma.evaluar("Casa para remodelar en Cabudare", "Cocina original, baños originales")
    assert r["etiqueta"] == "ESTIMACIÓN"
    assert "para remodelar" in r["senales"]
    assert "cocina original" in r["senales"]
    assert "banos originales" in r["senales"]
    assert r["valor"] == 60


def test_sin_senales():
    r = senales_reforma.evaluar("Apartamento a estrenar", "Acabados de lujo")
    assert r["valor"] == 0
    assert r["senales"] == []


def test_sin_texto_es_dato_no_disponible():
    r = senales_reforma.evaluar(None, None)
    assert r["valor"] is None
    assert "DATO NO DISPONIBLE" in r["nota"]


def test_tope_100():
    texto = " ".join(senales_reforma.SENALES)
    assert senales_reforma.evaluar(texto, "")["valor"] == 100
