from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.request import Request

from app_run.models import Run
from app_run.serializers import RunSerializer, UserSerializer


@api_view()
def detail_company(request):
    return Response(settings.ABOUT_COMPANY)


class RunViewSet(ModelViewSet):
    queryset = Run.objects.select_related('athlete').all()
    serializer_class = RunSerializer


class UserViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(is_superuser=False).only('id',
                                                                 'date_joined',
                                                                 'username',
                                                                 'last_name',
                                                                 'first_name')
        type_user = self.request.query_params.get('type')
        if type_user == 'coach':
            return queryset.filter(is_staff=True)
        elif type_user == 'athlete':
            return queryset.filter(is_staff=False)
        else:
            return queryset