"""
Interfaz CLI (Command Line Interface)
Interfaz por consola para el chatbot
"""

import sys
from typing import Optional
from src.core.interfaces import IChatService
from src.core.config import Config


class CLIInterface:
    """
    Interfaz de línea de comandos para el chatbot
    """
    
    def __init__(self, chat_service: IChatService):
        """
        Inicializa la interfaz CLI
        
        Args:
            chat_service: Servicio de chat
        """
        self.chat_service = chat_service
        self.current_user_id: Optional[int] = None
    
    def run(self):
        """Ejecuta el loop principal de la CLI"""
        self._show_welcome()
        
        while True:
            try:
                user_input = input("\n💬 Tú: ").strip()
                
                if not user_input:
                    continue
                
                # Comandos especiales
                if user_input.lower() in ['/salir', '/exit', '/quit']:
                    self._show_goodbye()
                    break
                elif user_input.lower() == '/ayuda':
                    self._show_help()
                    continue
                elif user_input.lower() == '/limpiar':
                    self.chat_service.clear_history()
                    print("✅ Historial limpiado")
                    continue
                elif user_input.lower() == '/stats':
                    self._show_stats()
                    continue
                elif user_input.lower().startswith('/usuario '):
                    self._set_user(user_input)
                    continue
                
                # Procesar mensaje normal
                response = self.chat_service.process_message(
                    user_input=user_input,
                    user_id=self.current_user_id
                )
                
                print(f"\n🤖 Asistente: {response.message}")
                print(f"   [Intención: {response.intent} | Confianza: {response.confidence:.2f}]")
            
            except KeyboardInterrupt:
                print("\n\n👋 Interrupción detectada. Saliendo...")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Intenta de nuevo o escribe '/ayuda' para ver comandos disponibles")
    
    def _show_welcome(self):
        """Muestra mensaje de bienvenida"""
        print("=" * 70)
        print("🤖  CHATBOT DE ATENCIÓN AL CLIENTE  🤖".center(70))
        print("=" * 70)
        print("\n¡Bienvenido! Estoy aquí para ayudarte.\n")
        print("Puedo asistirte con:")
        print("  🔧 Soporte técnico y resolución de problemas")
        print("  🛍️  Recomendaciones de productos")
        print("  📝 Quejas y feedback")
        print("  ❓ Preguntas frecuentes")
        print("\nComandos disponibles:")
        print("  /ayuda    - Muestra esta ayuda")
        print("  /limpiar  - Limpia el historial de conversación")
        print("  /stats    - Muestra estadísticas de la sesión")
        print("  /usuario <id> - Simula ser un usuario específico (ej: /usuario 1)")
        print("  /salir    - Termina la conversación")
        print("\n" + "=" * 70)
    
    def _show_goodbye(self):
        """Muestra mensaje de despedida"""
        print("\n" + "=" * 70)
        print("👋 ¡Gracias por usar nuestro servicio!")
        print("   Esperamos haber sido de ayuda. ¡Hasta pronto!")
        print("=" * 70 + "\n")
    
    def _show_help(self):
        """Muestra ayuda"""
        print("\n📚 AYUDA - COMANDOS DISPONIBLES")
        print("-" * 50)
        print("/ayuda       - Muestra esta ayuda")
        print("/limpiar     - Limpia el historial de conversación")
        print("/stats       - Muestra estadísticas de la sesión")
        print("/usuario <id> - Simula ser un usuario (1-4)")
        print("/salir       - Termina la conversación")
        print("-" * 50)
        print("\nEjemplos de consultas:")
        print("  • 'No puedo iniciar sesión en mi cuenta'")
        print("  • 'Busco una laptop para diseño gráfico'")
        print("  • 'El producto llegó dañado, estoy muy molesto'")
        print("  • '¿Cuánto tarda el envío?'")
    
    def _show_stats(self):
        """Muestra estadísticas de la sesión"""
        stats = self.chat_service.get_stats()
        print("\n📊 ESTADÍSTICAS DE LA SESIÓN")
        print("-" * 50)
        print(f"Total de mensajes: {stats['total_messages']}")
        print(f"Tus mensajes: {stats['user_messages']}")
        print(f"Respuestas del bot: {stats['bot_messages']}")
        print(f"Intenciones disponibles: {', '.join(stats['available_intents'])}")
        print(f"Tiempo promedio de respuesta: {stats['avg_response_time_ms']:.2f} ms")
        print(f"P95 de respuesta: {stats['p95_response_time_ms']:.2f} ms")
        print(
            f"Fallback a general: {stats['fallback_to_general_count']} "
            f"({stats['fallback_rate_pct']:.2f}%)"
        )
        if stats['intent_accuracy_pct'] is None:
            print("Accuracy de intención: N/A (sin etiquetas esperadas)")
        else:
            print(
                f"Accuracy de intención: {stats['intent_accuracy_pct']:.2f}% "
                f"sobre {stats['intent_evaluated_samples']} muestras"
            )
        if self.current_user_id:
            print(f"Usuario actual: ID {self.current_user_id}")
        print("-" * 50)
    
    def _set_user(self, command: str):
        """Establece el usuario actual"""
        try:
            user_id_str = command.split()[1]
            user_id = int(user_id_str)
            if 1 <= user_id <= 4:  # Tenemos 4 usuarios en la BD simulada
                self.current_user_id = user_id
                print(f"✅ Ahora simulando como usuario ID {user_id}")
            else:
                print("❌ ID de usuario inválido. Usa un número del 1 al 4.")
        except (IndexError, ValueError):
            print("❌ Formato incorrecto. Usa: /usuario <id>")


def main():
    """Función principal para ejecutar la CLI"""
    from src.clients.openai_client import OpenAIClient, MockLLMClient
    from src.infrastructure.database_sim import DatabaseSimulator
    from src.factories.strategy_factory import StrategyFactory
    from src.application.chat_service import ChatService
    
    print("🚀 Iniciando chatbot...")
    
    # Validar configuración
    has_api_key = Config.validate()
    
    # Inicializar componentes (Dependency Injection manual)
    try:
        if has_api_key:
            llm_client = OpenAIClient()
        else:
            print("⚠️  Usando modo simulación (sin OpenAI)")
            llm_client = MockLLMClient()
        
        database = DatabaseSimulator()
        strategy_factory = StrategyFactory(llm_client, database)
        chat_service = ChatService(strategy_factory)
        
        # Iniciar CLI
        cli = CLIInterface(chat_service)
        cli.run()
    
    except Exception as e:
        print(f"❌ Error al inicializar el chatbot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
