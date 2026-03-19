"""
Estrategia de Quejas y Feedback
Maneja quejas de clientes con empatía y registra feedback
"""

from src.core.interfaces import IChatStrategy, ChatContext, ChatResponse, ILLMClient, IDatabase
from src.core.config import Config
from src.policies.severity_policy import SeverityPolicy


class ComplaintStrategy(IChatStrategy):
    """
    Estrategia para manejar quejas y feedback negativo
    Cumple con SRP (Single Responsibility Principle) - solo maneja quejas
    """
    
    def __init__(self, llm_client: ILLMClient, database: IDatabase, severity_policy: SeverityPolicy | None = None):
        """
        Inicializa la estrategia con dependencias inyectadas
        
        Args:
            llm_client: Cliente LLM para generar respuestas empáticas
            database: Base de datos para registrar quejas
        """
        self.llm_client = llm_client
        self.database = database
        self.severity_policy = severity_policy or SeverityPolicy()
    
    def process(self, context: ChatContext) -> ChatResponse:
        """
        Procesa una queja o feedback negativo
        
        Args:
            context: Contexto de la conversación
            
        Returns:
            Respuesta empática con soluciones propuestas
        """
        user_input = context.user_input
        
        # Categorizar la gravedad de la queja
        severity = self.severity_policy.assess(user_input)
        
        # Obtener información del cliente si está disponible
        customer_context = ""
        if context.user_id:
            customer = self.database.get_customer_by_id(context.user_id)
            if customer:
                tickets = self.database.get_tickets(customer_id=context.user_id)
                customer_context = f"\n\nCliente: {customer.get('name')} (Membresía: {customer.get('membership')}, Tickets previos: {len(tickets)})"
        
        # Construir prompt para manejo de quejas
        prompt = f"""El cliente tiene esta queja o feedback negativo:
"{user_input}"
{customer_context}

Gravedad estimada: {severity}

Responde con:
1. Reconocimiento empático del problema
2. Disculpa sincera si es apropiado
3. Solución concreta o pasos siguientes
4. Compensación si la gravedad es alta (descuento, envío gratis, etc.)

Mantén un tono profesional y comprensivo."""
        
        # Generar respuesta usando LLM
        response_text = self.llm_client.query(
            prompt=prompt,
            system_prompt=Config.get_system_prompt("complaint"),
            temperature=0.6,  # Menor temperatura para respuestas más consistentes
            max_tokens=500
        )
        
        # Crear ticket para la queja
        ticket = None
        if context.user_id:
            ticket = self.database.create_ticket(
                customer_id=context.user_id,
                ticket_type="complaint",
                subject=user_input[:100]
            )
            response_text += f"\n\n📋 He registrado tu queja con el ticket #{ticket['id']}. Un supervisor revisará tu caso y se pondrá en contacto contigo."
        
        return ChatResponse(
            message=response_text,
            intent="complaint",
            confidence=0.9,
            metadata={
                "severity": severity,
                "ticket_id": ticket['id'] if ticket else None,
                "requires_supervisor": severity == "high"
            }
        )
    
    def get_strategy_name(self) -> str:
        """Retorna el nombre de la estrategia"""
        return "ComplaintStrategy"
