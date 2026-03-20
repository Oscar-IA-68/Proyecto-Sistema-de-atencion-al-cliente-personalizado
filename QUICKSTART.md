# Guía Rápida de Uso

## 🚀 Inicio Rápido (5 minutos)

### 1. Clonar e Instalar

```bash
# Clonar repositorio
git clone <url-del-repo>
cd Proyecto-Sistema-de-atencion-al-cliente-personalizado

# Crear entorno virtual
python -m venv venv

# Activar entorno
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# (Opcional para desarrollo y testing)
pip install -r requirements-dev.txt
```

### 2. Configurar API Key (Opcional)

También puedes crear un archivo `.env` en la raíz del proyecto:

```env
OPENAI_API_KEY=sk-tu-api-key-aqui
```

**Opción A: Con OpenAI (recomendado para producción)**
```bash
# Windows PowerShell:
$env:OPENAI_API_KEY = "sk-tu-api-key-aqui"

# Linux/Mac:
export OPENAI_API_KEY="sk-tu-api-key-aqui"
```

**Opción B: Sin API Key (modo demo)**
- El sistema funciona en modo simulación
- Respuestas basadas en keywords
- Ideal para desarrollo y testing

### 3. Ejecutar

**Interfaz CLI (Terminal):**
```bash
python main.py
```

**Interfaz Web (Streamlit):**
```bash
streamlit run app.py
```

---

## 💬 Ejemplos de Uso

### Soporte Técnico
```
💬 Tú: No puedo iniciar sesión en mi cuenta
🤖 Asistente: [Detecta "support"] 
              [Proporciona solución paso a paso]
              [Crea ticket #107]
```

### Recomendaciones
```
💬 Tú: Busco una laptop para diseño gráfico con buen presupuesto
🤖 Asistente: [Detecta "recommendation"]
              [Consulta catálogo]
              [Recomienda: Laptop Pro X ($1,299.99)]
```

### Quejas
```
💬 Tú: El producto llegó dañado, estoy muy molesto
🤖 Asistente: [Detecta "complaint", severidad: high]
              [Respuesta empática]
              [Ofrece compensación]
              [Crea ticket para supervisor]
```

### FAQ
```
💬 Tú: ¿Cuánto tarda el envío?
🤖 Asistente: [Detecta "faq"]
              [Busca en base de conocimiento]
              [Respuesta: "3-5 días hábil estándar, 1-2 express"]
```

---

## 🧪 Testing

Antes de correr tests, instala dependencias de desarrollo:

```bash
pip install -r requirements-dev.txt
```

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Con cobertura
pytest tests/ --cov=src --cov-report=html

# Test específico
pytest tests/test_chat_service.py -v
```

**Resultado esperado**: 72/72 tests pasando ✅

**Aislamiento en pruebas**:
- Los tests usan una copia temporal de `data/` (definida en `tests/conftest.py`).
- Ejecutar tests no debe modificar `data/tickets.json` ni otros JSON reales.

---

## 🎮 Comandos CLI

Dentro de la interfaz CLI (`python main.py`):

| Comando | Descripción |
|---------|-------------|
| `/ayuda` | Muestra ayuda completa |
| `/limpiar` | Limpia historial de conversación |
| `/stats` | Muestra estadísticas de la sesión |
| `/usuario 1` | Simula ser usuario con ID 1 (1-4) |
| `/salir` | Termina la conversación |

Métricas mostradas por `/stats`:

- `avg_response_time_ms`: promedio de latencia por respuesta.
- `p95_response_time_ms`: latencia en percentil 95.
- `fallback_to_general_count` y `fallback_rate_pct`: frecuencia de fallback a intención general.
- `intent_accuracy_pct`: accuracy de clasificación si hay etiquetas esperadas.
- `intent_evaluated_samples`: cantidad de muestras usadas para accuracy.

Lectura rápida recomendada:

- Si sube `fallback_rate_pct`, revisar reglas de detección de intención.
- Si sube `p95_response_time_ms`, revisar prompts o dependencia LLM.
- Si `intent_accuracy_pct` aparece como N/A, no se están enviando etiquetas esperadas.

---

## 🛠️ Estructura del Proyecto

```
Proyecto-Sistema-de-atencion-al-cliente-personalizado/
├── src/
│   ├── core/               # Interfaces y configuración
│   ├── policies/           # Reglas de negocio aisladas
│   ├── clients/            # Cliente OpenAI
│   ├── infrastructure/     # Base de datos simulada
│   ├── strategies/         # 5 estrategias de chat
│   ├── factories/          # Factory Pattern
│   ├── application/        # Servicio de chat
│   └── ui/                 # CLI y Streamlit
├── data/                   # Datos JSON simulados
├── tests/                  # Tests unitarios (72 tests)
├── main.py                 # Entry point CLI
├── app.py                  # Entry point Streamlit
└── requirements.txt        # Dependencias
```

---

## 🔧 Configuración Avanzada

### Cambiar Modelo de OpenAI

Editar [src/core/config.py](src/core/config.py):

```python
OPENAI_MODEL: str = "gpt-4"  # Cambiar de gpt-3.5-turbo a gpt-4
```

### Agregar Nueva Estrategia

1. Crear archivo en `src/strategies/`:

```python
# src/strategies/refund_strategy.py
from src.core.interfaces import IChatStrategy, ChatContext, ChatResponse

class RefundStrategy(IChatStrategy):
    def __init__(self, llm_client, database):
        self.llm_client = llm_client
        self.database = database
    
    def process(self, context: ChatContext) -> ChatResponse:
        # Tu lógica de reembolsos
        return ChatResponse(
            message="Procesando reembolso...",
            intent="refund",
            confidence=0.9
        )
    
    def get_strategy_name(self) -> str:
        return "RefundStrategy"
```

2. Registrar en `StrategyFactory`:

```python
# src/factories/strategy_factory.py
from src.strategies.refund_strategy import RefundStrategy

self._strategies["refund"] = RefundStrategy(llm_client, database)
```

3. Agregar prompt en `Config.SYSTEM_PROMPTS`

---

## 🎯 Casos de Uso Pre-cargados

El sistema incluye datos de ejemplo:

- **4 Clientes**: Con diferentes membresías (Premium, Standard, Basic)
- **6 Productos**: Electrónica, accesorios, audio
- **5 Tickets**: Histórico de soporte
- **8 FAQ**: Preguntas frecuentes comunes

Simula ser un usuario con `/usuario <id>` (1-4).

---

## 🐛 Troubleshooting

### Error: "OpenAI API key no configurada"
**Solución**: 
- Configura la variable de entorno `OPENAI_API_KEY`
- O usa el modo simulación (funciona sin API key)

### Error: "ModuleNotFoundError"
**Solución**:
```bash
pip install -r requirements.txt
```

### Tests fallan
**Solución**:
```bash
# Reinstalar dependencias
pip install --upgrade -r requirements-dev.txt

# Verificar entorno virtual activo
```

### Streamlit no abre
**Solución**:
```bash
# Verificar instalación
pip show streamlit

# Abrir manualmente
# Navega a: http://localhost:8501
```

---

## 📊 Métricas de Calidad

- ✅ **72 tests unitarios** (100% pasando)
- ✅ **5 estrategias** implementadas
- ✅ **2 interfaces** (CLI + Web)
- ✅ **Principios SOLID** aplicados
- ✅ **Inyección de dependencias** completa
- ✅ **Cobertura de casos**: soporte, recomendaciones, quejas, FAQ

### Métricas Operativas Disponibles

- ✅ Latencia promedio por interacción (`avg_response_time_ms`)
- ✅ Latencia p95 (`p95_response_time_ms`)
- ✅ Tasa de fallback a intención general (`fallback_rate_pct`)
- ✅ Accuracy de intención con muestras etiquetadas (`intent_accuracy_pct`)

---

## 🤝 Contribuir

1. Fork del proyecto
2. Crear rama feature: `git checkout -b feature/nueva-estrategia`
3. Commit: `git commit -m 'Agregar RefundStrategy'`
4. Push: `git push origin feature/nueva-estrategia`
5. Pull Request

---

## 📝 Recursos Adicionales

- [README.md](README.md) - Documentación completa
- [SOLID_ANALYSIS.md](SOLID_ANALYSIS.md) - Análisis de principios SOLID
- [tests/](tests/) - Ejemplos de testing con mocks

---

## ⏱️ Tiempos Estimados

- **Setup inicial**: 5 minutos
- **Primer test**: 2 minutos
- **Entender arquitectura**: 15 minutos
- **Agregar nueva estrategia**: 30 minutos
- **Personalizar para tu caso**: 1-2 horas

---

**¿Preguntas?** Revisa el [README.md](README.md) completo o ejecuta `/ayuda` en la CLI.
