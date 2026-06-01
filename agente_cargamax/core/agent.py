import json
import os
from typing import Dict, Optional
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from agente_cargamax.config import config
from agente_cargamax.memory.conversacional import MemoriaCortoPlazo
from agente_cargamax.memory.semantica import MemoriaLargoPlazo
from agente_cargamax.planner.planificador import PlanificadorTareas
from agente_cargamax.tools.documentos import consultar_documentos
from agente_cargamax.tools.redaccion import redactar_respuesta
from agente_cargamax.tools.razonador import razonador_tool

class AgenteCargaMax:
    """Agente orquestador principal de CargaMax Sur Ltda.
    
    Integra tools de consulta, escritura y razonamiento,
    memoria de corto y largo plazo, y planificación de tareas
    para atender consultas B2B de forma adaptativa.
    """
    
    def __init__(self, cliente_id: Optional[str] = None):
        self.cliente_id = cliente_id or "anonimo"
        self.memoria_corto = MemoriaCortoPlazo(max_turnos=config.MAX_HISTORIA_CONVERSACION)
        self.memoria_largo = MemoriaLargoPlazo()
        self.planificador = PlanificadorTareas()
        self.llm = ChatGroq(
            model=config.MODELO_LLM,
            groq_api_key=config.GROQ_API_KEY,
            temperature=0.2
        )
        
        # Flag para ejecución sin API (modo simulación)
        self.modo_simulacion = not config.GROQ_API_KEY
    
    def procesar_consulta(self, consulta: str) -> Dict:
        """Procesa una consulta del cliente end-to-end.
        
        Retorna un diccionario con:
        - respuesta_final: str
        - accion: "responder" | "escalar"
        - metadata: dict con pasos ejecutados, fuentes, decisiones
        """
        if self.modo_simulacion:
            return self._procesar_modo_simulacion(consulta)
        
        # 1. Recuperar contexto de memoria a largo plazo
        contexto_memoria = self.memoria_largo.obtener_contexto_texto(
            consulta, self.cliente_id
        )
        
        # 2. Razonar: clasificar intención y decidir acción
        decision = razonador_tool.clasificar_y_decidir(consulta, contexto_memoria)
        
        # 3. Si requiere escalamiento, preparar respuesta de escalamiento
        if decision.get("requiere_escalamiento", False):
            respuesta_escalamiento = self._generar_respuesta_escalamiento(decision)
            self._guardar_interaccion(consulta, respuesta_escalamiento)
            return {
                "respuesta_final": respuesta_escalamiento,
                "accion": "escalar",
                "metadata": {
                    "decision": decision,
                    "pasos_ejecutados": ["clasificacion", "escalamiento"],
                    "fuentes": []
                }
            }
        
        # 4. Planificar tareas
        plan = self.planificador.generar_plan(
            consulta,
            decision.get("intencion", "otro"),
            contexto_memoria
        )
        
        # 5. Ejecutar plan paso a paso
        resultados_pasos = []
        informacion_acumulada = ""
        
        for paso in plan:
            tool = paso.get("tool", "")
            accion = paso.get("accion", "")
            
            if tool == "consultar_documentos":
                resultado = consultar_documentos(accion)
                informacion_acumulada += f"\n{resultado}"
                resultados_pasos.append({"paso": paso["paso"], "tool": tool, "resultado": resultado})
            
            elif tool == "redactar_respuesta":
                # Solo ejecutar al final del plan
                if paso == plan[-1]:
                    break
                else:
                    resultados_pasos.append({"paso": paso["paso"], "tool": tool, "resultado": "Pendiente"})
            
            elif tool == "razonar_y_decidir":
                # Validación intermedia
                val = razonador_tool.validar_limites_respuesta(informacion_acumulada)
                resultados_pasos.append({"paso": paso["paso"], "tool": tool, "resultado": val})
        
        # 6. Redactar respuesta final
        respuesta_final = redactar_respuesta(informacion_acumulada, tipo="consulta_general")
        
        # 7. Validar guardrails
        validacion = razonador_tool.validar_limites_respuesta(respuesta_final)
        if not validacion.get("valida", True):
            respuesta_final = validacion.get("respuesta_corregida", respuesta_final)
        
        # 8. Guardar en memorias
        self._guardar_interaccion(consulta, respuesta_final)
        
        # Extraer fuentes de los resultados
        fuentes = []
        for r in resultados_pasos:
            if r["tool"] == "consultar_documentos" and "Fuentes:" in r["resultado"]:
                partes = r["resultado"].split("Fuentes:")
                if len(partes) > 1:
                    fuentes.append(partes[1].strip())
        
        return {
            "respuesta_final": respuesta_final,
            "accion": "responder",
            "metadata": {
                "decision": decision,
                "plan": plan,
                "pasos_ejecutados": resultados_pasos,
                "fuentes": list(set(fuentes)),
                "validacion_guardrails": validacion
            }
        }
    
    def _guardar_interaccion(self, consulta: str, respuesta: str):
        """Guarda la interacción en ambas memorias."""
        # Memoria corto plazo
        self.memoria_corto.agregar_interaccion(consulta, respuesta)
        
        # Memoria largo plazo (resumen simple)
        resumen = f"Cliente preguntó: {consulta[:100]}... Agente respondió: {respuesta[:100]}..."
        self.memoria_largo.almacenar_interaccion(
            self.cliente_id,
            resumen,
            metadata={"tipo_consulta": "general"}
        )
    
    def _generar_respuesta_escalamiento(self, decision: Dict) -> str:
        """Genera un mensaje cordial indicando que se escalará a un ejecutivo."""
        motivo = decision.get("motivo_escalamiento", "Requiere atención especializada.")
        return (
            f"Estimado cliente, agradecemos su consulta. "
            f"Hemos identificado que esta solicitud requiere atención personalizada de un ejecutivo de cuentas: {motivo}\n\n"
            f"Un representante se contactará con usted dentro de las primeras 4 horas del siguiente día hábil. "
            f"Horario de atención: Lunes a Viernes 08:30 - 18:00, Sábados 09:00 - 13:00."
        )
    
    def _procesar_modo_simulacion(self, consulta: str) -> Dict:
        """Modo fallback cuando no hay API key configurada.
        Muestra el flujo y estructura sin consumir tokens."""
        return {
            "respuesta_final": (
                "[MODO SIMULACIÓN] No se detectó GROQ_API_KEY.\n\n"
                "Flujo que se ejecutaría:\n"
                "1. Clasificación de intención y decisión de escalamiento.\n"
                "2. Planificación de subtareas según complejidad.\n"
                "3. Consulta RAG sobre documentos de CargaMax.\n"
                "4. Redacción de respuesta con guardrails.\n"
                "5. Validación final y almacenamiento en memoria.\n\n"
                "Configure la variable de entorno GROQ_API_KEY para ejecutar con LLM real."
            ),
            "accion": "responder",
            "metadata": {
                "modo": "simulacion",
                "consulta_recibida": consulta
            }
        }

