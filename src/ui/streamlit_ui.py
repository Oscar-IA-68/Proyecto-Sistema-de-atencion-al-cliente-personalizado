"""
Interfaz Streamlit
Interfaz web moderna para el chatbot
"""

import streamlit as st
from datetime import datetime
from typing import Optional
from src.application.app_factory import AppFactory


def initialize_session_state():
    """Inicializa el estado de la sesión de Streamlit"""
    if 'chat_service' not in st.session_state:
        # Inicializar componentes de forma centralizada para evitar wiring duplicado.
        components = AppFactory.create_components()
        
        st.session_state.chat_service = components.chat_service
        st.session_state.database = components.database
        st.session_state.llm_provider = components.provider_name
        st.session_state.messages = []
        st.session_state.current_user_id = None
        st.session_state.total_conversations = 0


def render_sidebar():
    """Renderiza la barra lateral con configuración y estadísticas"""
    with st.sidebar:
        st.title("⚙️ Configuración")
        
        # Selector de usuario
        st.subheader("👤 Usuario Simulado")
        customers = st.session_state.database.get_customers()
        customer_options = {f"{c['name']} (ID: {c['id']})": c['id'] for c in customers}
        customer_options["Sin usuario"] = None
        
        selected_customer = st.selectbox(
            "Selecciona un usuario:",
            options=list(customer_options.keys()),
            index=0
        )
        st.session_state.current_user_id = customer_options[selected_customer]
        
        # Estadísticas
        st.subheader("📊 Estadísticas")
        stats = st.session_state.chat_service.get_stats()
        db_stats = st.session_state.database.get_stats()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Mensajes", stats['total_messages'])
            st.metric("Clientes", db_stats['total_customers'])
        with col2:
            st.metric("Conversaciones", st.session_state.total_conversations)
            st.metric("Productos", db_stats['total_products'])
        
        # Información de la BD
        st.subheader("💾 Base de Datos")
        st.info(f"""
        **Tickets abiertos:** {db_stats['open_tickets']}  
        **FAQ disponibles:** {db_stats['total_faq']}  
        **Categorías:** {', '.join(db_stats['product_categories'])}
        """)
        
        # Controles
        st.subheader("🎮 Controles")
        if st.button("🗑️ Limpiar Conversación", use_container_width=True):
            st.session_state.chat_service.clear_history()
            st.session_state.messages = []
            st.rerun()
        
        # API Key status
        st.subheader("🔑 Estado API")
        provider = st.session_state.get("llm_provider", "desconocido")
        if provider == "mock":
            st.warning("⚠️ Modo simulación activo")
        else:
            st.success(f"✅ Proveedor activo: {provider}")


def render_chat_interface():
    """Renderiza la interfaz principal de chat"""
    st.title("🤖 Chatbot de Atención al Cliente")
    
    # Tabs para diferentes vistas
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📋 Historial", "ℹ️ Info"])
    
    with tab1:
        render_chat_tab()
    
    with tab2:
        render_history_tab()
    
    with tab3:
        render_info_tab()


def render_chat_tab():
    """Renderiza el tab de chat"""
    # Mensajes del chat
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "metadata" in message and message["metadata"]:
                    with st.expander("📊 Detalles"):
                        st.json(message["metadata"])
    
    # Input de usuario
    if prompt := st.chat_input("Escribe tu mensaje aquí..."):
        # Agregar mensaje del usuario
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().isoformat()
        })
        
        # Mostrar mensaje del usuario
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Procesar respuesta
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                response = st.session_state.chat_service.process_message(
                    user_input=prompt,
                    user_id=st.session_state.current_user_id
                )
                
                st.markdown(response.message)
                
                # Metadata
                metadata = {
                    "intent": response.intent,
                    "confidence": f"{response.confidence:.2f}",
                    **response.metadata
                }
                
                with st.expander("📊 Detalles"):
                    st.json(metadata)
        
        # Agregar respuesta al historial
        st.session_state.messages.append({
            "role": "assistant",
            "content": response.message,
            "metadata": metadata,
            "timestamp": datetime.now().isoformat()
        })
        
        st.session_state.total_conversations += 1
        st.rerun()


def render_history_tab():
    """Renderiza el tab de historial"""
    st.subheader("📋 Historial de Conversación")
    
    if not st.session_state.messages:
        st.info("No hay mensajes en el historial aún. ¡Comienza una conversación!")
        return
    
    # Mostrar historial en tabla
    for i, msg in enumerate(st.session_state.messages):
        col1, col2, col3 = st.columns([1, 5, 2])
        
        with col1:
            icon = "👤" if msg["role"] == "user" else "🤖"
            st.markdown(f"### {icon}")
        
        with col2:
            st.markdown(f"**{msg['content'][:100]}...**" if len(msg['content']) > 100 else f"**{msg['content']}**")
            if "metadata" in msg:
                st.caption(f"Intención: {msg.get('metadata', {}).get('intent', 'N/A')}")
        
        with col3:
            timestamp = msg.get('timestamp', 'N/A')
            if timestamp != 'N/A':
                time = datetime.fromisoformat(timestamp).strftime("%H:%M:%S")
                st.caption(time)
        
        st.divider()


def render_info_tab():
    """Renderiza el tab de información"""
    st.subheader("ℹ️ Información del Sistema")
    
    st.markdown("""
    ### 🎯 Capacidades del Chatbot
    
    Este chatbot puede ayudarte con:
    
    1. **🔧 Soporte Técnico**
       - Resolver problemas técnicos
       - Ayuda con errores
       - Crear tickets de soporte
    
    2. **🛍️ Recomendaciones de Productos**
       - Sugerir productos según necesidades
       - Comparar opciones
       - Información de catálogo
    
    3. **📝 Quejas y Feedback**
       - Manejar quejas con empatía
       - Registrar feedback
       - Proponer soluciones
    
    4. **❓ Preguntas Frecuentes**
       - Responder dudas comunes
       - Políticas de la empresa
       - Información general
    
    ### 🏗️ Arquitectura
    
    El sistema está construido siguiendo **principios SOLID**:
    
    - **S**ingle Responsibility: Cada clase tiene una única responsabilidad
    - **O**pen/Closed: Extensible sin modificar código existente
    - **L**iskov Substitution: Las interfaces son intercambiables
    - **I**nterface Segregation: Interfaces específicas por cliente
    - **D**ependency Inversion: Depende de abstracciones, no implementaciones
    
    ### 📊 Base de Datos Simulada
    
    El sistema simula una base de datos real con:
    - Clientes y sus perfiles
    - Catálogo de productos
    - Tickets de soporte
    - Base de conocimiento (FAQ)
    
    ### 🔧 Tecnologías
    
    - **Python 3.8+**
    - **OpenAI API** (GPT-3.5-turbo)
    - **Streamlit** (interfaz web)
    - **JSON** (persistencia simulada)
    """)
    
    # Ejemplos de uso
    with st.expander("💡 Ejemplos de Consultas"):
        st.markdown("""
        **Soporte Técnico:**
        - "No puedo iniciar sesión en mi cuenta"
        - "Tengo un error al procesar el pago"
        
        **Recomendaciones:**
        - "Busco una laptop para diseño gráfico"
        - "¿Qué mouse me recomiendas?"
        
        **Quejas:**
        - "El producto llegó dañado"
        - "Muy mal servicio, estoy molesto"
        
        **FAQ:**
        - "¿Cómo cambio mi contraseña?"
        - "¿Cuánto tarda el envío?"
        """)


def main():
    """Función principal de la aplicación Streamlit"""
    st.set_page_config(
        page_title="Chatbot Atención al Cliente",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Inicializar estado
    initialize_session_state()
    
    # Renderizar UI
    render_sidebar()
    render_chat_interface()
    
    # Footer
    st.markdown("---")
    st.caption("🤖 Sistema de Atención al Cliente Automatizado | Proyecto LLM 2026")


if __name__ == "__main__":
    main()
