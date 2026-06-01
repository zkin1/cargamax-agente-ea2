import json
from typing import List, Dict
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from agente_cargamax.config import config

class PlanificadorTareas:
    """Planificador: descompone consultas complejas en subtareas secuenciales.
    
    Permite al agente abordar consultas multipaso de forma estructurada,
    ejecutando cada tarea en orden y ajustando el plan si es necesario.
    """
    
    def __init__(self):
        self.llm = ChatGroq(
            model=config.MODELO_LLM,
            groq_api_key=config.GROQ_API_KEY,
            temperature=0.1
        )
    
    def generar_plan(self, consulta: str, intencion: str, contexto: str = "") -> List[Dict]:
        """Genera un plan de pasos para resolver una consulta compleja.
        
        Retorna una lista de diccionarios:
        [{"paso": 1, "accion": "...", "tool": "consulta|redaccion|razonamiento", "dependencia": null}, ...]
        """
        prompt = f"""
Eres el planificador de tareas del agente de CargaMax Sur Ltda.

CONSULTA DEL CLIENTE:
{consulta}

INTENCIÓN DETECTADA:
{intencion}

CONTEXTO ADICIONAL:
{contexto}

INSTRUCCIONES:
Descompón la consulta en pasos secuenciales. Cada paso debe indicar:
- qué información buscar o qué acción realizar,
- qué tool usar (consultar_documentos, redactar_respuesta, razonar_y_decidir).
- de qué paso depende (si es el primero, dependencia=null).

Si la consulta es SIMPLE (una sola pregunta directa), genera un plan de 1-2 pasos.
Si es COMPLEJA (múltiples preguntas o requiere síntesis), genera 3-5 pasos.

Responde ÚNICAMENTE con un array JSON válido. No uses markdown, no expliques nada fuera del JSON.

Formato:
[
  {{
    "paso": 1,
    "accion": "descripción de la acción",
    "tool": "nombre_tool",
    "dependencia": null
  }},
  {{
    "paso": 2,
    "accion": "descripción de la acción",
    "tool": "nombre_tool",
    "dependencia": 1
  }}
]
"""
        
        messages = [
            SystemMessage(content="Planificador de tareas del agente CargaMax. Responde solo JSON."),
            HumanMessage(content=prompt)
        ]
        
        respuesta = self.llm.invoke(messages)
        contenido = respuesta.content.strip()
        
        # Limpiar markdown
        if contenido.startswith("```json"):
            contenido = contenido[7:]
        if contenido.startswith("```"):
            contenido = contenido[3:]
        if contenido.endswith("```"):
            contenido = contenido[:-3]
        contenido = contenido.strip()
        
        try:
            plan = json.loads(contenido)
            if not isinstance(plan, list):
                plan = [plan] if isinstance(plan, dict) else []
        except json.JSONDecodeError:
            # Fallback: plan simple directo
            plan = [
                {"paso": 1, "accion": f"Consultar información sobre: {consulta}", "tool": "consultar_documentos", "dependencia": None},
                {"paso": 2, "accion": "Redactar respuesta al cliente", "tool": "redactar_respuesta", "dependencia": 1}
            ]
        
        return plan
    
    def ajustar_plan(self, plan_actual: List[Dict], paso_fallido: int, razon: str) -> List[Dict]:
        """Ajusta el plan si un paso falla o requiere modificación.
        
        Ejemplo: si no se encuentra información en un documento,
        el planificador puede agregar un paso de búsqueda alternativa
        o modificar el paso de redacción para indicar la limitación.
        """
        prompt = f"""
El siguiente plan de tareas falló en el paso {paso_fallido}.

PLAN ACTUAL:
{json.dumps(plan_actual, ensure_ascii=False, indent=2)}

RAZÓN DEL FALLO:
{razon}

Ajusta el plan para manejar esta situación. Puedes:
- Modificar pasos posteriores.
- Agregar pasos de búsqueda alternativa.
- Incluir un paso de escalamiento si no se puede resolver.

Responde ÚNICAMENTE con el nuevo array JSON de pasos.
"""
        
        messages = [
            SystemMessage(content="Planificador de tareas del agente CargaMax. Responde solo JSON."),
            HumanMessage(content=prompt)
        ]
        
        respuesta = self.llm.invoke(messages)
        contenido = respuesta.content.strip()
        
        if contenido.startswith("```json"):
            contenido = contenido[7:]
        if contenido.startswith("```"):
            contenido = contenido[3:]
        if contenido.endswith("```"):
            contenido = contenido[:-3]
        contenido = contenido.strip()
        
        try:
            plan_ajustado = json.loads(contenido)
            if not isinstance(plan_ajustado, list):
                plan_ajustado = plan_actual  # Mantener original si el parseo falla
        except json.JSONDecodeError:
            # Fallback: agregar paso de escalamiento
            plan_ajustado = plan_actual.copy()
            plan_ajustado.append({
                "paso": len(plan_ajustado) + 1,
                "accion": "Escalar a ejecutivo humano debido a información insuficiente",
                "tool": "razonar_y_decidir",
                "dependencia": paso_fallido
            })
        
        return plan_ajustado

