import chromadb
import uuid
import logging
from typing import List, Dict
# ייבוא הפונקציה בלבד משכבת ה-Infrastructure של OpenAI
from app.infrastructure.openai_client import get_embedding

# הגדרת לוגר למעקב אחרי פעולות מסד הנתונים
logger = logging.getLogger("VectorStore")


class VectorStoreManager:
    def __init__(self, db_path: str = "./sentinel_db"):
        """אתחול מסד הנתונים הוקטורי ChromaDB"""
        try:
            self.client = chromadb.PersistentClient(path=db_path)
            self.collection = self.client.get_or_create_collection(
                name="sentinel_docs",
                metadata={"hnsw:space": "cosine"}  # שימוש במרחק קוסינוס לדיוק מירבי בחיפוש סמנטי
            )
            logger.info("ChromaDB initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

    async def add_documents(self, chunks: list[str], filename: str):
        """שמירת מסמכים עם מניעת כפילויות"""
        try:
            # בדיקה אם הקובץ כבר קיים ב-DB
            existing = self.collection.get(where={"source": filename})
            if existing and existing.get('ids') and len(existing['ids']) > 0:
                logger.info(f"הקובץ {filename} כבר קיים. מדלג על שמירה כפולה.")
                return

            ids = [str(uuid.uuid4()) for _ in chunks]
            metadatas = [{"source": filename} for _ in chunks]
            embeddings = [await get_embedding(chunk) for chunk in chunks]

            self.collection.add(
                documents=chunks,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )
            logger.info(f"נשמרו {len(chunks)} קטעים חדשים עבור {filename}")
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
    async def search(self, query: str, filename: str = None, n_results: int = 3) -> Dict:
        """
        חיפוש סמנטי עם אפשרות לסינון לפי קובץ ספציפי
        """
        try:
            query_embed = await get_embedding(query)

            # הגדרת תנאי סינון (Metadata filtering)
            search_params = {
                "query_embeddings": [query_embed],
                "n_results": n_results
            }

            # אם הועבר שם קובץ, נבצע סינון קשיח
            if filename:
                search_params["where"] = {"source": filename}

            results = self.collection.query(**search_params)

            sources = list(set([m["source"] for m in results["metadatas"][0]])) if results["metadatas"] else []
            context = " ".join(results["documents"][0]) if results["documents"] else ""

            return {
                "context": context,
                "sources": sources
            }
        except Exception as e:
            logger.error(f"Search query failed: {e}")
            return {"context": "", "sources": []}

# יצירת המופע (Instance) לשימוש בכל חלקי האפליקציה
# התיקון כאן: האובייקט נוצר לאחר הגדרת המחלקה וללא ייבוא מעגלי
vector_store = VectorStoreManager()