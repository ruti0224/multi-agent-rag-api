import io
from PyPDF2 import PdfReader
from typing import List


class FileProcessor:

    async def process_txt(content: bytes) -> List[str]:
        """עיבוד קובץ טקסט פשוט"""
        try:
            # פענוח הביטים לטקסט (UTF-8)
            text = content.decode("utf-8")
            return FileProcessor.create_chunks(text)
        except UnicodeDecodeError:
            # טיפול במקרה שהקובץ מקודד אחרת (כמו Windows-1255 לעברית)
            text = content.decode("iso-8859-8")
            return FileProcessor.create_chunks(text)
    @staticmethod
    async def process_pdf(file_content: bytes) -> List[str]:
        """הופך PDF לרשימה של צ'אנקים של טקסט"""
        reader = PdfReader(io.BytesIO(file_content))
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"

        return FileProcessor.create_chunks(full_text)

    @staticmethod
    def create_chunks(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        chunks = []
        clean_text = " ".join(text.split())
        words = clean_text.split()
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        return chunks