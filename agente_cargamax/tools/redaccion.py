from typing import Dict
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from agente_cargamax.config import config

class ToolRedaccion:
    """Tool de escritura: genera respuestas formales y estructuradas para clientes B2B."""
    
    def __init__(self):
        self.llm = ChatGroq(
            model=config.MODELO_LLM,
            groq_api_key=config.GROQ_API_KEY,
            temperature=0.4  # Ligeramente creativo pero controlado
        )
        
        self.system_prompt = (
            "Eres un redactor profesional de CargaMax Sur Ltda. "
            "Tu tarea es transformar información técnica y operacional en respuestas claras, "
            "cordiales y estructuradas para clientes B2B. "
            "Usa español neutro y profesional. "
            "Incluye saludos cordiales y cierres apropiados. "
            "Nunca prometas disponibilidad real ni valores definitivos sin confirmación."
        )
    
    def redactar_respuesta(self, informacion: str, tipo: str = "consulta_general") -> str:
        """Redacta una respuesta basada en información recuperada.
        
        Args:
            informacion: El contenido técnico/operacional a comunicar.
            tipo: Tipo de comunicación (consulta_general, escalamiento, resumen, email).
        """
        prompt_especializado = f"""
Redacta una respuesta de tipo '{tipo}' para un cliente B2B de CargaMax Sur Ltda.

INFORMACIÓN TÉCNICA A COMUNICAR:
{informacion}

INSTRUCCIONES:
- Saluda de forma cordial.
- Presenta la información de manera clara y estructurada.
- Si es necesario, indica que los valores son referenciales y sujetos a confirmación formal.
- Cierra ofreciendo ayuda adicional.
- No inventes datos que no estén en la información proporcionada.
"""
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt_especializado)
        ]
        
        respuesta = self.llm.invoke(messages)
        return respuesta.content
    
    def redactar_resumen(self, puntos_clave: list) -> str:
        """Genera un resumen estructurado a partir de puntos clave."""
        puntos_texto = "\n".join([f"- {p}" for p in puntos_clave])
        prompt = f"""
Genera un resumen ejecutivo para un cliente B2B basado en los siguientes puntos:

{puntos_texto}

El resumen debe ser breve (máximo 3 párrafos), profesional y en español neutro.
"""
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        respuesta = self.llm.invoke(messages)
        return respuesta.content

# Instancia singleton
redaccion_tool = ToolRedaccion()

def redactar_respuesta(informacion: str, tipo: str = "consulta_general") -> str:
    """Función wrapper para LangChain Tool."""
    return redaccion_tool.redactar_respuesta(informacion, tipo)

def redactar_resumen(puntos_clave: list) -> str:
    """Función wrapper para LangChain Tool."""
    return redaccion_tool.redactar_resumen(puntos_clave)

