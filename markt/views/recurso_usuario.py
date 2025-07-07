from rest_framework import viewsets, permissions, parsers, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType
import PyPDF2
import chromadb
import google.generativeai as genai
import os
from ..models import RecursoUsuarios
from ..serializers.recurso_usuarios import RecursoUsuariosSerializer
from ..permissions import IsAuthenticatedOrReadOnlyCustom

class RecursoUsuariosViewSet(viewsets.ModelViewSet):
    queryset = RecursoUsuarios.objects.all()
    serializer_class = RecursoUsuariosSerializer
    permission_classes = [IsAuthenticatedOrReadOnlyCustom]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    pagination_class = PageNumberPagination

    def get_chromadb_client(self):
        chroma_dir = os.path.join(os.getcwd(), 'chroma_db')
        os.makedirs(chroma_dir, exist_ok=True)
        return chromadb.PersistentClient(path=chroma_dir)

    def get_gemini_api_key(self):
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY no está configurada como variable de entorno.")
        return api_key
    
    def get_queryset(self):
        queryset = RecursoUsuarios.objects.all()
        author_type = self.request.query_params.get('author_type')
        author_id = self.request.query_params.get('author_id')

        if author_type and author_id:
            try:
                # Usar ContentType para encontrar el modelo
                content_type = ContentType.objects.get(model=author_type.lower())
                queryset = queryset.filter(author_type=content_type, author_id=author_id)
            except ContentType.DoesNotExist:
                # Si el tipo es inválido, retornar queryset vacío
                return RecursoUsuarios.objects.none()

        return queryset

    def perform_create(self, serializer):
        instance = serializer.save()

        # Extraer texto del PDF
        pdf_path = instance.archivo.path
        texto_pdf = ""
        try:
            with open(pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    texto_pdf += page.extract_text() or ""
        except Exception as e:
            print(f"Error al leer PDF: {e}")
            texto_pdf = ""

        # Configurar Gemini
        try:
            api_key = self.get_gemini_api_key()
            genai.configure(api_key=api_key)
        except ValueError as e:
            print(f"Error configurando Gemini: {e}")
            return

        def chunk_text(text, max_bytes=30000):
            chunks, current_chunk = [], ""
            for char in text:
                test_chunk = current_chunk + char
                if len(test_chunk.encode('utf-8')) > max_bytes:
                    if current_chunk:
                        chunks.append(current_chunk)
                        current_chunk = char
                    else:
                        chunks.append(char[:max_bytes//4])
                else:
                    current_chunk = test_chunk
            if current_chunk:
                chunks.append(current_chunk)
            return chunks

        text_chunks = chunk_text(texto_pdf)
        all_embeddings = []
        for chunk in text_chunks:
            try:
                response = genai.embed_content(model="embedding-001", content=chunk)
                all_embeddings.append(response['embedding'])
            except Exception as e:
                print(f"Error generando embedding: {e}")
                continue

        vector = all_embeddings[0] if all_embeddings else []

        embeddings = all_embeddings
        documents = text_chunks
        metadatas = [{"recurso_id": instance.id}] * len(text_chunks)
        ids = [f"{instance.id}_{i}" for i in range(len(text_chunks))]

        client = self.get_chromadb_client()
        collection = client.get_or_create_collection("recursos")

        collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        # Verificación
        try:
            verification = collection.get(ids=ids)
            if verification['ids']:
                print(f"✅ VERIFICACIÓN EXITOSA: Recurso ID: {instance.id}, Título: {instance.titulo}")
            else:
                print(f"❌ ERROR: Documento no guardado correctamente.")
        except Exception as e:
            print(f"❌ ERROR en verificación de ChromaDB: {e}")

    @action(detail=True, methods=['post'], url_path='consultar')
    def consultar_documento(self, request, pk=None):
        try:
            recurso = self.get_object()
            pregunta = request.data.get('pregunta')
            if not pregunta:
                return Response({'error': 'Se requiere una pregunta'}, status=status.HTTP_400_BAD_REQUEST)

            client = self.get_chromadb_client()
            try:
                collection = client.get_collection("recursos")
            except Exception:
                collection = client.create_collection("recursos")

            api_key = self.get_gemini_api_key()
            genai.configure(api_key=api_key)

            pregunta_resp = genai.embed_content(model="embedding-001", content=pregunta)
            query_emb = pregunta_resp['embedding']

            chroma_results = collection.query(
                query_embeddings=[query_emb],
                n_results=5,
                where={"recurso_id": recurso.id}
            )

            context_chunks = chroma_results['documents'][0]
            contexto = "\n\n".join(context_chunks)

            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"""
            CONTEXTO:
            {contexto}

            PREGUNTA: {pregunta}

            INSTRUCCIONES:
            - Responde solo con la información del contexto
            - Si no hay información suficiente, dilo claramente
            """
            response = model.generate_content(prompt)

            return Response({
                'recurso_id': recurso.id,
                'titulo': recurso.titulo,
                'pregunta': pregunta,
                'respuesta': response.text,
                'fecha_consulta': recurso.fecha_subida
            }, status=status.HTTP_200_OK)

        except RecursoUsuarios.DoesNotExist:
            return Response({'error': 'Recurso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
