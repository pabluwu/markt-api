from rest_framework import viewsets, permissions, parsers
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
import PyPDF2
import chromadb
import google.generativeai as genai
import os
from ..models import Recurso
from ..serializers.recurso import RecursoSerializer
from ..permissions import IsAuthenticatedOrReadOnlyCustom

class RecursoViewSet(viewsets.ModelViewSet):
    queryset = Recurso.objects.all()
    serializer_class = RecursoSerializer
    permission_classes = [IsAuthenticatedOrReadOnlyCustom]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    pagination_class = PageNumberPagination

    def get_chromadb_client(self):
        """Obtiene el cliente de ChromaDB con configuración persistente"""
        # Crear directorio para ChromaDB si no existe
        chroma_dir = os.path.join(os.getcwd(), 'chroma_db')
        print(chroma_dir)
        os.makedirs(chroma_dir, exist_ok=True)
        
        # Configurar ChromaDB con persistencia
        return chromadb.PersistentClient(path=chroma_dir)
    
    def get_gemini_api_key(self):
        """Obtiene la API key de Google Gemini solo desde variables de entorno"""
        api_key = os.environ.get('GEMINI_API_KEY')
        print(api_key)
        if not api_key:
            raise ValueError("GEMINI_API_KEY no está configurada como variable de entorno.")
        return api_key

    def perform_create(self, serializer):
        # 1. Guardar el recurso normalmente (incluye el archivo PDF)
        instance = serializer.save(autor=self.request.user)

        # 2. Extraer el texto del PDF usando PyPDF2
        pdf_path = instance.archivo.path
        texto_pdf = ""
        try:
            with open(pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    texto_pdf += page.extract_text() or ""
        except Exception as e:
            # Manejo de errores de lectura de PDF
            print(f"Error al leer PDF: {e}")
            texto_pdf = ""

        # 3. Generar embeddings con Google Gemini
        try:
            api_key = self.get_gemini_api_key()
            genai.configure(api_key=api_key)
        except ValueError as e:
            print(f"Error configurando Gemini: {e}")
            return
        
        # Dividir el texto en chunks si es muy largo (límite ~30,000 bytes)
        def chunk_text(text, max_bytes=30000):
            """Divide el texto en chunks que no excedan max_bytes"""
            chunks = []
            current_chunk = ""
            
            for char in text:
                test_chunk = current_chunk + char
                if len(test_chunk.encode('utf-8')) > max_bytes:
                    if current_chunk:
                        chunks.append(current_chunk)
                        current_chunk = char
                    else:
                        # Si un solo carácter excede el límite, lo truncamos
                        chunks.append(char[:max_bytes//4])  # Aproximadamente
                else:
                    current_chunk = test_chunk
            
            if current_chunk:
                chunks.append(current_chunk)
            
            return chunks
        
        # Dividir el texto en chunks
        text_chunks = chunk_text(texto_pdf)
        
        # Generar embeddings para cada chunk
        all_embeddings = []
        for chunk in text_chunks:
            try:
                response = genai.embed_content(model="embedding-001", content=chunk)
                all_embeddings.append(response['embedding'])
            except Exception as e:
                print(f"Error generando embedding para chunk: {e}")
                continue
        
        # Usar el primer embedding como representativo del documento
        # O podrías promediar todos los embeddings si prefieres
        vector = all_embeddings[0] if all_embeddings else []

        # 4. Guardar el vector en ChromaDB asociado al ID del recurso
        embeddings       = all_embeddings
        documents        = text_chunks
        metadatas        = [{"recurso_id": instance.id}] * len(text_chunks)
        ids              = [f"{instance.id}_{i}" for i in range(len(text_chunks))]

        client    = self.get_chromadb_client()
        collection = client.get_or_create_collection("recursos")

        collection.add(
            embeddings=embeddings,
            documents=documents,    # aquí guardas cada fragmento
            metadatas=metadatas,
            ids=ids
        )
        
        # client.persist()
        
        # 5. Verificación de que se guardó correctamente en ChromaDB
        try:
            # Verificar que el documento existe en ChromaDBz
            verification = collection.get(ids=ids)
            
            if verification['ids']:
                print(f"✅ VERIFICACIÓN EXITOSA:")
                print(f"   📄 Recurso ID: {instance.id}")
                print(f"   📝 Título: {instance.titulo}")
                print(f"   👤 Autor: {instance.autor.username}")
                print(f"   🔢 Vector guardado: {len(vector)} valores")
                print(f"   📊 Total documentos en ChromaDB: {collection.count()}")
                print(f"   🆔 ID verificado en ChromaDB: {verification['ids'][0]}")
                print(f"   💾 Directorio persistente: {client._path}")
            else:
                print(f"❌ ERROR: El documento no se guardó correctamente en ChromaDB")
                print(f"   Recurso ID: {instance.id}")
                
        except Exception as e:
            print(f"❌ ERROR en verificación de ChromaDB: {e}")
            print(f"   Recurso ID: {instance.id}")

    @action(detail=True, methods=['post'], url_path='consultar')
    def consultar_documento(self, request, pk=None):
        """
        Endpoint para consultar un documento específico usando Google Gemini
        POST /api/recursos/{id}/consultar/
        Body: {"pregunta": "¿Qué dice el documento sobre...?"}
        """
        try:
            try:
                recurso = self.get_object()
            except Exception as e:
                print(f" No se obtuvo id  Recurso ID: {e}")
            # 1. Validar pregunta
            pregunta = request.data.get('pregunta')
            if not pregunta:
                return Response({'error': 'Se requiere una pregunta en el campo "pregunta"'}, status=status.HTTP_400_BAD_REQUEST)

            # 2. Obtener cliente y colección
            print("obteniendo client: ========================== \n")
            client = self.get_chromadb_client()
            try:
                collection = client.get_collection("recursos")
            except Exception:
                collection = client.create_collection("recursos")

            # 3. Generar embedding de la pregunta
            print("configurando Gemini: ========================== \n")
            try:
                api_key = self.get_gemini_api_key()
                genai.configure(api_key=api_key)
            except ValueError as e:
                print(f"Error configurando Gemini: {e}")
                return
            pregunta_resp = genai.embed_content(model="embedding-001", content=pregunta)
            query_emb = pregunta_resp['embedding']

            # 4. Hacer búsqueda en ChromaDB — recupera, por ejemplo, los 5 chunks más cercanos]
            print("obteniendo query chroma: ========================== \n")
            chroma_results = collection.query(
                query_embeddings=[query_emb],
                n_results=5,  # o cuantos quieras devolver
                where={"recurso_id": recurso.id}
            )

            # chroma_results['documents'] → [[doc1, doc2, …]]
            print("results query chroma: ========================== \n")
            context_chunks = chroma_results['documents'][0]
            contexto = "\n\n".join(context_chunks)            # => [doc1, doc2, …]

            # Ahora sí join sobre strings
            # contexto = "\n\n".join(context_chunks)
            # contexto = "\n\n".join(context_chunks)

            # 6. Generar la respuesta con Google Gemini
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"""
            Basándote únicamente en el siguiente fragmento extraído del documento, responde la pregunta de manera clara y precisa.
            
            CONTEXTO:
            {contexto}
            
            PREGUNTA: {pregunta}
            
            INSTRUCCIONES:
            - Responde solo basándote en la información del contexto
            - Si la información no está, indícalo claramente
            - Proporciona una respuesta estructurada y útil
            """
            response = model.generate_content(prompt)

            # 7. Retornar resultado
            return Response({
                'recurso_id': recurso.id,
                'titulo': recurso.titulo,
                'pregunta': pregunta,
                'respuesta': response.text,
                'fecha_consulta': recurso.fecha_subida
            }, status=status.HTTP_200_OK)

        except Recurso.DoesNotExist:
            return Response({'error': 'Recurso no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            print(e)
            return Response({'error': f'Error al procesar la consulta: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    