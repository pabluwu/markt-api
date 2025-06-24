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
        os.makedirs(chroma_dir, exist_ok=True)
        
        # Configurar ChromaDB con persistencia
        return chromadb.PersistentClient(path=chroma_dir)

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
        genai.configure(api_key="AIzaSyCiQ33NtzVvddmsHQHDB3DgEXKsx3VQFxY")
        
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
        client = self.get_chromadb_client()
        collection = client.get_or_create_collection("recursos")
        collection.add(
            embeddings=[vector],
            metadatas=[{"recurso_id": instance.id}],
            ids=[str(instance.id)]
        )
        
        # 5. Verificación de que se guardó correctamente en ChromaDB
        try:
            # Verificar que el documento existe en ChromaDB
            verification = collection.get(ids=[str(instance.id)])
            
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
            # 1. Obtener el recurso
            recurso = self.get_object()
            
            # 2. Validar que existe en ChromaDB
            client = self.get_chromadb_client()
            
            # Verificar si la colección existe, si no, crearla
            try:
                collection = client.get_collection("recursos")
            except Exception:
                # Si la colección no existe, crear una nueva
                collection = client.create_collection("recursos")
                print("📚 Colección 'recursos' creada automáticamente")
            
            # Buscar el documento en ChromaDB
            chroma_results = collection.get(ids=[str(recurso.id)])
            
            if not chroma_results['ids']:
                return Response({
                    'error': 'El documento no está disponible para consultas. No se encontró en la base de vectores.',
                    'detalle': 'El documento existe en la base de datos pero no tiene su vector asociado en ChromaDB. Intenta subir el documento nuevamente.'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 3. Obtener la pregunta del request
            pregunta = request.data.get('pregunta')
            if not pregunta:
                return Response({
                    'error': 'Se requiere una pregunta en el campo "pregunta"'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 4. Extraer el texto del PDF para el contexto
            pdf_path = recurso.archivo.path
            texto_pdf = ""
            try:
                with open(pdf_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        texto_pdf += page.extract_text() or ""
            except Exception as e:
                return Response({
                    'error': f'Error al leer el archivo PDF: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # 5. Configurar Google Gemini para la consulta
            genai.configure(api_key="AIzaSyCiQ33NtzVvddmsHQHDB3DgEXKsx3VQFxY")
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # 6. Crear el prompt para la consulta
            prompt = f"""
            Basándote únicamente en el siguiente documento, responde la pregunta de manera clara y precisa.
            
            DOCUMENTO:
            {texto_pdf[:8000]}  # Limitar a 8000 caracteres para evitar límites
            
            PREGUNTA: {pregunta}
            
            INSTRUCCIONES:
            - Responde solo basándote en la información del documento
            - Si la información no está en el documento, indícalo claramente
            - Proporciona una respuesta estructurada y útil
            - Si es necesario, cita partes específicas del documento
            """
            
            # 7. Generar la respuesta con Google Gemini
            response = model.generate_content(prompt)
            
            # 8. Devolver la respuesta
            return Response({
                'recurso_id': recurso.id,
                'titulo': recurso.titulo,
                'pregunta': pregunta,
                'respuesta': response.text,
                'fecha_consulta': recurso.fecha_subida
            }, status=status.HTTP_200_OK)
            
        except Recurso.DoesNotExist:
            return Response({
                'error': 'Recurso no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({
                'error': f'Error al procesar la consulta: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
