# 🤖 Sistema de Atención al Cliente Automatizado

**Proyecto LLM - Chatbot Inteligente con OpenAI**

Sistema de atención al cliente automatizado que utiliza modelos de lenguaje de gran escala (LLM) para proporcionar soporte técnico, recomendaciones de productos, manejo de quejas y respuestas a preguntas frecuentes.

## 📋 Descripción

Este proyecto implementa un chatbot avanzado siguiendo los **principios SOLID** y patrones de diseño profesionales. El sistema puede:

- 🔧 **Soporte Técnico**: Resolver problemas, crear tickets, asistencia paso a paso
- 🛍️ **Recomendaciones**: Sugerir productos basados en necesidades del cliente
- 📝 **Manejo de Quejas**: Respuestas empáticas y registro de feedback
- ❓ **FAQ**: Responder preguntas frecuentes usando base de conocimiento

## 🏗️ Arquitectura SOLID

El proyecto está diseñado con principios SOLID en mente:

```
src/
├── core/               # Interfaces y configuración (DIP)
│   ├── interfaces.py   # Abstracciones (ILLMClient, IDatabase, IChatStrategy)
│   └── config.py       # Configuración centralizada
├── policies/           # Reglas de negocio aisladas (SRP)
│   ├── ticket_policy.py
│   ├── severity_policy.py
│   └── fallback_policy.py
├── clients/            # Clientes externos (OpenAI)
│   └── openai_client.py
├── infrastructure/     # Persistencia y BD simulada
│   └── database_sim.py
├── strategies/         # Strategy Pattern (OCP, SRP)
│   ├── support_strategy.py
│   ├── recommendation_strategy.py
│   ├── complaint_strategy.py
│   ├── faq_strategy.py
│   └── general_strategy.py
├── factories/          # Factory Pattern (OCP)
│   └── strategy_factory.py
├── application/        # Servicios de aplicación (SRP)
│   └── chat_service.py
└── ui/                 # Interfaces de usuario
    ├── cli_interface.py
    └── streamlit_ui.py
```

### Principios SOLID Aplicados

- **S**ingle Responsibility: Cada clase tiene una única responsabilidad
- **O**pen/Closed: Extensible sin modificar código (Strategy Pattern)
- **L**iskov Substitution: Interfaces intercambiables (ILLMClient permite cambiar proveedores)
- **I**nterface Segregation: Interfaces específicas por cliente
- **D**ependency Inversion: Inyección de dependencias manual, abstracción sobre concreción

### Estado Técnico Actual

- Reglas críticas aisladas en `src/policies/` para reforzar SRP
- Estrategias delegan reglas de ticket, severidad y fallback
- Métricas operativas en `ChatService`: latencia, fallback y accuracy de intención
- Tests ejecutados con aislamiento de datos para no mutar archivos en `data/`
- Suite de pruebas actual: **72 tests pasando**

## 🚀 Instalación

### Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Cuenta de OpenAI con API key (opcional, funciona en modo simulado sin ella)

### Paso 1: Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd Proyecto-Sistema-de-atencion-al-cliente-personalizado
```

### Paso 2: Crear Entorno Virtual

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

Para desarrollo y pruebas (pytest, black, flake8):

```bash
pip install -r requirements-dev.txt
```

### Paso 4: Configurar API Key de OpenAI (Opcional)

Puedes configurar la API key en variables de entorno o en un archivo `.env` en la raíz del proyecto:

```env
OPENAI_API_KEY=tu-api-key-aqui
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY = "tu-api-key-aquí"
```

**Windows (CMD):**
```cmd
set OPENAI_API_KEY=tu-api-key-aquí
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY="tu-api-key-aquí"
```

> **Nota**: Si no configuras la API key, el sistema funcionará en **modo simulación** con respuestas predefinidas basadas en keywords.

## 💻 Uso

### Opción 1: Interfaz CLI (Línea de Comandos)

```bash
python main.py
```

**Comandos disponibles en CLI:**
- `/ayuda` - Muestra ayuda y comandos
- `/limpiar` - Limpia historial de conversación
- `/stats` - Muestra estadísticas de la sesión
- `/usuario <id>` - Simula ser un usuario específico (1-4)
- `/salir` - Termina la conversación

### Métricas Operativas (Etapa 4)

La sesión de chat ahora registra métricas operativas para evaluar calidad de ejecución además de la funcionalidad.

- `avg_response_time_ms`: promedio de tiempo de respuesta por interacción.
- `p95_response_time_ms`: percentil 95 de latencia; muestra la experiencia en el peor 5% de casos.
- `fallback_to_general_count`: cuántas veces la detección de intención terminó en `general`.
- `fallback_rate_pct`: porcentaje de fallback sobre interacciones de usuario.
- `intent_accuracy_pct`: porcentaje de acierto de intención cuando se provee etiqueta esperada.
- `intent_evaluated_samples`: número de muestras usadas para calcular accuracy.

Fórmulas usadas:

- `fallback_rate_pct = (fallback_to_general_count / user_messages) * 100`
- `intent_accuracy_pct = (intent_predictions_correct / intent_predictions_total) * 100`

Notas de interpretación:

- `intent_accuracy_pct` puede ser `N/A` cuando no se envía `expected_intent` en `process_message(...)`.
- Reducir `fallback_rate_pct` mejora cobertura de intenciones específicas.
- Un `p95_response_time_ms` bajo es más relevante que solo el promedio para validar experiencia real.

**Ejemplos de consultas:**
```
💬 Tú: No puedo iniciar sesión en mi cuenta
💬 Tú: Busco una laptop para diseño gráfico
💬 Tú: El producto llegó dañado, estoy molesto
💬 Tú: ¿Cómo cambio mi contraseña?
```

### Opción 2: Interfaz Web (Streamlit)

```bash
streamlit run app.py
```

Esto abrirá automáticamente tu navegador en `http://localhost:8501`

**Características de la interfaz web:**
- 💬 Chat interactivo con historial
- 👤 Selector de usuario simulado
- 📊 Estadísticas en tiempo real
- 📋 Vista de historial completo
- ℹ️ Información del sistema

## 🧪 Testing

> **Prerequisito**: Instalar dependencias de desarrollo con `pip install -r requirements-dev.txt`.

### Ejecutar Tests Unitarios

```bash
pytest tests/ -v
```

### Ejecutar Tests con Cobertura

```bash
pytest tests/ --cov=src --cov-report=html
```

> **Nota técnica**: Los tests redirigen las rutas de `Config` a una copia temporal de `data/` definida en `tests/conftest.py`. Esto evita modificar `data/tickets.json` durante las pruebas.

> **Cobertura de métricas**: `tests/test_chat_service.py` valida la presencia y cálculo base de `avg_response_time_ms`, `p95_response_time_ms`, `fallback_rate_pct` e `intent_accuracy_pct`.

## 📊 Base de Datos Simulada

El sistema incluye datos JSON simulados en la carpeta `data/`:

- **customers.json**: 4 clientes de ejemplo
- **products.json**: 6 productos en diferentes categorías
- **tickets.json**: 5 tickets de soporte históricos
- **faq.json**: 8 preguntas frecuentes

## 🎯 Casos de Uso Implementados

### 1. Soporte Técnico
```
Usuario: "Tengo un error al procesar mi pago"
Sistema: [Detecta intención "support"]
         [Genera solución paso a paso]
         [Crea ticket de seguimiento]
```

### 2. Recomendaciones de Productos
```
Usuario: "Busco auriculares para gaming"
Sistema: [Detecta intención "recommendation"]
         [Consulta catálogo de productos]
         [Recomienda productos específicos con justificación]
```

### 3. Manejo de Quejas
```
Usuario: "Muy mal servicio, el producto llegó dañado"
Sistema: [Detecta intención "complaint"]
         [Evalúa severidad: high/medium/low]
         [Respuesta empática + solución]
         [Crea ticket para supervisor]
```

### 4. FAQ
```
Usuario: "¿Cuánto tarda el envío?"
Sistema: [Detecta intención "faq"]
         [Busca en base de conocimiento]
         [Retorna respuesta precisa + FAQ relacionadas]
```

## 🔧 Extensibilidad

### Agregar Nueva Estrategia

1. Crear archivo en `src/strategies/nueva_strategy.py`
2. Implementar la interfaz `IChatStrategy`
3. Registrar en `StrategyFactory`

```python
# src/strategies/nueva_strategy.py
from src.core.interfaces import IChatStrategy, ChatContext, ChatResponse

class NuevaStrategy(IChatStrategy):
    def process(self, context: ChatContext) -> ChatResponse:
        # Tu lógica aquí
        pass
    
    def get_strategy_name(self) -> str:
        return "NuevaStrategy"
```

### Cambiar Proveedor de LLM

Gracias a la interfaz `ILLMClient`, puedes cambiar de OpenAI a otro proveedor:

```python
# src/clients/anthropic_client.py
class AnthropicClient(ILLMClient):
    def query(self, prompt: str, ...) -> str:
        # Implementación con Anthropic Claude
        pass
```

## 📝 Estructura de Decisiones

- **Inyección Manual** vs DI Container: Simplicidad para prototipo, escalable a futuro
- **JSON en Memoria** vs Base de Datos: Suficiente para demo, fácil migrar a PostgreSQL/MongoDB
- **Strategy Pattern**: Cada tipo de consulta es extensible sin modificar código existente
- **Factory Pattern**: Routing automático de intenciones, fácil agregar nuevas
- **Policies Module**: Reglas críticas aisladas para reducir acoplamiento en estrategias
- **Test Data Isolation**: Pruebas sin efectos colaterales sobre archivos JSON del repositorio

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia especificada en el archivo LICENSE.

## 👨‍💻 Autor

Proyecto desarrollado como parte del curso de Inteligencia Artificial - LLM 2026

## 🙏 Agradecimientos

- OpenAI por proporcionar la API de GPT
- Streamlit por el framework de UI
- Comunidad de Python por las excelentes bibliotecas
