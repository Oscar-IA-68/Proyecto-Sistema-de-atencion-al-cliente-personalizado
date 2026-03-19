"""
Estrategia de Soporte Técnico
Maneja consultas de soporte y problemas técnicos
"""

from src.core.interfaces import IChatStrategy, ChatContext, ChatResponse, ILLMClient, IDatabase
from src.core.config import Config
from src.policies.ticket_policy import TicketPolicy


class SupportStrategy(IChatStrategy):
    """
    Estrategia para manejar consultas de soporte técnico
    Cumple con SRP (Single Responsibility Principle) - solo maneja soporte
    """
    
    def __init__(self, llm_client: ILLMClient, database: IDatabase, ticket_policy: TicketPolicy | None = None):
        """
        Inicializa la estrategia con dependencias inyectadas
        
        Args:
            llm_client: Cliente LLM para generar respuestas
            database: Base de datos para consultar información
        """
        self.llm_client = llm_client
        self.database = database
        self.ticket_policy = ticket_policy or TicketPolicy()
    
    def process(self, context: ChatContext) -> ChatResponse:
        """
        Procesa una consulta de soporte técnico
        
        Args:
            context: Contexto de la conversación
            
        Returns:
            Respuesta con solución o pasos a seguir
        """
        user_input = context.user_input
        
        # Obtener información del cliente si está disponible
        customer_context = ""
        if context.user_id:
            customer = self.database.get_customer_by_id(context.user_id)
            if customer:
                tickets = self.database.get_tickets(customer_id=context.user_id)
                customer_context = f"\n\nContexto del cliente:\n- Nombre: {customer.get('name')}\n- Membresía: {customer.get('membership')}\n- Tickets previos: {len(tickets)}"
        
        # Construir prompt para el LLM
        prompt = f"""El cliente tiene este problema de soporte:
"{user_input}"
{customer_context}

Proporciona una solución clara y paso a paso. Si necesitas más información, pregúntala de forma específica."""
        
        # Generar respuesta usando LLM
        response_text = self.llm_client.query(
            prompt=prompt,
            system_prompt=Config.get_system_prompt("support"),
            temperature=0.7,
            max_tokens=500
        )
        
        # Crear ticket si el problema parece serio
        if self.ticket_policy.should_create_ticket(user_input):
            if context.user_id:
                ticket = self.database.create_ticket(
                    customer_id=context.user_id,
                    ticket_type="support",
                    subject=user_input[:100]  # Primeros 100 caracteres
                )
                response_text += f"\n\n📝 He creado el ticket #{ticket['id']} para dar seguimiento a tu problema."
        
        return ChatResponse(
            message=response_text,
            intent="support",
            confidence=0.9,
            metadata={"requires_followup": True}
        )
    
    def get_strategy_name(self) -> str:
        """Retorna el nombre de la estrategia"""
        return "SupportStrategy"
