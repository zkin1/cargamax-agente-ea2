# Diagrama de Arquitectura del Agente CargaMax

## Vista General de Componentes

```mermaid
graph TB
    subgraph Entrada["📥 Entrada"]
        C[Cliente B2B]
    end

    subgraph Agente["🤖 Agente CargaMax"]
        A[Orquestador Principal]
        R[Tool Razonamiento<br/>Clasificación + Validación]
        P[Planificador de Tareas]
        
        subgraph Tools["🔧 Tools"]
            T1[Tool Consulta<br/>RAG sobre docs]
            T2[Tool Redacción<br/>Respuestas formales]
        end
        
        subgraph Memoria["🧠 Memoria"]
            M1[Memoria Corto Plazo<br/>Historial conversacional]
            M2[Memoria Largo Plazo<br/>Contexto semántico]
        end
    end

    subgraph Datos["📚 Datos y Modelos"]
        DB[(FAISS<br/>Vector Store)]
        DOCS[Documentos CargaMax<br/>Tarifario / Términos / ADR]
        LLM[Groq API<br/>Llama 3 70B]
        EMB[HuggingFace<br/>Embeddings MiniLM]
    end

    subgraph Salida["📤 Salida"]
        RES[Respuesta al Cliente]
        ESC[Escalamiento a Ejecutivo]
    end

    C -->|consulta| A
    A -->|contexto| M2
    M2 -->|recupera| A
    A -->|analiza| R
    R -->|intención + complejidad| P
    P -->|plan de pasos| A
    A -->|busca info| T1
    T1 -->|query semántica| EMB
    EMB -->|embedding| DB
    DB -->|chunks relevantes| T1
    DOCS -->|indexado| DB
    T1 -->|datos + fuentes| A
    A -->|genera texto| T2
    T2 -->|usa| LLM
    R -->|valida guardrails| A
    A -->|guarda| M1
    A -->|resume| M2
    A -->|respuesta| RES
    R -->|requiere escalamiento| ESC
```

## Flujo de Trabajo del Agente (Secuencia)

```mermaid
sequenceDiagram
    participant Cliente
    participant Orquestador as Orquestador Agente
    participant Razonador as Tool Razonamiento
    participant Planificador as Planificador
    participant Consulta as Tool Consulta (RAG)
    participant Redaccion as Tool Redacción
    participant MemoriaC as Memoria Corto Plazo
    participant MemoriaL as Memoria Largo Plazo
    participant FAISS as FAISS Vector Store

    Cliente->>Orquestador: Envía consulta
    Orquestador->>MemoriaL: Recuperar contexto previo
    MemoriaL-->>Orquestador: Contexto relevante
    Orquestador->>Razonador: Clasificar intención
    Razonador-->>Orquestador: Intención + ¿escalar?

    alt Requiere Escalamiento
        Orquestador->>Cliente: Respuesta de escalamiento
    else Puede Resolver Autónomamente
        Orquestador->>Planificador: Generar plan de tareas
        Planificador-->>Orquestador: Lista de pasos

        loop Por cada paso del plan
            alt Paso = Consultar documentos
                Orquestador->>Consulta: Ejecutar RAG
                Consulta->>FAISS: Búsqueda semántica
                FAISS-->>Consulta: Chunks relevantes
                Consulta-->>Orquestador: Información + fuentes
            else Paso = Redactar respuesta
                Orquestador->>Redaccion: Generar respuesta formal
                Redaccion-->>Orquestador: Texto final
            end
        end

        Orquestador->>Razonador: Validar guardrails
        Razonador-->>Orquestador: ¿Válida? + corrección
        Orquestador->>MemoriaC: Guardar interacción
        Orquestador->>MemoriaL: Almacenar resumen
        Orquestador->>Cliente: Respuesta final
    end
```

## Diagrama de Estados del Agente

```mermaid
stateDiagram-v2
    [*] --> RecibirConsulta
    RecibirConsulta --> RecuperarContexto : Memoria largo plazo
    RecuperarContexto --> ClasificarIntencion : Tool razonamiento
    
    ClasificarIntencion --> PlanificarTareas : Complejidad = compleja
    ClasificarIntencion --> EjecutarSimple : Complejidad = simple
    
    PlanificarTareas --> EjecutarPaso : Plan generado
    EjecutarPaso --> EjecutarPaso : Siguiente paso
    EjecutarPaso --> AjustarPlan : Paso falla
    AjustarPlan --> EjecutarPaso : Plan corregido
    EjecutarPaso --> ValidarGuardrails : Último paso
    EjecutarSimple --> ValidarGuardrails : Info obtenida
    
    ValidarGuardrails --> RedactarRespuesta : Válida
    ValidarGuardrails --> CorregirRespuesta : Inválida
    CorregirRespuesta --> RedactarRespuesta : Corregida
    
    RedactarRespuesta --> AlmacenarMemoria : Guardar historial
    AlmacenarMemoria --> EntregarRespuesta : Listo
    EntregarRespuesta --> [*]
    
    ClasificarIntencion --> EscalarEjecutivo : Requiere escalamiento
    EscalarEjecutivo --> AlmacenarMemoria : Guardar historial
```

## Relación entre Componentes y Flujo de Trabajo

| Componente | Rol en el flujo de trabajo automatizado |
|-----------|------------------------------------------|
| **Orquestador** | Recibe la consulta, coordina la secuencia de tools y memoria, y entrega la respuesta final. Es el cerebro del flujo. |
| **Tool Razonamiento** | Filtra y clasifica antes de actuar. Decide si el agente puede resolver solo o si debe escalarse. Reduce riesgo operacional. |
| **Planificador** | Permite que el agente no se 'pierda' ante consultas complejas. Divide el problema en pasos manejables, como haría un operador humano. |
| **Tool Consulta (RAG)** | Garantiza que las respuestas se basen en documentos reales de CargaMax, no en conocimiento genérico del LLM. Mitiga alucinaciones. |
| **Tool Redacción** | Estandariza el tono y formato de las respuestas, manteniendo la imagen institucional sin depender de la variabilidad del LLM. |
| **Memoria Corto Plazo** | Mantiene coherencia dentro de una misma conversación. Permite preguntas de seguimiento como "¿y con express?" sin repetir contexto. |
| **Memoria Largo Plazo** | Personaliza la atención entre sesiones. Un cliente recurrente no debe repetir sus preferencias cada vez que contacta. |
| **FAISS** | Almacena tanto el corpus documental (RAG) como los resúmenes de memoria. Unifica la infraestructura de recuperación semántica localmente sin dependencias de servicios cloud. |
| **Groq (LLM)** | Provee la capacidad de lenguaje para todas las tools: entender consultas, generar texto, razonar sobre decisiones. |

