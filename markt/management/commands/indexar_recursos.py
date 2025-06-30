import os
from django.core.management.base import BaseCommand
from markt.models import Recurso
import PyPDF2
import chromadb
import google.generativeai as genai
from django.conf import settings

class Command(BaseCommand):
    help = "Indexa en ChromaDB todos los recursos existentes"

    def chunk_text(self, text, max_bytes=30000):
        chunks, current = [], ""
        for c in text:
            test = current + c
            if len(test.encode("utf-8")) > max_bytes:
                if current:
                    chunks.append(current)
                    current = c
                else:
                    chunks.append(c[: max_bytes // 4])
            else:
                current = test
        if current:
            chunks.append(current)
        return chunks

    def get_chromadb_client(self):
        chroma_dir = os.path.join(settings.BASE_DIR, 'chroma_db')
        os.makedirs(chroma_dir, exist_ok=True)
        return chromadb.PersistentClient(path=chroma_dir)

    def get_gemini_key(self):
        key = os.environ.get('GEMINI_API_KEY')
        if not key:
            raise ValueError("GEMINI_API_KEY no configurada")
        return key

    def handle(self, *args, **options):
        self.stdout.write("🔄 Iniciando indexado de recursos existentes...")
        client     = self.get_chromadb_client()
        collection = client.get_or_create_collection("recursos")

        errores, cont = [], 0
        genai.configure(api_key=self.get_gemini_key())

        for recurso in Recurso.objects.all():
            try:
                # 1. Leer texto
                texto = ""
                with open(recurso.archivo.path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for p in reader.pages:
                        texto += p.extract_text() or ""

                # 2. Chunking
                text_chunks = self.chunk_text(texto)

                # 3. Embeddings
                embeddings = [
                    genai.embed_content(model="embedding-001", content=chunk)['embedding']
                    for chunk in text_chunks
                ]

                # 4. IDs y metadatos
                ids       = [f"{recurso.id}_{i}" for i in range(len(text_chunks))]
                metadatas = [{"recurso_id": recurso.id}] * len(text_chunks)

                # 5. Añadir a ChromaDB
                collection.add(
                    embeddings=embeddings,
                    documents=text_chunks,
                    metadatas=metadatas,
                    ids=ids
                )
                cont += 1
                self.stdout.write(f"  • Indexado Recurso {recurso.id} “{recurso.titulo}”")

            except Exception as e:
                errores.append((recurso.id, str(e)))
                self.stderr.write(f"  ✕ Error recurso {recurso.id}: {e}")

        # 6. Persistir todo
        # client.persist()
        self.stdout.write(f"\n✅ Hecho: {cont} recursos indexados.")
        if errores:
            self.stderr.write(f"❗ Se produjeron errores en {len(errores)} recursos.")
            for rid, msg in errores:
                self.stderr.write(f"   – ID {rid}: {msg}")
