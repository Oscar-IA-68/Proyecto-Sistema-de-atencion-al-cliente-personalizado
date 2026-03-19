"""
Estrategia de Recomendación de Productos
Sugiere productos basándose en necesidades del cliente
"""

from typing import List, Dict, Any
from src.core.interfaces import IChatStrategy, ChatContext, ChatResponse, ILLMClient, IDatabase
from src.core.config import Config


class RecommendationStrategy(IChatStrategy):
    """
    Estrategia para recomendar productos
    Cumple con SRP (Single Responsibility Principle) - solo maneja recomendaciones
    """
    
    def __init__(self, llm_client: ILLMClient, database: IDatabase):
        """
        Inicializa la estrategia con dependencias inyectadas
        
        Args:
            llm_client: Cliente LLM para generar recomendaciones
            database: Base de datos para consultar productos
        """
        self.llm_client = llm_client
        self.database = database
    
    def process(self, context: ChatContext) -> ChatResponse:
        """
        Procesa una solicitud de recomendación de producto
        
        Args:
            context: Contexto de la conversación
            
        Returns:
            Respuesta con recomendaciones personalizadas
        """
        user_input = context.user_input
        
        # Obtener catálogo de productos
        products = self.database.get_products()
        
        # Formatear información de productos
        products_info = self._format_products(products)
        
        # Obtener información del cliente si está disponible
        customer_context = ""
        if context.user_id:
            customer = self.database.get_customer_by_id(context.user_id)
            if customer:
                customer_context = f"\n\nCliente: {customer.get('name')} (Membresía: {customer.get('membership')})"
        
        # Construir prompt para recomendaciones
        prompt = f"""El cliente busca lo siguiente:
"{user_input}"
{customer_context}

Catálogo de productos disponibles:
{products_info}

Recomienda los productos más adecuados según sus necesidades. Explica por qué cada producto es una buena opción.
Si necesitas más información sobre su presupuesto o uso específico, pregúntale."""
        
        # Generar recomendación usando LLM
        response_text = self.llm_client.query(
            prompt=prompt,
            system_prompt=Config.get_system_prompt("recommendation"),
            temperature=0.7,
            max_tokens=500
        )
        
        # Extraer productos mencionados para metadata
        mentioned_products = self._extract_mentioned_products(response_text, products)
        
        return ChatResponse(
            message=response_text,
            intent="recommendation",
            confidence=0.9,
            metadata={
                "products_mentioned": mentioned_products,
                "catalog_size": len(products)
            }
        )
    
    def _format_products(self, products: List[Dict[str, Any]]) -> str:
        """Formatea productos para el prompt"""
        formatted = []
        for p in products:
            formatted.append(
                f"- {p['name']} (${p['price']}) - {p['category']}: {p['description']}"
            )
        return "\n".join(formatted)
    
    def _extract_mentioned_products(self, response: str, products: List[Dict[str, Any]]) -> List[str]:
        """Extrae nombres de productos mencionados en la respuesta"""
        mentioned = []
        response_lower = response.lower()
        
        for product in products:
            product_name = product.get('name', '')
            if product_name.lower() in response_lower:
                mentioned.append(product_name)
        
        return mentioned
    
    def get_strategy_name(self) -> str:
        """Retorna el nombre de la estrategia"""
        return "RecommendationStrategy"
