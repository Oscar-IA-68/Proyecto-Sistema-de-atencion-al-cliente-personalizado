# Revalidacion puntual Test 8 con criterio endurecido

## 1. Contexto
Se ejecuta solo la prueba 8 porque era el ultimo pendiente tecnico.
La validacion usa el criterio endurecido en `scripts/run_8_tests.py`.

## 2. Problema
La prueba de input largo/multi-intencion podia marcar PASS con respuestas superficiales.

## 3. Causa raiz (si aplica)
No hay error de API en esta corrida; el problema fue calidad insuficiente de profundidad.

## 4. Cambios aplicados
1. Criterio endurecido para Test 8:
   - Longitud minima >= 120
   - Ratio respuesta/input >= 0.30
   - No permitir PASS si detecta fallback de error
   - Confianza minima >= 0.60

## 5. Validacion
Comando ejecutado:

`c:/Users/yuvlo/OneDrive/Documentos/Codigo_carrera/Inteligencia_artificial/archivos_github/Proyecto-Sistema-de-atencion-al-cliente-personalizado/.venv/Scripts/python.exe -c "import json; from scripts.run_8_tests import TestSuite; s=TestSuite(); r=s.test_8_edge_case_long_input(); print(json.dumps(r, ensure_ascii=False))"`

Resultado:
1. Estado: PARTIAL
2. Motivo: `insufficient_depth_for_long_input`
3. input_length: 357
4. response_length: 95
5. response_ratio: 0.2661
6. checks:
   - has_min_length: false
   - has_min_ratio: false
   - is_error_fallback: false
   - confidence_ok: true

## 6. Impacto
1. Se confirma que el nuevo criterio evita falsos PASS por respuestas cortas.
2. Queda formalmente cerrado el pendiente de ejecucion de Test 8.
3. Se mantiene brecha funcional de profundidad para multi-intencion (P3).

## 7. Riesgos
1. Sin P3, el sistema puede seguir dando respuestas correctas pero poco profundas en inputs complejos.
2. Variabilidad generativa puede cambiar la longitud en corridas futuras.

## 8. Proximos pasos
1. Implementar P3 multi-intencion para aumentar cobertura y profundidad.
2. Tras P3, re-ejecutar solo Test 8 y buscar PASS bajo criterio endurecido.
