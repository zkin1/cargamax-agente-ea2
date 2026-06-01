import os
from dotenv import load_dotenv

load_dotenv()

class ConfiguracionAgente:
    """Configuración central del agente CargaMax."""
    
    # API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Modelos Groq
    MODELO_LLM: str = "llama-3.3-70b-versatile"  # Alternativa: mixtral-8x7b-32768
    MODELO_EMBEDDINGS: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Rutas
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR: str = os.path.join(BASE_DIR, "agente_cargamax", "data")
    FAISS_DIR: str = os.path.join(BASE_DIR, "faiss_db")
    
    # Parámetros RAG
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100
    TOP_K_DOCUMENTOS: int = 3
    
    # Parámetros de memoria
    MAX_HISTORIA_CONVERSACION: int = 10
    
    # Guardrails del sistema (heredados de EP1)
    SYSTEM_PROMPT: str = (
        "Eres el Asistente Virtual de Atención al Cliente de CargaMax Sur Ltda. "
        "Tu rol es responder consultas operacionales y de logística de clientes B2B. "
        "Reglas estrictas: "
        "1. Usa SOLO la información recuperada de los documentos internos (RAG) para responder. "
        "2. NUNCA garantices disponibilidad de flota en tiempo real ni emitas cotizaciones vinculantes. "
        "3. Si la consulta involucra una cotización formal, contrato, reclamo o carga peligrosa sin documentación, DEBES escalar a un ejecutivo humano. "
        "4. Responde en español neutro, cordial y profesional. "
        "5. Cita siempre la fuente del documento cuando proporciones información."
    )

config = ConfiguracionAgente()

