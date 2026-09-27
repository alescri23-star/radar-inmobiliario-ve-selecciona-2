from scraper.fuentes.plantilla import FuentePlantilla

HTML = """
<div data-anuncio-id="A1"><a href="https://ejemplo.invalid/a1">x</a>
  <span class="titulo">Casa para remodelar</span><span class="precio">$ 35.000</span></div>
<div data-anuncio-id="A2"><a href="https://ejemplo.invalid/a2">x</a></div>
"""


def test_parsea_y_deja_ausentes_en_none():
    anuncios = FuentePlantilla().parsear_listado(HTML)
    assert [a.id_externo for a in anuncios] == ["A1", "A2"]
    assert anuncios[0].precio == 35000 and anuncios[0].moneda == "USD"
    assert anuncios[1].precio is None and anuncios[1].titulo is None
