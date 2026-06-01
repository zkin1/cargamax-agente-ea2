# Agente CargaMax - Atencion al Cliente B2B

Agente funcional para CargaMax Sur Ltda., desarrollado como parte del curso ISY0101 - Optativo Ingenieria de Soluciones con IA.

## Que hace este agente

- **Consulta** documentos internos (tarifario, terminos, normativas) usando RAG
- **Redacta** respuestas formales para clientes B2B
- **Razona** para decidir si responde autonomamente o escala a un ejecutivo humano
- **Recuerda** el contexto de conversaciones anteriores (memoria corto y largo plazo)
- **Planifica** pasos secuenciales para consultas complejas

## Stack tecnico

- **LangChain** - Orquestacion de agentes
- **Groq API** - LLM Llama 3.3 70B
- **FAISS** - Vector store local
- **HuggingFace** - Embeddings MiniLM

## Instalacion

```bash
pip install -r requirements.txt
```

Crear archivo `.env` en la raiz con:
```
GROQ_API_KEY=tu_clave_aqui
```

## Ejecucion

Demo principal (4 consultas de ejemplo):
```bash
python main.py
```

Demos individuales:
```bash
# Consulta simple vs compleja
python tests/demo_consulta.py

# Memoria corto y largo plazo
python tests/demo_memoria.py

# Decisiones adaptativas (5 escenarios)
python tests/demo_decisiones.py
```

## Estructura del proyecto

```
agente_cargamax/
  core/agent.py          # Orquestador principal
  tools/
    documentos.py         # Tool de consulta RAG
    redaccion.py          # Tool de redaccion
    razonador.py          # Tool de razonamiento
  memory/
    conversacional.py     # Memoria corto plazo
    semantica.py          # Memoria largo plazo
  planner/
    planificador.py       # Planificacion de tareas
  data/
    tarifario_2024.txt    # Documentos mock de CargaMax
    terminos_generales.txt
    normativas_adr.txt

tests/                    # Demos ejecutables
docs/                     # Diagramas y flujos
main.py                   # Punto de entrada
requirements.txt          # Dependencias
Informe_EA2.md            # Informe tecnico completo
```

## Guardrails de seguridad

- No garantiza disponibilidad de flota en tiempo real
- No emite cotizaciones vinculantes sin confirmacion
- Escalado automatico a ejecutivo ante cotizaciones formales, reclamos o carga peligrosa

## Documentacion adicional

- `docs/diagrama_arquitectura.md` - Diagramas de arquitectura
- `docs/ejemplos_flujo.md` - Casos de uso paso a paso
- `Informe_EA2.md` - Informe tecnico completo con justificaciones

Proyecto academico - ISY0101.
