import os
from typing import List, Optional
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from agente_cargamax.config import config

class MemoriaLargoPlazo:
    """Memoria de largo plazo: recuperación semántica de interacciones pasadas.
    
    Almacena resúmenes de conversaciones anteriores en una colección
    vectorial separada, permitiendo al agente 'recordar' preferencias
    y contexto de clientes recurrentes.
    """
    
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name=config.MODELO_EMBEDDINGS)
        self.faiss_dir = os.path.join(config.FAISS_DIR, "memoria_largo_plazo")
        
        # Inicializar o cargar el vector store
        faiss_index = os.path.join(self.faiss_dir, "index.faiss")
        if os.path.exists(faiss_index):
            self.vectorstore = FAISS.load_local(
                self.faiss_dir, self.embeddings, allow_dangerous_deserialization=True
            )
        else:
            # Crear vacío inicialmente
            self.vectorstore = None
    
    def almacenar_interaccion(self, cliente_id: str, resumen: str, metadata: Optional[dict] = None):
        """Almacena un resumen de interacción en la memoria semántica.
        
        Args:
            cliente_id: Identificador único del cliente (ej. email, RUT).
            resumen: Texto resumido de la interacción.
            metadata: Datos adicionales (fecha, tipo de consulta, etc.).
        """
        meta = metadata or {}
        meta["cliente_id"] = cliente_id
        meta["tipo"] = "resumen_interaccion"
        
        doc = Document(page_content=resumen, metadata=meta)
        
        if self.vectorstore is None:
            self.vectorstore = FAISS.from_documents(
                documents=[doc],
                embedding=self.embeddings
            )
        else:
            self.vectorstore.add_documents([doc])
        
        os.makedirs(self.faiss_dir, exist_ok=True)
        self.vectorstore.save_local(self.faiss_dir)
    
    def recuperar_contexto_relevante(self, consulta: str, cliente_id: Optional[str] = None, k: int = 3) -> List[Document]:
        """Recupera interacciones pasadas relevantes para la consulta actual.
        
        Si se proporciona cliente_id, filtra por ese cliente para
        personalizar la recuperación.
        """
        if self.vectorstore is None:
            return []
        
        filter_dict = None
        if cliente_id:
            filter_dict = {"cliente_id": cliente_id}
        
        try:
            resultados = self.vectorstore.similarity_search(
                consulta,
                k=k,
                filter=filter_dict
            )
            return resultados
        except Exception:
            # Fallback sin filtro si hay problemas
            return self.vectorstore.similarity_search(consulta, k=k)
    
    def obtener_contexto_texto(self, consulta: str, cliente_id: Optional[str] = None) -> str:
        """Recupera y formatea el contexto relevante como texto."""
        docs = self.recuperar_contexto_relevante(consulta, cliente_id)
        if not docs:
            return "No hay contexto previo relevante."
        
        partes = []
        for i, doc in enumerate(docs, 1):
            partes.append(f"[Interacción anterior {i}]: {doc.page_content}")
        
        return "\n\n".join(partes)

