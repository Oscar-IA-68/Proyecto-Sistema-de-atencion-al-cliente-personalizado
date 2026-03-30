# Revalidacion integral suite8 con .venv

## 1. Contexto
Se ejecuta la suite funcional completa de 8 pruebas tras confirmar disponibilidad de cuota y migracion operativa al entorno `.venv`.

## 2. Problema
Cerrar la sesion pendiente con evidencia integral de estado post-fixes (P1/P2) y verificar estabilidad general.

## 3. Causa raiz (si aplica)
No aplica causa nueva de producto; durante la corrida se observaron eventos de limite por minuto (`429`) que fueron absorbidos por retries/fallback del sistema.

## 4. Cambios aplicados
No hubo cambios de codigo en esta ejecucion.
Se aplico ejecucion controlada con interprete explicito de `.venv`.

## 5. Validacion
Comando ejecutado:

`c:/Users/yuvlo/OneDrive/Documentos/Codigo_carrera/Inteligencia_artificial/archivos_github/Proyecto-Sistema-de-atencion-al-cliente-personalizado/.venv/Scripts/python.exe scripts/run_8_tests.py`

Artefacto generado:
- `informes/revalidacion/2026-03-29_2011_revalidacion_resultados_8_pruebas_v01.json`

Resultado global:
- PASS: 8/8
- PARTIAL: 0/8
- FAIL: 0/8

Comparativa relevante vs corrida previa (`2026-03-28_revalidacion_resultados_8_pruebas_v01.json`):
1. Test #2 (Support intent)
   - Antes: intent `general`, metadata sin contexto de cliente.
   - Ahora: intent `support`, metadata enriquecida con `customer_id`, `customer_name`, `customer_membership`.
2. Test #3 (Recommendation)
   - Antes: `has_products=false`.
   - Ahora: `has_products=true` (con metadata de catalogo presente).
3. Test #4 (FAQ)
   - Antes: intent `general`.
   - Ahora: intent `faq`, `used_faq=true`.
4. Test #7 (Resiliencia)
   - Antes: intent `general`.
   - Ahora: intent `support`.
5. Test #8 (Input largo)
   - Se mantiene respuesta de 79 caracteres en JSON de suite8 (limitacion multi-intencion aun pendiente de P3).

## 6. Impacto
1. Se confirma mejora funcional sostenida en deteccion de intenciones y metadata de soporte.
2. Se valida recuperacion operacional tras sesion bloqueada por quota diaria.
3. Se mantiene abierto el gap de multi-intencion profunda (P3), aunque la suite marca PASS por criterio actual.

## 7. Riesgos
1. Riesgo de falsos positivos de calidad: la suite puede marcar PASS aunque haya degradacion por fallback (ej. respuestas genericas por `429` RPM).
2. Riesgo de limite por minuto: se observaron respuestas `429` durante la corrida completa.
3. Riesgo de criterio insuficiente en Test #8: el PASS no exige respuesta extendida/coherente para multi-intencion.

## 8. Proximos pasos
1. Ajustar criterios de aceptacion en `scripts/run_8_tests.py` para marcar PARTIAL cuando haya fallback por error LLM en pruebas de calidad.
2. Ejecutar una segunda corrida de suite8 con pausa entre pruebas para reducir `429` por minuto.
3. Priorizar implementacion P3 para resolver limitacion de multi-intencion en Test #8.
