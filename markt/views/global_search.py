from django.apps import apps
from django.db.models import Q
from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class GlobalSearchAPIView(APIView):
    def get(self, request):
        query = request.GET.get('q', '').strip()
        if not query:
            return Response({"detail": "Parámetro 'q' requerido."}, status=status.HTTP_400_BAD_REQUEST)

        MIS_APPS = ["markt", "auth"]  # pon aquí tu app o apps
        EXCLUDED_FIELDS = ['password']
        EXCLUDED_MODELS = ["seguimiento", "like", "permission"]

        results = {}

        for model in apps.get_models():
            if model._meta.app_label not in MIS_APPS:
                continue
            
            if model._meta.model_name in EXCLUDED_MODELS:
                continue

            model_name = model._meta.model_name
            app_label = model._meta.app_label
            queryset = model.objects.all()

            q_object = Q()
            for field in model._meta.fields:
                if isinstance(field, (models.CharField, models.TextField)):
                    q_object |= Q(**{f"{field.name}__icontains": query})

            filtered = queryset.filter(q_object)
            if filtered.exists():
                results[f"{app_label}.{model_name}"] = [
                    {
                        "id": obj.id,
                        **{
                            field.name: getattr(obj, field.name)
                            for field in model._meta.fields
                            if isinstance(field, (models.CharField, models.TextField)) and field.name not in EXCLUDED_FIELDS
                        }
                    }
                    for obj in filtered
                ]

        return Response(results)

