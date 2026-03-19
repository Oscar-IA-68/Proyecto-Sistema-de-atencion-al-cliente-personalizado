"""
Configuración centralizada del sistema
"""

import os
from typing import Dict, Any


class Config:
    """Configuración central de la aplicación"""
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Modelo OpenAI
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 500
    
    # Rutas de datos
    DATA_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    CUSTOMERS_FILE: str = os.path.join(DATA_DIR, "customers.json")
    PRODUCTS_FILE: str = os.path.join(DATA_DIR, "products.json")
    TICKETS_FILE: str = os.path.join(DATA_DIR, "tickets.json")
    FAQ_FILE: str = os.path.join(DATA_DIR, "faq.json")
    
    # Intenciones del sistema
    INTENTS: Dict[str, str] = {
        "support": "Consulta de soporte técnico",
        "recommendation": "Recomendación de productos",
        "complaint": "Queja o feedback",
        "faq": "Pregunta frecuente",
        "general": "Conversación general"
    }
    
    # Prompts del sistema
    SYSTEM_PROMPTS: Dict[str, str] = {
        "intent_detection": """Eres un clasificador de intenciones. Clasifica el mensaje del usuario en una de estas categorías:
- support: Problemas técnicos, errores, no puede hacer algo
- recommendation: Busca un producto, pide sugerencias, quiere comprar algo
- complaint: Se queja, está molesto, da feedback negativo
- faq: Pregunta sobre políticas, procesos, información general
- general: Conversación casual, saludos, agradecimientos

Responde SOLO con el nombre de la categoría, sin explicaciones.""",
        
        "support": """Eres un agente de soporte técnico experto y empático. 
Tu objetivo es ayudar a resolver problemas técnicos de forma clara y paso a paso.
Sé conciso pero completo. Si necesitas información adicional, pregúntala.""",
        
        "recommendation": """Eres un experto en recomendaciones de productos.
Haz preguntas inteligentes para entender las necesidades del cliente.
Recomienda productos específicos basándote en: presupuesto, uso previsto, y preferencias.
Sé honesto sobre las limitaciones de los productos.""",
        
        "complaint": """Eres un especialista en atención al cliente enfocado en resolver quejas.
Sé empático, reconoce el problema, y ofrece soluciones concretas.
Mantén un tono profesional y comprensivo. Registra los detalles de la queja.""",
        
        "faq": """Eres un asistente virtual eficiente.
Responde preguntas frecuentes de forma clara y directa usando la información proporcionada.
Si no tienes la información exacta, indica cómo el usuario puede obtenerla.""",
        
        "general": """Eres un asistente virtual amigable y profesional.
Mantén conversaciones naturales, ayuda con dudas generales, y dirige a los usuarios al tipo correcto de soporte."""
    }
    
    # Umbrales de confianza
    INTENT_CONFIDENCE_THRESHOLD: float = 0.6
    FAQ_SIMILARITY_THRESHOLD: float = 0.7
    
    # Configuración de conversación
    MAX_HISTORY_LENGTH: int = 10
    
    @classmethod
    def validate(cls) -> bool:
        """Valida que la configuración esté completa"""
        if not cls.OPENAI_API_KEY:
            print("⚠️  ADVERTENCIA: OPENAI_API_KEY no está configurada")
            print("   Para usar el chatbot con OpenAI, configura tu API key:")
            print("   export OPENAI_API_KEY='tu-api-key'  (Linux/Mac)")
            print("   $env:OPENAI_API_KEY='tu-api-key'  (Windows PowerShell)")
            return False
        return True
    
    @classmethod
    def get_system_prompt(cls, intent: str) -> str:
        """Obtiene el prompt del sistema para una intención específica"""
        return cls.SYSTEM_PROMPTS.get(intent, cls.SYSTEM_PROMPTS["general"])
