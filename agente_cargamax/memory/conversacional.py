from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
from typing import List, Optional

class MemoriaCortoPlazo:
    """Memoria de corto plazo: mantiene el hilo conversacional actual.
    
    Usa ConversationBufferMemory de LangChain para recordar
    los últimos intercambios entre el cliente y el agente.
    """
    
    def __init__(self, max_turnos: int = 10):
        self.memory = ConversationBufferMemory(
            memory_key="historial_conversacion",
            return_messages=True,
            input_key="input",
            output_key="output"
        )
        self.max_turnos = max_turnos
    
    def agregar_interaccion(self, entrada_cliente: str, respuesta_agente: str):
        """Guarda un par entrada-salida en la memoria."""
        self.memory.save_context(
            {"input": entrada_cliente},
            {"output": respuesta_agente}
        )
    
    def obtener_historial(self) -> List:
        """Retorna el historial de mensajes como lista de objetos Message."""
        return self.memory.buffer if hasattr(self.memory, 'buffer') else []
    
    def obtener_historial_texto(self) -> str:
        """Retorna el historial como texto plano para inyección en prompts."""
        historial = self.obtener_historial()
        lineas = []
        for msg in historial:
            if isinstance(msg, HumanMessage):
                lineas.append(f"Cliente: {msg.content}")
            elif isinstance(msg, AIMessage):
                lineas.append(f"Agente: {msg.content}")
        return "\n".join(lineas)
    
    def limpiar(self):
        """Reinicia la memoria (por ejemplo, al finalizar una sesión)."""
        self.memory.clear()
    
    def resumir_si_necesario(self) -> str:
        """Si el historial es muy largo, retorna un resumen."""
        historial = self.obtener_historial()
        if len(historial) > self.max_turnos * 2:
            # Nota: en una implementación más avanzada se podría usar
            # ConversationSummaryMemory para resumir automáticamente.
            return f"[Historial extenso: {len(historial)//2} intercambios. Contexto resumido disponible.]"
        return self.obtener_historial_texto()

