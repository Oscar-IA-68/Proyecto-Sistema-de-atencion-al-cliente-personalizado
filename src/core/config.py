"""
Configuracion centralizada del sistema
"""

import os
from typing import Any, Dict

from dotenv import load_dotenv


# Cargar variables de entorno desde .env sin sobreescribir variables ya exportadas
load_dotenv(override=False)


def _get_env_float(name: str, default: float) -> float:
    """Obtiene un float desde entorno con fallback seguro."""
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _get_env_int(name: str, default: int) -> int:
    """Obtiene un entero desde entorno con fallback seguro."""
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


class Config:
    """Configuracion central de la aplicacion"""

    # Seleccion de proveedor LLM
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai").strip().lower() or "openai"
    SUPPORTED_LLM_PROVIDERS = ("openai", "google_ai_studio", "mock")

    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "").strip()
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "").strip()

    # Modelo OpenAI
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo").strip() or "gpt-3.5-turbo"
    OPENAI_TEMPERATURE: float = _get_env_float("OPENAI_TEMPERATURE", 0.7)
    OPENAI_MAX_TOKENS: int = _get_env_int("OPENAI_MAX_TOKENS", 500)

    # Modelo Google AI Studio (Gemini)
    GOOGLE_MODEL: str = os.getenv("GOOGLE_MODEL", "gemini-2.5-flash").strip() or "gemini-2.5-flash"
    GOOGLE_TEMPERATURE: float = _get_env_float("GOOGLE_TEMPERATURE", 0.7)
    GOOGLE_MAX_TOKENS: int = _get_env_int("GOOGLE_MAX_TOKENS", 500)

    # Rutas de datos
    DATA_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    CUSTOMERS_FILE: str = os.path.join(DATA_DIR, "customers.json")
    PRODUCTS_FILE: str = os.path.join(DATA_DIR, "products.json")
    TICKETS_FILE: str = os.path.join(DATA_DIR, "tickets.json")
    FAQ_FILE: str = os.path.join(DATA_DIR, "faq.json")

    # Intenciones del sistema
    INTENTS: Dict[str, str] = {
        "support": "Consulta de soporte tecnico",
        "recommendation": "Recomendacion de productos",
        "complaint": "Queja o feedback",
        "faq": "Pregunta frecuente",
        "general": "Conversacion general",
    }

    # Prompts del sistema
    SYSTEM_PROMPTS: Dict[str, str] = {
        "intent_detection": """Eres un clasificador de intenciones. Clasifica el mensaje del usuario en una de estas categorias:
- support: Problemas tecnicos, errores, no puede hacer algo
- recommendation: Busca un producto, pide sugerencias, quiere comprar algo
- complaint: Se queja, esta molesto, da feedback negativo
- faq: Pregunta sobre politicas, procesos, informacion general
- general: Conversacion casual, saludos, agradecimientos

Responde SOLO con el nombre de la categoria, sin explicaciones.""",
        "support": """Eres un agente de soporte tecnico experto y empatico.
Tu objetivo es ayudar a resolver problemas tecnicos de forma clara y paso a paso.
Se conciso pero completo. Si necesitas informacion adicional, preguntala.""",
        "recommendation": """Eres un experto en recomendaciones de productos especializado en nuestro catálogo.
Haz preguntas inteligentes para entender las necesidades del cliente.
Recomienda productos ESPECÍFICOS basándote en: presupuesto, uso previsto, y preferencias.
IMPORTANTE: Cuando recomiendes un producto, DEBES mencionar su nombre EXACTO tal como aparece en el catálogo.
Ejemplo: Si recomiendas una laptop, debes decir "Laptop Pro X" (no solo "una laptop").
Se honesto sobre las limitaciones de los productos.""",
        "complaint": """Eres un especialista en atencion al cliente enfocado en resolver quejas.
Se empatico, reconoce el problema, y ofrece soluciones concretas.
Manten un tono profesional y comprensivo. Registra los detalles de la queja.""",
        "faq": """Eres un asistente virtual eficiente.
Responde preguntas frecuentes de forma clara y directa usando la informacion proporcionada.
Si no tienes la informacion exacta, indica como el usuario puede obtenerla.""",
        "general": """Eres un asistente virtual amigable y profesional.
Manten conversaciones naturales, ayuda con dudas generales, y dirige a los usuarios al tipo correcto de soporte.""",
    }

    # Umbrales de confianza
    INTENT_CONFIDENCE_THRESHOLD: float = 0.6
    FAQ_SIMILARITY_THRESHOLD: float = 0.7

    # Configuracion de conversacion
    MAX_HISTORY_LENGTH: int = 10

    @classmethod
    def validate(cls) -> bool:
        """Valida que la configuracion este completa."""
        if not cls.OPENAI_API_KEY.strip():
            print("ADVERTENCIA: OPENAI_API_KEY no esta configurada")
            print("Para usar el chatbot con OpenAI, configura tu API key:")
            print("export OPENAI_API_KEY='tu-api-key'  (Linux/Mac)")
            print("$env:OPENAI_API_KEY='tu-api-key'  (Windows PowerShell)")
            return False
        return True

    @classmethod
    def get_system_prompt(cls, intent: str) -> str:
        """Obtiene el prompt del sistema para una intencion especifica."""
        return cls.SYSTEM_PROMPTS.get(intent, cls.SYSTEM_PROMPTS["general"])
