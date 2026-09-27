# Hoja de ruta

## Fase 0 — Base (esta estructura)
- [x] Esquema PostgreSQL + PostGIS con histórico inmutable
- [x] Zonas: Barquisimeto (piloto activo); Margarita, Los Roques, Morrocoy, Tucacas y Chichiriviche (registradas, inactivas)
- [x] Cliente HTTP respetuoso y plantilla de fuente
- [x] Detector de señales de reforma (v1, palabras clave)

## Fase 1 — Piloto Barquisimeto
- [ ] Elegir la primera fuente y revisar robots.txt y términos de uso
- [ ] Implementar su parser a partir de `scraper/fuentes/plantilla.py`
- [ ] Probar en modo simulación y activar la fuente con aprobación
- [ ] Ejecución periódica (p. ej. diaria) para empezar a acumular histórico

## Fase 2 — Análisis
- [ ] Mapa de anuncios con potencial de reforma
- [ ] Precio por m² por sector y evolución en el tiempo
- [ ] Señales de demanda desde el exterior (compradores venezolanos fuera del país)

## Fase 3 — Expansión (requiere aprobación)
- [ ] Isla de Margarita y los cayos (Los Roques, Morrocoy, Tucacas, Chichiriviche)
- [ ] Segunda fuente de datos
- [ ] Captación de leads en un sistema separado (Airtable o CRM)
