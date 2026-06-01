# Agente de Atención al Cliente - CargaMax Sur Ltda.

Agente funcional desarrollado como parte de la Evaluación Parcial 2 del curso **ISY0101 - Optativo Ingeniería de Soluciones con IA**.

Continúa el proyecto iniciado en la Evaluación Parcial 1, implementando un agente con herramientas de consulta, escritura y razonamiento, memoria de corto y largo plazo, y planificación de tareas para atender consultas B2B de logística.

## Requisitos

- Python 3.10 o superior
- pip
- Clave API de Groq (gratuita, se obtiene en [console.groq.com](https://console.groq.com))

## Instalación

1. Clonar o descargar este repositorio.

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Configurar la clave API de Groq como variable de entorno:

**Windows PowerShell:**
```powershell
$env:GROQ_API_KEY="tu_clave_de_groq_aqui"
```

**Windows CMD:**
```cmd
set GROQ_API_KEY=tu_clave_de_groq_aqui
```

**Linux / macOS:**
```bash
export GROQ_API_KEY=tu_clave_de_groq_aqui
```

> Nota: también puedes crear un archivo `.env` en la raíz del proyecto con el contenido `GROQ_API_KEY=tu_clave_de_groq_aqui`. Este archivo ya está incluido en `.gitignore` para que no se suba al repositorio.

## Ejecución

### Demo principal (4 consultas predefinidas)

```bash
python main.py
```

### Demos individuales

Consulta simple vs. compleja con RAG:
```bash
python tests/demo_consulta.py
```

Memoria de corto y largo plazo:
```bash
python tests/demo_memoria.py
```

Toma de decisiones adaptativas:
```bash
python tests/demo_decisiones.py
```

## Arquitectura del Agente

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENTE CARGAMAX                              │
│  Orquestador principal que coordina tools, memoria y planner   │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│    TOOLS      │     │    MEMORIA    │     │  PLANIFICADOR │
├───────────────┤     ├───────────────┤     ├───────────────┤
│ • Consulta    │     │ • Corto plazo │     │ • Descompone  │
│   (RAG)       │     │   (buffer     │     │   consultas   │
│ • Redacción   │     │   conversac.) │     │   complejas   │
│ • Razonamiento│     │ • Largo plazo │     │ • Ajusta plan │
│   (router)    │     │   (vectorial  │     │   ante fallos │
└───────────────┘     │   semántica)  │     └───────────────┘
                      └───────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐   ┌─────────────────┐   ┌─────────────────┐
│    FAISS      │   │    Documentos   │   │      Groq       │
│  Vector Store │   │   Mock internos │   │  (LLM + Emb.)  │
│  (RAG + Mem.) │   │   de CargaMax   │   │                 │
└───────────────┘   └─────────────────┘   └─────────────────┘
```

## Estructura del Repositorio

```
agente_cargamax/
├── config.py                  # Configuración central (API keys, prompts, constantes)
├── core/
│   └── agent.py               # Orquestador principal del agente
├── tools/
│   ├── documentos.py          # Tool de consulta RAG sobre documentos internos
│   ├── redaccion.py           # Tool de redacción de respuestas formales
│   └── razonador.py           # Tool de clasificación de intención y validación
├── memory/
│   ├── conversacional.py      # Memoria de corto plazo (historial conversacional)
│   └── semantica.py           # Memoria de largo plazo (recuperación semántica)
├── planner/
│   └── planificador.py        # Descomposición de consultas complejas en pasos
└── data/
    ├── tarifario_2024.txt     # Tarifario base de rutas nacionales
    ├── terminos_generales.txt # Términos y condiciones del servicio
    └── normativas_adr.txt     # Normativas de carga peligrosa

tests/
├── demo_consulta.py           # Demo de consultas simples y complejas
├── demo_memoria.py            # Demo de memoria corto/largo plazo
└── demo_decisiones.py         # Demo de toma de decisiones adaptativas

docs/
├── diagrama_arquitectura.md   # Diagramas Mermaid de arquitectura
└── ejemplos_flujo.md          # Casos de uso paso a paso

main.py                        # Punto de entrada principal
requirements.txt               # Dependencias del proyecto
README.md                      # Este archivo
Informe_EA2.md                 # Informe técnico de la evaluación
```

## Componentes Principales

### 1. Tool de Consulta (RAG)

Usa **LangChain + FAISS + HuggingFace Embeddings** para recuperar información de documentos internos de CargaMax (tarifario, términos, normativas ADR) y generar respuestas fundadas.

### 2. Tool de Redacción

Transforma la información técnica recuperada en comunicaciones formales, cordiales y estructuradas para clientes B2B, respetando el tono institucional de CargaMax.

### 3. Tool de Razonamiento

Clasifica la intención del cliente, evalúa si la consulta puede resolverse autónomamente o debe escalarse a un ejecutivo humano, y valida que las respuestas no violen guardrails de seguridad.

### 4. Memoria Corto Plazo

Mantiene el hilo conversacional actual usando `ConversationBufferMemory` de LangChain, permitiendo referencias implícitas y coherencia dentro de una misma sesión.

### 5. Memoria Largo Plazo

Almacena resúmenes de interacciones en una colección vectorial separada, permitiendo al agente "recordar" preferencias y contexto de clientes recurrentes entre sesiones distintas.

### 6. Planificador de Tareas

Descompone consultas complejas (multipregunta) en subtareas secuenciales y ajusta el plan dinámicamente si un paso falla o no encuentra información suficiente.

## Guardrails de Seguridad

El agente implementa restricciones heredadas del diseño de la EP1:

- No garantiza disponibilidad de flota en tiempo real.
- No emite cotizaciones vinculantes sin confirmación formal.
- No solicita datos sensibles como claves bancarias.
- Escalación automática a ejecutivo humano ante cotizaciones formales, reclamos o carga peligrosa sin documentación.
- Todas las respuestas se validan contra violaciones de guardrails antes de entregarse al cliente.

## Frameworks y Tecnologías

| Componente | Tecnología | Justificación |
|------------|------------|---------------|
| Orquestación | LangChain | Framework estándar para agentes, memoria, tools y RAG en Python. Comunidad activa y documentación extensa. |
| LLM | Groq (Llama 3 70B) | Inferencia ultrarrápida, modelos open-source robustos, tier gratuito ideal para prototipado académico. |
| Embeddings | HuggingFace (MiniLM) | Modelo local, sin costo de API, compatible con FAISS. |
| Vector Store | FAISS (Meta) | Librería estándar de Meta para recuperación semántica, funciona local, sin cuentas cloud, integración directa con LangChain. |
| Evaluación | RAGAS (referencia EP1) | Métricas de faithfulness y relevancy para garantizar calidad del RAG. |

## Licencia y Autoría

Proyecto académico desarrollado para el curso ISY0101 - Optativo Ingeniería de Soluciones con IA.

