# Principios de datos

1. **El histórico nunca se sobrescribe.** Cada lectura con cambios crea una fila nueva en `observaciones`. La base de datos bloquea `UPDATE` y `DELETE` en esa tabla.
2. **Nunca se infiere "vendido".** Si un anuncio deja de aparecer, pasa a `no_visto`. Desaparecer no significa venderse: puede estar pausado, caducado o publicado en otro sitio.
3. **Dato ausente = `DATO NO DISPONIBLE`.** En la base se guarda `NULL`; las vistas lo muestran explícitamente. Nunca se rellena con supuestos.
4. **Estimaciones etiquetadas.** Todo cálculo propio (p. ej. potencial de reforma) va en `estimaciones` con etiqueta `ESTIMACIÓN` o `HIPÓTESIS` y el método usado.
5. **Lectura respetuosa.** Se respeta robots.txt y se hace una pausa mínima de 3 s entre peticiones. Si aparece un CAPTCHA, un login o un bloqueo, el proceso se detiene: nunca se intenta evitarlos.
6. **Datos personales mínimos.** No se guardan nombres, teléfonos ni correos de particulares.
7. **Requiere aprobación de Alessandro:** activar una fuente o una zona fuera de Lara, hacer scraping masivo, contratar servicios de pago o lanzar al público.
