import json
from typing import Dict
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from agente_cargamax.config import config

class ToolRazonador:
    """Tool de razonamiento: clasifica intención, valida límites y decide acciones."""
    
    def __init__(self):
        self.llm = ChatGroq(
            model=config.MODELO_LLM,
            groq_api_key=config.GROQ_API_KEY,
            temperature=0.0  # Determinista para decisiones
        )
        
        self.system_prompt = (
            "Eres el módulo de razonamiento y control de calidad del agente de CargaMax Sur Ltda. "
            "Tu función es analizar la consulta del cliente y determinar la acción correcta. "
            "Responde SIEMPRE en formato JSON válido sin markdown ni comentarios."
        )
    
    def clasificar_y_decidir(self, consulta: str, contexto: str = "") -> Dict:
        """Analiza la consulta y devuelve una decisión estructurada.
        
        Retorna:
            {
                "intencion": "informacional | cotizacion | reclamo | peligrosa | otro",
                "complejidad": "simple | compleja",
                "requiere_escalamiento": true/false,
                "motivo_escalamiento": "texto explicativo si aplica",
                "plan_sugerido": ["paso 1", "paso 2", ...] (solo si complejidad=complex),
                "respuesta_directa_permitida": true/false
            }
        """
        prompt = f"""
Analiza la siguiente consulta de un cliente B2B de CargaMax Sur Ltda. y determina la acción correcta.

CONSULTA DEL CLIENTE:
{consulta}

CONTEXTO ADICIONAL:
{contexto}

REGLAS DE DECISIÓN:
1. Intención "informacional": consulta sobre tarifas, rutas, tiempos, documentación, normativas.
2. Intención "cotizacion": solicitud de precio formal, contrato, volumen mayor a lo habitual.
3. Intención "reclamo": queja por servicio, daño, pérdida, demora.
4. Intención "peligrosa": consulta sobre transporte de materiales peligrosos, químicos, combustibles.
5. Complejidad "simple": una sola pregunta directa que se responde con un documento.
6. Complejidad "compleja": múltiples preguntas entrelazadas o que requieren síntesis de varias fuentes.

ESCALAMIENTO OBLIGATORIO (requiere_escalamiento=true) SI:
- Es una cotización formal o solicitud de contrato.
- Es un reclamo formal.
- Es carga peligrosa sin documentación completa mencionada.
- El cliente solicita hablar con un ejecutivo humano.
- La consulta está fuera del alcance de los documentos internos conocidos.

Responde ÚNICAMENTE con un objeto JSON válido. No uses markdown, no expliques nada fuera del JSON.

Formato de respuesta:
{{
  "intencion": "...",
  "complejidad": "...",
  "requiere_escalamiento": boolean,
  "motivo_escalamiento": "...",
  "plan_sugerido": ["..."],
  "respuesta_directa_permitida": boolean
}}
"""
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        respuesta = self.llm.invoke(messages)
        contenido = respuesta.content.strip()
        
        # Limpiar posibles delimitadores markdown
        if contenido.startswith("```json"):
            contenido = contenido[7:]
        if contenido.startswith("```"):
            contenido = contenido[3:]
        if contenido.endswith("```"):
            contenido = contenido[:-3]
        contenido = contenido.strip()
        
        try:
            decision = json.loads(contenido)
        except json.JSONDecodeError:
            # Fallback seguro
            decision = {
                "intencion": "otro",
                "complejidad": "simple",
                "requiere_escalamiento": True,
                "motivo_escalamiento": "No se pudo analizar la consulta automáticamente. Se escala a ejecutivo humano.",
                "plan_sugerido": [],
                "respuesta_directa_permitida": False
            }
        
        return decision
    
    def validar_limites_respuesta(self, respuesta_generada: str) -> Dict:
        """Valida que la respuesta no viole guardrails del sistema."""
        prompt = f"""
Valida si la siguiente respuesta viola alguna regla del sistema de CargaMax Sur Ltda.

RESPUESTA A VALIDAR:
{respuesta_generada}

REGLAS A VERIFICAR:
1. ¿Garantiza disponibilidad de flota en tiempo real? (palabras como "garantizamos", "disponible ahora", "seguro que tenemos")
2. ¿Emite una cotización vinculante? (palabras como "cotizamos en", "precio final", "costo definitivo")
3. ¿Solicita datos sensibles como RUT, claves bancarias? (solo RUT es aceptable si el cliente lo ofrece voluntariamente)
4. ¿Es respetuosa y profesional?

Responde ÚNICAMENTE con JSON:
{{
  "valida": boolean,
  "violaciones": ["..."],
  "respuesta_corregida": "..." (si hay violaciones, corrige la respuesta manteniendo la información válida)
}}
"""
        messages = [
            SystemMessage(content=self.system_prompt),
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
            validacion = json.loads(contenido)
        except json.JSONDecodeError:
            validacion = {
                "valida": True,
                "violaciones": [],
                "respuesta_corregida": respuesta_generada
            }
        
        return validacion

# Instancia singleton
razonador_tool = ToolRazonador()

def razonar_y_decidir(consulta: str, contexto: str = "") -> str:
    """Función wrapper para LangChain Tool. Retorna JSON como string."""
    decision = razonador_tool.clasificar_y_decidir(consulta, contexto)
    return json.dumps(decision, ensure_ascii=False, indent=2)

def validar_limites(respuesta_generada: str) -> str:
    """Función wrapper para LangChain Tool. Retorna JSON como string."""
    validacion = razonador_tool.validar_limites_respuesta(respuesta_generada)
    return json.dumps(validacion, ensure_ascii=False, indent=2)

