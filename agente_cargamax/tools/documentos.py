from typing import List, Dict
import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
from agente_cargamax.config import config
import pickle

class ToolConsultaDocumentos:
    """Tool de consulta: RAG sobre documentos internos de CargaMax."""
    
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name=config.MODELO_EMBEDDINGS)
        self.vectorstore = None
        self.qa_chain = None
        self._inicializar_rag()
    
    def _inicializar_rag(self):
        """Carga documentos, los divide en chunks y construye el vector store."""
        documentos = []
        data_dir = config.DATA_DIR
        
        archivos = [f for f in os.listdir(data_dir) if f.endswith('.txt')]
        for archivo in archivos:
            ruta = os.path.join(data_dir, archivo)
            loader = TextLoader(ruta, encoding='utf-8')
            docs = loader.load()
            for doc in docs:
                doc.metadata["source"] = archivo
            documentos.extend(docs)
        
        # Dividir en chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP
        )
        chunks = text_splitter.split_documents(documentos)
        
        # Crear o cargar vector store persistente con FAISS
        faiss_path = os.path.join(config.FAISS_DIR, "index.faiss")
        if os.path.exists(faiss_path):
            self.vectorstore = FAISS.load_local(
                config.FAISS_DIR, self.embeddings, allow_dangerous_deserialization=True
            )
        else:
            self.vectorstore = FAISS.from_documents(
                documents=chunks,
                embedding=self.embeddings
            )
            os.makedirs(config.FAISS_DIR, exist_ok=True)
            self.vectorstore.save_local(config.FAISS_DIR)
        
        # Crear chain de QA con retrieval
        llm = ChatGroq(
            model=config.MODELO_LLM,
            groq_api_key=config.GROQ_API_KEY,
            temperature=0.1
        )
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": config.TOP_K_DOCUMENTOS}
            ),
            return_source_documents=True
        )
    
    def consultar(self, pregunta: str) -> Dict:
        """Consulta la base documental y retorna respuesta con fuentes."""
        if not self.qa_chain:
            return {
                "respuesta": "Error: sistema RAG no inicializado.",
                "fuentes": []
            }
        
        resultado = self.qa_chain.invoke({"query": pregunta})
        
        fuentes = []
        if "source_documents" in resultado:
            for doc in resultado["source_documents"]:
                fuente = doc.metadata.get("source", "desconocido")
                if fuente not in fuentes:
                    fuentes.append(fuente)
        
        return {
            "respuesta": resultado.get("result", "No se encontró información."),
            "fuentes": fuentes
        }

# Instancia singleton
consulta_tool = ToolConsultaDocumentos()

def consultar_documentos(pregunta: str) -> str:
    """Función wrapper para LangChain Tool."""
    resultado = consulta_tool.consultar(pregunta)
    fuentes_str = ", ".join(resultado["fuentes"]) if resultado["fuentes"] else "Sin fuente"
    return f"{resultado['respuesta']}\n\n[Fuentes: {fuentes_str}]"

