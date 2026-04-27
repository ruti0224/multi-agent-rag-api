import chromadb
import uuid
import logging
import os
from typing import List, Dict
from sentence_transformers import SentenceTransformer

# הגדרת לוגים מקצועית
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("VectorStore")


class VectorDBManager:
    """
    ניהול מסד נתונים וקטורי מבוסס ChromaDB.
    המחלקה מרכזת את כל פעולות ה-RAG: חיתוך, וקטוריזציה, אחסון וחיפוש.
    """

    def __init__(self, db_path: str = "./sentinel_db", collection_name: str = "sentinel_knowledge"):
        try:
            if not os.path.exists(db_path):
                os.makedirs(db_path)
            self.client = chromadb.PersistentClient(path=db_path)
            logger.info("Initializing SentenceTransformer model...")
            self.model = SentenceTransformer('./local_model')
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=self.embedding_wrapper
            )
            logger.info(f"VectorDB initialized: {collection_name}")
        except Exception as e:
            logger.error(f"VectorDB initialization failed: {str(e)}")
            raise

    def embedding_wrapper(self, input_texts: List[str]) -> List[List[float]]:
        """עטיפה שמחברת בין ChromaDB למודל ה-SentenceTransformer"""
        embeddings = self.model.encode(input_texts)
        return embeddings.tolist()

    def _smart_chunking(self, text: str, chunk_size: int, overlap: int = 100) -> List[str]:
        paragraphs = text.split('\n')
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) <= chunk_size:
                current_chunk += para + "\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n"

        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks
    def process_and_store(self, text: str, chunk_size: int = 600) -> Dict[str, any]:
        """עיבוד טקסט גולמי ואחסונו ב-DB"""
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty")

        try:
            chunks = self._smart_chunking(text, chunk_size)
            ids = [str(uuid.uuid4()) for _ in chunks]
            metadatas = [{"source": "document_upload", "chunk_index": i} for i in range(len(chunks))]

            self.collection.add(
                documents=chunks,
                ids=ids,
                metadatas=metadatas
            )
            logger.info(f"Successfully stored {len(chunks)} chunks.")
            return {"status": "success", "count": len(chunks)}
        except Exception as e:
            logger.error(f"Storage error: {str(e)}")
            raise

    def query_database(self, question: str, n_results: int = 3) -> str:
        """חיפוש סמנטי לקבלת הקשר (Context)"""
        if not question or not question.strip():
            return ""
        try:
            results = self.collection.query(query_texts=[question], n_results=n_results)
            if results and results.get("documents") and results["documents"][0]:
                return "\n---\n".join(results["documents"][0])
            return ""
        except Exception as e:
            logger.error(f"Query error: {str(e)}")
            return ""

    def clear_database(self):
        """ניקוי מסד הנתונים"""
        try:
            existing_ids = self.collection.get()["ids"]
            if existing_ids:
                self.collection.delete(ids=existing_ids)
                logger.info("Database cleared.")
        except Exception as e:
            logger.error(f"Clear error: {str(e)}")

vector_db = VectorDBManager()