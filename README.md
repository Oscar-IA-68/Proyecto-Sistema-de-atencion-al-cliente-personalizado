# 🤖 Sistema de Atención al Cliente Automatizado

**Proyecto LLM - Chatbot Inteligente Multi-proveedor**

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
├── clients/            # Clientes externos (OpenAI + mocks)
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
│   ├── llm_provider_factory.py  # Selección de proveedor LLM por configuración
│   └── strategy_factory.py
├── application/        # Servicios de aplicación (SRP)
│   ├── app_factory.py   # Wiring centralizado de dependencias
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
- Suite de pruebas: ejecutable con `pytest tests/ -v`

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
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
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
LLM_PROVIDER=openai
```

### Configuracion de limites de tokens (recomendado)

El sistema ya no fuerza limites hardcodeados por estrategia. Puedes definirlos por entorno segun tu plan y proveedor.

- Si NO defines limites, la aplicacion deja que el proveedor use su comportamiento por defecto.
- Si defines limites, se aplican sin necesidad de cambiar codigo.

Variables disponibles:

```env
# Compatibilidad por proveedor
OPENAI_MAX_TOKENS=
GOOGLE_MAX_TOKENS=

# Limite global para respuestas del bot
DEFAULT_RESPONSE_MAX_TOKENS=

# Limites por tipo de estrategia (prioridad sobre el global)
SUPPORT_MAX_TOKENS=
RECOMMENDATION_MAX_TOKENS=
COMPLAINT_MAX_TOKENS=
FAQ_MAX_TOKENS=
GENERAL_MAX_TOKENS=

# Limite para clasificacion de intencion (recomendado mantener bajo)
INTENT_CLASSIFICATION_MAX_TOKENS=50
```

Orden de prioridad para respuestas:
1. Limite por estrategia (`*_MAX_TOKENS`)
2. Limite global (`DEFAULT_RESPONSE_MAX_TOKENS`)
3. Limite por proveedor (`OPENAI_MAX_TOKENS` o `GOOGLE_MAX_TOKENS`)
4. Sin limite explicito de la app (usa default del proveedor)

`LLM_PROVIDER` define qué cliente se inicializa en runtime:

- `openai`: usa `OpenAIClient` (requiere `OPENAI_API_KEY`)
- `google_ai_studio`: usa `GoogleAIStudioClient` con modelos Gemini (requiere `GOOGLE_API_KEY`)
- `mock`: usa `MockLLMClient` (sin llamadas externas)

Si seleccionas `openai` o `google_ai_studio` sin API key correspondiente, el sistema degrada automáticamente a `mock`.

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

### Opción 2: Usar Google AI Studio (RECOMENDADO PARA PROBAR GRATIS)

Si prefieres **probar la aplicación sin costo**, Google AI Studio ofrece tokens gratuitos ilimitados para modelos Gemini.

#### Paso 1: Crear Cuenta en Google AI Studio

1. Abre https://aistudio.google.com en tu navegador
2. Inicia sesión con tu cuenta Google (si no tienes, crea una)
3. Acepta los términos de uso de Gemini API
4. Se te mostrará automáticamente el dashboard de AI Studio

#### Paso 2: Obtener API Key de Google

1. Haz clic en **"Get API key"** en la interfaz de AI Studio
2. Selecciona **"Create API key in new Google Cloud project"** (o usa un proyecto existente)
3. Se generará automáticamente una nueva API key
4. Copia la key y guárdala de forma segura

#### Paso 3: Configurar en Tu Entorno

En archivo `.env` o variables de entorno del sistema:

```env
LLM_PROVIDER=google_ai_studio
GOOGLE_API_KEY=tu-api-key-de-google-aqui
GOOGLE_MODEL=gemini-2.5-flash
```

**Windows (PowerShell):**
```powershell
$env:LLM_PROVIDER = "google_ai_studio"
$env:GOOGLE_API_KEY = "tu-api-key-aquí"
```

**Linux/Mac:**
```bash
export LLM_PROVIDER="google_ai_studio"
export GOOGLE_API_KEY="tu-api-key-aquí"
```

#### Free Tier de Google AI Studio

- ✅ **Tokens gratuitos ilimitados** para probar (dentro de límites de cuota mensuales)
- ✅ **Modelos disponibles**: Gemini 2.5 Flash, Gemini 1.5 Pro, Gemini 1.5 Flash
- ⚠️ **Límites recomendados**: 
  - ~1,500 requests por minuto en free tier
  - ~15,000 tokens de entrada por minuto
  - Si alcanzas límites, el sistema fallará gracefully y reportará error
- 💡 **Recomendación**: Usa `gemini-2.5-flash` (más rápido y económico) para desarrollo

Si excedes cuotas durante desarrollo, puedes:
- Cambiar temporalmente a `LLM_PROVIDER=mock` sin modificar otros archivos
- Esperar a que se resetee la cuota (normalmente cada 24 horas)
- Actualizar a un plan de pago en Google Cloud Console

> **Nota**: Si no configuras API key, el sistema funcionará en **modo simulación** con respuestas predefinidas basadas en keywords.

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

### Scripts de Pruebas Operativas

Para flujos de validacion manual, smoke avanzado y revalidaciones, revisa:

- [scripts/README.md](scripts/README.md)

Ese documento explica cuando ejecutar cada script y donde se guardan los artefactos.

> **Advertencia importante**: A diferencia de `pytest` (aislado por `tests/conftest.py`),
> los scripts en `scripts/` pueden mutar datos reales de `data/` durante pruebas
> funcionales (por ejemplo, crear tickets). Para ejecuciones repetibles, usar copia
> de `data/` o entorno dedicado.

### Reportes y Evidencia

Los resultados de ejecuciones y revalidaciones se almacenan en [informes](informes):

- [informes/analisis](informes/analisis)
- [informes/ejecuciones](informes/ejecuciones)
- [informes/revalidacion](informes/revalidacion)
- [informes/resumenes](informes/resumenes)

Convenciones y plantilla de reportes:

- [informes/GUIA_CREACION_INFORMES.md](informes/GUIA_CREACION_INFORMES.md)

## 📊 Base de Datos Simulada

El sistema incluye datos JSON simulados en la carpeta `data/`:

- **customers.json**: 5 clientes de ejemplo
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

Gracias a la interfaz `ILLMClient`, puedes cambiar proveedor sin modificar estrategias.

Compatibilidad actual del proyecto:

- ✅ `openai` (modelo configurable con `OPENAI_MODEL`)
- ✅ `mock` (modo simulación para desarrollo y pruebas)
- 🧩 Extensible a nuevos proveedores vía `LLMProviderFactory.register_provider(...)`

Ejemplo de extensión:

```python
# src/clients/anthropic_client.py (ejemplo de extensión)
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

## 📚 Documentación Técnica

- [scripts/README.md](scripts/README.md) - Guia de scripts operativos de pruebas
- [informes/GUIA_CREACION_INFORMES.md](informes/GUIA_CREACION_INFORMES.md) - Convencion para creacion de informes
- [SOLID_ANALYSIS.md](SOLID_ANALYSIS.md) - Analisis de arquitectura y principios SOLID

## 📄 Licencia

Este proyecto está bajo la licencia especificada en el archivo LICENSE.

## 👨‍💻 Autor

Proyecto desarrollado como parte del curso de Inteligencia Artificial - LLM 2026

## 🙏 Agradecimientos

- OpenAI por proporcionar la API de GPT
- Streamlit por el framework de UI
- Comunidad de Python por las excelentes bibliotecas
