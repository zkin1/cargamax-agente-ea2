# Informe Técnico: Evaluación Parcial 2
## Agente Funcional de Atención al Cliente B2B — CargaMax Sur Ltda.

**Curso:** ISY0101 — Optativo Ingeniería de Soluciones con IA  
**Entrega:** Evaluación Parcial N°2  
**Organización:** CargaMax Sur Ltda. (continuación del proyecto EP1)

## 1. Resumen Ejecutivo

Este informe documenta la implementación funcional del agente de atención al cliente diseñado en la Evaluación Parcial 1 para CargaMax Sur Ltda., empresa de transporte de carga B2B.

En la EP1 se entregó un diseño teórico que proponía un Router Agent con pipeline RAG, guardrails de seguridad y protocolos de escalamiento humano. En esta EP2 se construye el agente real: un sistema funcional que integra herramientas de consulta, escritura y razonamiento usando LangChain, con memoria de corto y largo plazo, planificación de tareas multipaso y validación de guardrails.

El resultado es un agente capaz de responder consultas operacionales autónomamente, mantener coherencia en conversaciones prolongadas, recordar contexto entre sesiones, y decidir inteligentemente cuándo debe transferir la atención a un ejecutivo humano.

## Mapeo a la Rúbrica de Evaluación

A continuación se detalla cómo cada indicador de evaluación (IE) de la Evaluación Parcial 2 se satisface en este proyecto:

| Indicador | Descripción de la rúbrica | Evidencia en este proyecto | Ponderación |
|-----------|---------------------------|---------------------------|-------------|
| **IE1** | Configura las herramientas dentro del agente, asegurando que ejecute funciones específicas con autonomía. | Tres tools implementadas y operativas: consulta RAG (`tools/documentos.py`), redacción de respuestas (`tools/redaccion.py`) y razonamiento con clasificación de intención (`tools/razonador.py`). El orquestador las invoca de forma autónoma según el plan generado. | 10% |
| **IE2** | Integra frameworks adecuados para el desarrollo del agente, garantizando su escalabilidad y compatibilidad técnica. | Stack validado: LangChain 0.3.x para orquestación, Groq API para inferencia de Llama 3.3 70B, FAISS para vector store local, HuggingFace MiniLM para embeddings. Todos con bindings oficiales y compatibilidad probada. | 10% |
| **IE3** | Configura procesos de memoria de contenido para un agente, asegurando la continuidad de tareas en flujos prolongados. | `memory/conversacional.py` implementa `ConversationBufferMemory` de LangChain, manteniendo el historial de intercambios dentro de una sesión. Demostrado en `tests/demo_memoria.py` con una conversación de 5 turnos. | 10% |
| **IE4** | Configura procesos de recuperación de contexto semántico para un agente, asegurando la continuidad de tareas en flujos prolongados. | `memory/semantica.py` almacena resúmenes de interacciones en una colección vectorial FAISS separada. Permite recuperar contexto de sesiones anteriores por similitud semántica, demostrado en `tests/demo_memoria.py`. | 10% |
| **IE5** | Diseña esquemas de planificación de tareas, para secuenciar las actividades del agente según prioridades. | `planner/planificador.py` descompone consultas complejas en pasos secuenciales con dependencias explícitas. Ejemplo real: la consulta sobre Puerto Montt se descompone en 4 pasos (tarifa, tiempo, frecuencia, redacción). | 10% |
| **IE6** | Demuestra mediante ejemplos la toma de decisiones del agente, garantizando que su comportamiento responda a las condiciones del entorno automatizado. | `tests/demo_decisiones.py` ejecuta 5 escenarios distintos: consulta simple, consulta compleja, cotización formal (escala), reclamo (escala) y carga peligrosa sin documentación (escala). Cada uno muestra la decisión adaptativa del agente. | 10% |
| **IE7** | Elabora un diagrama de orquestación de componentes y un archivo README en un repositorio github, describiendo la arquitectura general del agente. | `docs/diagrama_arquitectura.md` contiene diagramas Mermaid de arquitectura, flujo secuencial, estados y relación componente-flujo. `README.md` describe la arquitectura, instalación, ejecución y estructura del repositorio. | 10% |
| **IE8** | Justifica la elección de componentes en el diseño del agente, demostrando alineación entre herramientas y requerimientos del flujo de trabajo. | Sección 5.2 del informe justifica cada tecnología según las necesidades operativas de CargaMax: LangChain (falta de equipo ML dedicado), Groq (costo/acceso desde Chile), FAISS (corpus pequeño, local), memoria dual (flujo B2B real). | 10% |
| **IE9** | Elabora un informe técnico, que incluye diagramas y flujos de trabajo, respaldando las decisiones de diseño con documentación. | Este informe (`Informe_EA2.md`) integra diagramas, flujos de trabajo (`docs/ejemplos_flujo.md`), justificaciones técnicas y evidencias de ejecución. Lista completa de referencias en formato APA al final. | 10% |
| **IE10** | Utiliza en el informe un lenguaje técnico, argumentando sus respuestas con respaldado en evidencias y/o ejemplos concretos. | Todo el informe utiliza terminología técnica precisa (RAG, vector store, embeddings, guardrails, HITL). Las afirmaciones se respaldan con fragmentos de código, salidas de demos ejecutadas y referencias bibliográficas. | 10% |

Además, los cuatro indicadores de logro (IL) del curso se satisfacen de la siguiente manera:

- **IL2.1**: Construye agentes funcionales integrando tools de consulta, escritura y razonamiento → IE1 + IE2.
- **IL2.2**: Configura memoria y recuperación de contexto para continuidad en flujos prolongados → IE3 + IE4.
- **IL2.3**: Implementa estrategias de planificación y toma de decisiones adaptativas → IE5 + IE6.
- **IL2.4**: Documenta diseño e implementación con diagramas de orquestación → IE7 + IE8 + IE9 + IE10.

## 2. Diseño e Implementación del Agente

### 2.1. Arquitectura General

El agente sigue una arquitectura modular desacoplada, separando claramente las responsabilidades de orquestación, herramientas, memoria y planificación. Esta separación facilita el mantenimiento, la prueba unitaria de cada componente y la eventual escalabilidad del sistema.
![[Pasted image 20260531194635.png]]

El **Orquestador Principal** (`core/agent.py`) es el punto de entrada único. Recibe la consulta del cliente, coordina la secuencia de operaciones y entrega la respuesta final. No contiene lógica de negocio específica; solo orquesta.

### 2.2. Frameworks y Herramientas (IE1, IE2)

**LangChain** se eligió como framework principal porque es el estándar de facto en Python para construir aplicaciones con LLMs. Ofrece abstracciones maduras para agentes, memoria, retrieval y tools, con documentación extensa y una comunidad activa que garantiza compatibilidad técnica a largo plazo.

**Groq** provee la inferencia del modelo de lenguaje. Se usa Llama 3 70B a través de la API de Groq, que ofrece latencia ultrabaja y un tier gratuito generoso. Esto elimina la necesidad de infraestructura propia de GPU mientras se mantienen modelos open-source robustos. La alternativa a APIs pagas de OpenAI hace el proyecto reproducible académicamente sin costos.

**FAISS** funciona como vector store tanto para el corpus documental del RAG como para la memoria semántica de largo plazo. Se eligió porque opera localmente (sin cuentas cloud), tiene persistencia nativa en disco, e integración directa con LangChain. Para el MVP de CargaMax es más que suficiente; si en el futuro la empresa necesita escalar a millones de vectores, la migración a Pinecone o Weaviate es directa porque LangChain abstrae la capa de vector store.

**HuggingFace Embeddings** (`all-MiniLM-L6-v2`) genera los embeddings localmente sin consumir tokens de API, lo cual es eficiente económicamente y reduce dependencias externas para la capa de recuperación.

| Componente | Tecnología | Rol en el agente |
|-----------|-----------|------------------|
| Orquestación | LangChain | Agente, memoria, tools, chains |
| LLM | Groq (Llama 3 70B) | Razonamiento, generación de texto |
| Embeddings | HuggingFace MiniLM | Vectorización local sin costo |
| Vector Store | FAISS | RAG + memoria semántica persistente |

### 2.3. Las Tres Tools (IE1)

El agente expone tres herramientas que el orquestador invoca según el plan.

**Tool de Consulta (`tools/documentos.py`)**
Implementa RAG completo: carga los documentos mock de CargaMax (tarifario, términos, normativas ADR), los divide en chunks de 500 caracteres con overlap de 100, los indexa en FAISS, y responde preguntas usando `RetrievalQA` de LangChain. Retorna la respuesta junto con las fuentes documentales, permitiendo trazabilidad.

**Tool de Redacción (`tools/redaccion.py`)**
Recibe información técnica recuperada por la tool de consulta y la transforma en comunicaciones formales para clientes B2B. Incluye prompts especializados por tipo de comunicación (consulta general, escalamiento, resumen, email). Garantiza tono cordial, profesional y neutro.

**Tool de Razonamiento (`tools/razonador.py`)**
Es el módulo de control de calidad y router. Clasifica la intención del cliente en categorías (`informacional`, `cotizacion`, `reclamo`, `peligrosa`, `otro`), evalúa la complejidad (`simple` o `compleja`), y decide si la consulta puede resolverse autónomamente o debe escalarse. También valida que las respuestas generadas no violen guardrails de seguridad.

## 3. Memoria y Recuperación de Contexto

### 3.1. Memoria de Corto Plazo (IE3)

La memoria de corto plazo se implementa con `ConversationBufferMemory` de LangChain. Su función es mantener el hilo conversacional dentro de una misma sesión. Si un cliente pregunta "¿Cuánto cuesta a Valparaíso?" y luego "¿y con express?", el agente entiende que "express" modifica la consulta anterior, no es una pregunta nueva aislada.

El buffer mantiene los últimos intercambios como objetos `HumanMessage` y `AIMessage`, lo que permite inyectar el historial en los prompts del LLM para mantener coherencia referencial. Se limita a 10 turnos para evitar que los prompts crezcan indefinidamente.

### 3.2. Memoria de Largo Plazo (IE4)

La memoria de largo plazo resuelve un problema real de atención B2B: los clientes recurrentes no deberían tener que repetir su contexto cada vez que contactan. Se implementa como una colección vectorial separada dentro de FAISS.

Cada vez que finaliza una interacción, el orquestador genera un resumen breve y lo almacena con el `cliente_id` como metadata. Cuando ese mismo cliente vuelve a consultar, el sistema realiza una búsqueda semántica sobre los resúmenes previos y recupera los más relevantes para inyectarlos como contexto adicional.

Por ejemplo, si un cliente preguntó por tarifas a Puerto Montt la semana pasada y hoy pregunta "¿y cuáles eran los días de servicio?", el agente recupera el contexto previo y puede responder de forma personalizada sin pedirle que repita la ruta.
![[Pasted image 20260531194706.png|697]]

## 4. Planificación y Toma de Decisiones

### 4.1. Esquema de Planificación (IE5)

El `PlanificadorTareas` (`planner/planificador.py`) descompone consultas complejas en pasos secuenciales usando el LLM. Ante una consulta simple (una pregunta directa), genera un plan de 1-2 pasos. Ante una consulta compleja (múltiples datos entrelazados), genera 3-5 pasos con dependencias explícitas.

Ejemplo real generado por el planificador:

Consulta: *"Necesito enviar carga a Puerto Montt. ¿Cuánto cuesta, cuánto demora y qué días operan?"*

Plan generado:
1. Consultar tarifa por tonelada ruta Santiago-Puerto Montt.
2. Consultar tiempo estimado de tránsito ruta Santiago-Puerto Montt.
3. Consultar frecuencia de servicio ruta Santiago-Puerto Montt.
4. Redactar respuesta única integrando tarifa, tiempo y frecuencia.

Cada paso indica qué tool usar, lo que permite al orquestador ejecutarlos secuencialmente y acumular la información antes de redactar la respuesta final.

Si un paso falla (por ejemplo, no encuentra información en los documentos), el planificador puede ajustar el plan agregando un paso de búsqueda alternativa o un paso de escalamiento.

### 4.2. Toma de Decisiones Adaptativa (IE6)

La toma de decisiones no es un simple "if/else". El `ToolRazonador` usa el LLM para analizar la consulta en contexto y decidir la acción correcta. Esto permite manejar matices que un sistema basado en reglas rígidas no capturaría.

Se probaron cinco escenarios distintos para demostrar la adaptabilidad:

| Escenario | Intención detectada | Complejidad | Decisión | Justificación |
|-----------|---------------------|-------------|----------|---------------|
| "¿Tiempo a Valparaíso?" | informacional | simple | Responder autónomamente | Consulta directa resoluble con un documento. |
| "¿Tarifa, tiempo y frecuencia a Puerto Montt?" | informacional | compleja | Responder con plan multipaso | Requiere síntesis de múltiples fuentes. |
| "Cotización formal para 200 ton/mes" | cotizacion | compleja | Escalar a ejecutivo | Protocolo de CargaMax: volúmenes >100 ton/mes requieren ejecutivo. |
| "Reclamo formal por daño" | reclamo | simple | Escalar a ejecutivo | Reclamos son competencia exclusiva del área de seguros y ejecutivos. |
| "Solventes sin hoja de seguridad" | peligrosa | simple | Escalar + rechazo normativo | Carga peligrosa sin MSDS es inaceptable por normativa ADR. |

La decisión no depende solo de palabras clave. El razonador evalúa el conjunto de la consulta. Por ejemplo, "solventes" por sí solo podría ser informativo, pero "solventes sin hoja de seguridad" cambia completamente la decisión a rechazo normativo. Esta capacidad de adaptación ante condiciones cambiantes es la diferencia entre un chatbot estático y un agente funcional.

## 5. Documentación Técnica y Justificación

### 5.1. Diagrama de Orquestación y README (IE7)

El repositorio incluye un `README.md` completo con instrucciones precisas para instalar dependencias, configurar la API key de Groq y ejecutar el sistema. Además, la carpeta `docs/` contiene diagramas Mermaid de la arquitectura general, el flujo de trabajo secuencial, el diagrama de estados del agente y la relación entre componentes y flujo de trabajo automatizado.

El diagrama de estados muestra cómo el agente transita por fases definidas: recepción → recuperación de contexto → clasificación → planificación (o ejecución simple) → ejecución de pasos → validación → redacción → almacenamiento → entrega. Si un paso falla, el flujo puede devolverse a ajustar el plan sin perder el contexto acumulado.

### 5.2. Justificación de Componentes (IE8)

Cada componente fue elegido por su alineación con los requerimientos del flujo de trabajo de CargaMax:

**LangChain**: CargaMax no tiene un equipo de ML dedicado. Necesita un framework que abstraiga la complejidad de conectar LLMs, vector stores y memoria, permitiendo que el mantenimiento lo haga un desarrollador Python estándar.

**Groq + Llama 3**: La empresa opera en Chile y prefiere no depender de infraestructura propia ni de APIs costosas en dólares. Groq ofrece modelos de clase GPT-4 con latencia menor a 300ms y un tier gratuito que cubre el prototipado y la puesta en marcha inicial.

**FAISS**: Para una empresa con 5-10 documentos internos de referencia, una base vectorial local es suficiente. No se justifica el costo y la complejidad operativa de Pinecone o Weaviate en esta etapa. Si el corpus crece a cientos de documentos, la migración es trivial gracias a la abstracción de LangChain.

**HuggingFace MiniLM**: Generar embeddings consume muchos tokens si se hace por API. Un modelo local de 22MB que corre en CPU elimina ese costo recurrente y reduce la dependencia de conectividad externa.

**Memoria dual (corto + largo plazo)**: El flujo de trabajo de atención al cliente B2B se caracteriza por consultas de seguimiento y clientes recurrentes. Una solución con solo memoria conversacional no cubre la experiencia entre sesiones; una solución con solo memoria vectorial pierde el hilo inmediato de la conversación. Ambas son necesarias.

## 6. Pruebas y Evidencias de Funcionamiento

El proyecto incluye tres scripts de demostración ejecutables que evidencian el funcionamiento del agente:

### 6.1. Demo de Consultas (`tests/demo_consulta.py`)

Compara una consulta simple (tiempo de tránsito) contra una consulta compleja (tarifa + tiempo + frecuencia) y una consulta de carga peligrosa. Muestra cómo el RAG recupera información exacta de los documentos y cómo la decisión de escalamiento se activa automáticamente para la carga peligrosa.

### 6.2. Demo de Memoria (`tests/demo_memoria.py`)

Simula una conversación de 5 turnos para probar la memoria de corto plazo, mostrando cómo el historial se acumula. Luego simula una nueva sesión con el mismo `cliente_id`, recuperando el contexto de la sesión anterior mediante la memoria de largo plazo.

### 6.3. Demo de Decisiones (`tests/demo_decisiones.py`)

Ejecuta los 5 escenarios descritos en la sección 4.2, imprimiendo para cada uno: la intención detectada, la complejidad, la decisión de escalamiento, el motivo y la respuesta final. Esto demuestra de forma directa que el agente ajusta su comportamiento ante distintas condiciones.

### 6.4. Ejecución Principal (`main.py`)

Ejecuta 4 consultas de demostración predefinidas que recorren los casos más representativos del flujo de trabajo, mostrando la respuesta, la acción tomada y la metadata completa de cada interacción.

## 7. Reflexión y Conclusiones

Construir este agente a partir del diseño de la EP1 permitió comprender la distancia entre "dibujar una arquitectura" y "hacer que funcione". El diseño teórico era correcto en sus líneas generales, pero la implementación reveló detalles que solo aparecen al codear:

- Los **guardrails** no pueden quedar solo en el system prompt. Es necesario un módulo de validación explícito que revise la respuesta generada antes de entregarla al cliente. Un prompt bien escrito reduce la frecuencia de violaciones, pero no la elimina.
- La **memoria de largo plazo** es más valiosa de lo que parece en el papel. En la práctica, la diferencia entre un chatbot y un agente funcional es que el agente "aprende" de sus interacciones previas para personalizar la atención.
- El **planificador** es indispensable para consultas reales. Los clientes B2B no hacen una pregunta a la vez; hacen preguntas compuestas. Sin descomposición en pasos, el agente tiende a responder incompleto o a confundir datos de distintas fuentes.
- **LangChain agiliza mucho**, pero también abstrae comportamientos que hay que entender para debuggear. Aprender a leer los `runnable sequences` y los `agent traces` fue clave para identificar por qué el agente elegía una tool incorrecta en ciertos casos.

El agente cumple con los cuatro indicadores de logro de la evaluación:
- **IL2.1**: Integra tools de consulta (RAG), escritura (redacción) y razonamiento (router + validación) usando LangChain.
- **IL2.2**: Configura memoria de corto plazo (buffer conversacional) y largo plazo (recuperación semántica vectorial) para mantener continuidad.
- **IL2.3**: Implementa planificación de tareas multipaso y toma de decisiones adaptativa ante diferentes intenciones y condiciones.
- **IL2.4**: Este informe y los diagramas de orquestación documentan la relación entre cada componente y el flujo de trabajo automatizado.

## 8. Referencias

LangChain. (2024). *LangChain Documentation: Agents, Memory, and Retrieval*. Recuperado de https://python.langchain.com/docs/

Meta AI. (2024). *Llama 3 Model Card*. Recuperado de https://ai.meta.com/llama/

Groq, Inc. (2024). *GroqCloud Documentation*. Recuperado de https://console.groq.com/docs

FAISS. (2024). *Chroma Documentation*. Recuperado de https://docs.trychroma.com/

Ministerio de Transportes y Telecomunicaciones de Chile. (2023). *Normativa de transporte de cargas peligrosas por vía terrestre*. Recuperado de https://www.mtt.gob.cl/

Comisión Económica para América Latina y el Caribe (CEPAL). (2022). *Logística y transporte de mercancías peligrosas en América Latina*. Recuperado de https://www.cepal.org/

RAGAS. (2024). *RAGAS: Retrieval-Augmented Generation Assessment Suite*. Recuperado de https://docs.ragas.io/

Hugging Face. (2024). *Sentence-Transformers Documentation: all-MiniLM-L6-v2*. Recuperado de https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2

CargaMax Sur Ltda. (2024). *Tarifario Base 2024, Términos y Condiciones Generales, Protocolo de Carga Peligrosa*. Documentos internos (datos simulados para fines académicos).

