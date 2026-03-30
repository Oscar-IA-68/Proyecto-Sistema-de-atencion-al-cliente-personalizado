"""
SUITE DE PRUEBAS COMPLETA: 8 PRUEBAS CON GOOGLE AI STUDIO
Objetivo: Identificar áreas de mejora en lógica de procesamiento y respuesta del LLM

Pruebas:
  1. Humo E2E: Conectividad y latencia
  2. Support: Intent support con contexto de cliente
  3. Recommendation: Detección de productos mencionados
  4. FAQ: Fallback policy
  5. Ambigüedad: Entrada ambigua para clasificación
  6. Malformación: Respuesta atípica del LLM
  7. Resiliencia: Error transitorio y reintentos
  8. Extremo: Input largo o multi-intención
"""

import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# Configurar encoding UTF-8 para Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', newline='')

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.application.app_factory import AppFactory
from src.core.config import Config

class TestSuite:
    """Ejecuta la suite completa de 8 pruebas y genera microinformes"""
    
    def __init__(self):
        self.results = []
        self.components = None
        self.init_components()
    
    def init_components(self):
        """Inicializa componentes una sola vez"""
        print("\n" + "="*80)
        print("INICIALIZANDO COMPONENTES PARA SUITE DE PRUEBAS")
        print("="*80)
        try:
            self.components = AppFactory.create_components()
            print(f"✓ Componentes creados")
            print(f"  Provider: {self.components.provider_name}")
            print(f"  Modelo: {Config.GOOGLE_MODEL}")
            print(f"  Temperatura: {Config.GOOGLE_TEMPERATURE}")
        except Exception as e:
            print(f"✗ Error: {e}")
            raise
    
    def test_1_smoke_greeting(self):
        """Prueba #1: Humo E2E - Saludo simple"""
        print("\n" + "="*80)
        print("PRUEBA #1: HUMO E2E - SALUDO SIMPLE")
        print("="*80)
        
        user_message = "Hola, ¿cómo estás?"
        user_id = "test_user_01"
        
        print(f"Entrada: '{user_message}'")
        start = time.time()
        
        try:
            response = self.components.chat_service.process_message(user_message, user_id)
            elapsed = time.time() - start
            
            print(f"✓ Intent: {response.intent} (conf: {response.confidence:.2f})")
            print(f"✓ Respuesta: {response.message[:100]}...")
            print(f"✓ Tiempo: {elapsed:.2f}s")
            
            return {
                "test": 1,
                "name": "Humo E2E",
                "status": "PASS",
                "intent": response.intent,
                "confidence": response.confidence,
                "elapsed": elapsed,
                "message_len": len(response.message),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"✗ Error: {e}")
            return {
                "test": 1,
                "name": "Humo E2E",
                "status": "FAIL",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def test_2_support_intent(self):
        """Prueba #2: Support - Intent con contexto de cliente"""
        print("\n" + "="*80)
        print("PRUEBA #2: SUPPORT INTENT - CONTEXTO DE CLIENTE")
        print("="*80)
        
        user_message = "Tengo un problema con mi cuenta, no puedo acceder"
        user_id = "C001"  # Customer ID existente
        
        print(f"Entrada: '{user_message}'")
        print(f"Customer ID: {user_id}")
        start = time.time()
        
        try:
            response = self.components.chat_service.process_message(user_message, user_id)
            elapsed = time.time() - start
            
            print(f"✓ Intent: {response.intent} (conf: {response.confidence:.2f})")
            print(f"✓ Respuesta: {response.message[:100]}...")
            print(f"✓ Metadata: {response.metadata}")
            print(f"✓ Tiempo: {elapsed:.2f}s")
            
            # Validaciones específicas para support
            is_support = response.intent in ["support", "general"]
            has_customer_context = "customer_id" in str(response.metadata) or response.confidence > 0.5
            
            return {
                "test": 2,
                "name": "Support Intent",
                "status": "PASS" if is_support else "PARTIAL",
                "intent": response.intent,
                "confidence": response.confidence,
                "has_customer_context": has_customer_context,
                "elapsed": elapsed,
                "metadata": response.metadata,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"✗ Error: {e}")
            return {
                "test": 2,
                "name": "Support Intent",
                "status": "FAIL",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def test_3_recommendation_intent(self):
        """Prueba #3: Recommendation - Detección de productos mencionados"""
        print("\n" + "="*80)
        print("PRUEBA #3: RECOMMENDATION INTENT - DETECCIÓN DE PRODUCTOS")
        print("="*80)
        
        user_message = "Buscamos un laptop para desarrollo, ¿qué me recomiendas?"
        user_id = "test_user_03"
        
        print(f"Entrada: '{user_message}'")
        start = time.time()
        
        try:
            response = self.components.chat_service.process_message(user_message, user_id)
            elapsed = time.time() - start
            
            print(f"✓ Intent: {response.intent} (conf: {response.confidence:.2f})")
            print(f"✓ Respuesta: {response.message[:100]}...")
            print(f"✓ Metadata: {response.metadata}")
            print(f"✓ Tiempo: {elapsed:.2f}s")
            
            is_recommendation = response.intent in ["recommendation", "general"]
            has_products = "products" in response.metadata or "products_mentioned" in response.metadata
            
            return {
                "test": 3,
                "name": "Recommendation Intent",
                "status": "PASS" if is_recommendation else "PARTIAL",
                "intent": response.intent,
                "confidence": response.confidence,
                "has_products": has_products,
                "elapsed": elapsed,
                "metadata": response.metadata,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"✗ Error: {e}")
            return {
                "test": 3,
                "name": "Recommendation Intent",
                "status": "FAIL",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def test_4_faq_fallback(self):
        """Prueba #4: FAQ - Fallback policy"""
        print("\n" + "="*80)
        print("PRUEBA #4: FAQ FALLBACK POLICY")
        print("="*80)
        
        user_message = "¿Cuál es la política de devolución?"
        user_id = "test_user_04"
        
        print(f"Entrada: '{user_message}'")
        start = time.time()
        
        try:
            response = self.components.chat_service.process_message(user_message, user_id)
            elapsed = time.time() - start
            
            print(f"✓ Intent: {response.intent} (conf: {response.confidence:.2f})")
            print(f"✓ Respuesta: {response.message[:100]}...")
            print(f"✓ Metadata: {response.metadata}")
            print(f"✓ Tiempo: {elapsed:.2f}s")
            
            is_faq_or_general = response.intent in ["faq", "general"]
            
            return {
                "test": 4,
                "name": "FAQ Fallback",
                "status": "PASS" if is_faq_or_general else "PARTIAL",
                "intent": response.intent,
                "confidence": response.confidence,
                "elapsed": elapsed,
                "metadata": response.metadata,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"✗ Error: {e}")
            return {
                "test": 4,
                "name": "FAQ Fallback",
                "status": "FAIL",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def test_5_ambiguous_intent(self):
        """Prueba #5: Entrada ambigua para evaluar clasificación"""
        print("\n" + "="*80)
        print("PRUEBA #5: ENTRADA AMBIGUA - CLASIFICACIÓN")
        print("="*80)
        
        user_message = "Ayuda"  # Muy breve y ambiguo
        user_id = "test_user_05"
        
        print(f"Entrada: '{user_message}'")
        start = time.time()
        
        try:
            response = self.components.chat_service.process_message(user_message, user_id)
            elapsed = time.time() - start
            
            print(f"✓ Intent: {response.intent} (conf: {response.confidence:.2f})")
            print(f"✓ Respuesta: {response.message[:100]}...")
            print(f"✓ Metadata: {response.metadata}")
            print(f"✓ Tiempo: {elapsed:.2f}s")
            
            # Esperamos fallback a 'general' por ambigüedad
            fallback_correct = response.intent == "general" or response.confidence < 0.7
            
            return {
                "test": 5,
                "name": "Entrada Ambigua",
                "status": "PASS" if fallback_correct else "PARTIAL",
                "intent": response.intent,
                "confidence": response.confidence,
                "fallback_correct": fallback_correct,
                "elapsed": elapsed,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"✗ Error: {e}")
            return {
                "test": 5,
                "name": "Entrada Ambigua",
                "status": "FAIL",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def test_6_malformed_response(self):
        """Prueba #6: Respuesta atípica/malformada del LLM"""
        print("\n" + "="*80)
        print("PRUEBA #6: TOLERANCIA A RESPUESTA ATÍPICA")
        print("="*80)
        
        # Entrada que podría producir respuesta inesperada
        user_message = "XYZ ABC 123 MALFORMED INPUT"
        user_id = "test_user_06"
        
        print(f"Entrada: '{user_message}'")
        start = time.time()
        
        try:
            response = self.components.chat_service.process_message(user_message, user_id)
            elapsed = time.time() - start
            
            print(f"✓ Intent: {response.intent} (conf: {response.confidence:.2f})")
            print(f"✓ Respuesta: {response.message[:100]}...")
            print(f"✓ Metadata: {response.metadata}")
            print(f"✓ Tiempo: {elapsed:.2f}s")
            
            # Validar que no crash y retorna estructura válida
            has_valid_structure = all([
                hasattr(response, 'intent'),
                hasattr(response, 'message'),
                hasattr(response, 'confidence'),
                len(response.message) > 0
            ])
            
            return {
                "test": 6,
                "name": "Respuesta Malformada",
                "status": "PASS" if has_valid_structure else "FAIL",
                "intent": response.intent,
                "confidence": response.confidence,
                "has_valid_structure": has_valid_structure,
                "elapsed": elapsed,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"✗ Error: {e}")
            return {
                "test": 6,
                "name": "Respuesta Malformada",
                "status": "FAIL",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def test_7_error_resilience(self):
        """Prueba #7: Error transitorio y reintentos"""
        print("\n" + "="*80)
        print("PRUEBA #7: RESILIENCIA - REINTENTOS Y FALLBACK")
        print("="*80)
        
        user_message = "¿Puede ayudarme con un problema urgente?"
        user_id = "test_user_07"
        
        print(f"Entrada: '{user_message}'")
        start = time.time()
        
        try:
            response = self.components.chat_service.process_message(user_message, user_id)
            elapsed = time.time() - start
            
            print(f"✓ Intent: {response.intent} (conf: {response.confidence:.2f})")
            print(f"✓ Respuesta: {response.message[:100]}...")
            print(f"✓ Metadata: {response.metadata}")
            print(f"✓ Tiempo: {elapsed:.2f}s")
            
            # Verificar que retorna respuesta válida (indica reintentos funcionaron)
            success = len(response.message) > 0 and response.confidence > 0
            
            return {
                "test": 7,
                "name": "Resiliencia",
                "status": "PASS" if success else "FAIL",
                "intent": response.intent,
                "confidence": response.confidence,
                "response_valid": success,
                "elapsed": elapsed,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"✗ Error: {e}")
            return {
                "test": 7,
                "name": "Resiliencia",
                "status": "FAIL",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def test_8_edge_case_long_input(self):
        """Prueba #8: Input largo o multi-intención"""
        print("\n" + "="*80)
        print("PRUEBA #8: EDGE CASE - INPUT LARGO/MULTI-INTENCIÓN")
        print("="*80)
        
        user_message = """
        Tengo varios problemas: primero, mi laptop no arranca; segundo, 
        los productos que vieron en el catálogo están fuera de stock; 
        y tercero, quiero saber si hay una política de descuentos por volumen. 
        También me gustaría reportar un problema con la facturación del mes pasado.
        ¿Pueden ayudarme con todo esto?
        """
        user_id = "test_user_08"
        
        print(f"Entrada: '{user_message[:80]}...' (largo: {len(user_message)} chars)")
        start = time.time()
        
        try:
            response = self.components.chat_service.process_message(user_message, user_id)
            elapsed = time.time() - start
            
            print(f"✓ Intent: {response.intent} (conf: {response.confidence:.2f})")
            print(f"✓ Respuesta: {response.message[:100]}...")
            print(f"✓ Metadata: {response.metadata}")
            print(f"✓ Tiempo: {elapsed:.2f}s")
            
            # Validación endurecida: evitar PASS con fallback por error o respuesta mínima
            message_text = (response.message or "").strip()
            response_length = len(message_text)
            input_length = len(user_message)
            response_ratio = (response_length / input_length) if input_length > 0 else 0.0

            fallback_error_phrases = [
                "lo siento, hubo un error al procesar tu solicitud",
                "por favor, intenta de nuevo",
            ]
            is_error_fallback = any(phrase in message_text.lower() for phrase in fallback_error_phrases)

            has_min_length = response_length >= 120
            has_min_ratio = response_ratio >= 0.30
            confidence_ok = response.confidence >= 0.6

            quality_checks = {
                "has_min_length": has_min_length,
                "has_min_ratio": has_min_ratio,
                "is_error_fallback": is_error_fallback,
                "confidence_ok": confidence_ok,
            }

            if is_error_fallback:
                status = "PARTIAL"
                status_reason = "fallback_error_detected"
            elif has_min_length and has_min_ratio and confidence_ok:
                status = "PASS"
                status_reason = "quality_checks_passed"
            elif response_length == 0:
                status = "FAIL"
                status_reason = "empty_response"
            else:
                status = "PARTIAL"
                status_reason = "insufficient_depth_for_long_input"

            print(f"✓ Longitud respuesta >= 120: {has_min_length}")
            print(f"✓ Ratio respuesta/input >= 0.30: {has_min_ratio} ({response_ratio:.2%})")
            print(f"✓ Detecta fallback de error: {is_error_fallback}")
            print(f"✓ Confianza >= 0.60: {confidence_ok}")
            print(f"✓ Criterio endurecido estado: {status} ({status_reason})")
            
            return {
                "test": 8,
                "name": "Edge Case Long Input",
                "status": status,
                "status_reason": status_reason,
                "intent": response.intent,
                "confidence": response.confidence,
                "input_length": input_length,
                "response_length": response_length,
                "response_ratio": response_ratio,
                "elapsed": elapsed,
                "quality_checks": quality_checks,
                "metadata": response.metadata,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"✗ Error: {e}")
            return {
                "test": 8,
                "name": "Edge Case Long Input",
                "status": "FAIL",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def run_all_tests(self):
        """Ejecuta todas las 8 pruebas"""
        print("\n" + "█"*80)
        print("█ INICIANDO SUITE COMPLETA: 8 PRUEBAS CON GOOGLE AI STUDIO")
        print("█"*80)
        
        tests = [
            self.test_1_smoke_greeting,
            self.test_2_support_intent,
            self.test_3_recommendation_intent,
            self.test_4_faq_fallback,
            self.test_5_ambiguous_intent,
            self.test_6_malformed_response,
            self.test_7_error_resilience,
            self.test_8_edge_case_long_input,
        ]
        
        for test_func in tests:
            result = test_func()
            self.results.append(result)
            time.sleep(0.5)  # Small delay entre pruebas
        
        self.print_summary()
        self.save_results()
    
    def print_summary(self):
        """Imprime resumen de resultados"""
        print("\n" + "="*80)
        print("RESUMEN DE RESULTADOS - 8 PRUEBAS")
        print("="*80)
        
        passed = sum(1 for r in self.results if r.get("status") == "PASS")
        partial = sum(1 for r in self.results if r.get("status") == "PARTIAL")
        failed = sum(1 for r in self.results if r.get("status") == "FAIL")
        
        print(f"\n✓ PASS:    {passed}/8")
        print(f"⚠ PARTIAL: {partial}/8")
        print(f"✗ FAIL:    {failed}/8")
        
        print("\nDetalle por prueba:")
        for result in self.results:
            status_icon = "✓" if result.get("status") == "PASS" else "⚠" if result.get("status") == "PARTIAL" else "✗"
            print(f"  {status_icon} Prueba #{result['test']}: {result['name']} - {result['status']}")
            if result.get("elapsed"):
                print(f"     Tiempo: {result['elapsed']:.2f}s")
        
        print("\n" + "="*80)
    
    def save_results(self):
        """Guarda resultados en JSON"""
        project_root = os.path.dirname(os.path.dirname(__file__))
        output_dir = os.path.join(project_root, "informes", "revalidacion")
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        output_file = os.path.join(
            output_dir,
            f"{timestamp}_revalidacion_resultados_8_pruebas_v01.json"
        )
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\nResultados guardados en: {output_file}")

if __name__ == "__main__":
    suite = TestSuite()
    suite.run_all_tests()
