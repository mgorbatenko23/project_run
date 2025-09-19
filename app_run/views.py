from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from app_run.models import Run
from app_run.serializers import RunSerializer


@api_view()
def detail_company(request):
    return Response(settings.ABOUT_COMPANY)


class RunViewSet(ModelViewSet):
    queryset = Run.objects.all()
    serializer_class = RunSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(athlete=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(athlete=self.request.user)
        