from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Count, Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import filters
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.generics import GenericAPIView
from rest_framework.exceptions import ParseError
from rest_framework import mixins
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

from app_run.models import Run
from app_run.serializers import RunSerializer, UserSerializer


@api_view()
def detail_company(request):
    return Response(settings.ABOUT_COMPANY)


class RunPagination(PageNumberPagination):
    page_size_query_param = 'size'


class RunViewSet(ModelViewSet):
    queryset = Run.objects.select_related('athlete').all()
    serializer_class = RunSerializer
    pagination_class = RunPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'athlete']
    ordering_fields = ['created_at']


class Userpagination(PageNumberPagination):
    page_size_query_param = 'size'


class UserViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.prefetch_related('athletes')\
                        .annotate(run_finished=Count('athletes__status',
                                                     filter=Q(athletes__status='finished')))    
    serializer_class = UserSerializer
    pagination_class = Userpagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name']
    ordering_fields = ['date_joined']

    def get_queryset(self):
        queryset = self.queryset.filter(is_superuser=False).all()

        type_user = self.request.query_params.get('type')
        if type_user == 'coach':
            return queryset.filter(is_staff=True)
        elif type_user == 'athlete':
            return queryset.filter(is_staff=False)
        else:
            return queryset


class RunViewStart(mixins.UpdateModelMixin,
                   GenericAPIView):
    queryset = Run.objects.all()
    serializer_class = RunSerializer

    def post(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
    
    def get_object(self):
        obj = super().get_object()
        if obj.status == 'in_progress':
            raise ParseError('The race has already begun')
        elif obj.status == 'finished':
            raise ParseError('The race is already over')
        else:
            return obj

    def perform_update(self, serializer):
        return serializer.save(status='in_progress')


class RunViewStop(mixins.UpdateModelMixin,
                  GenericAPIView):
    queryset = Run.objects.all()
    serializer_class = RunSerializer
    
    def post(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def get_object(self):
        obj = super().get_object()
        if obj.status == 'init':
            raise ParseError('The race has not started yet')
        elif obj.status == 'finished':
            raise ParseError('The race is already over')
        else:
            return obj

    def perform_update(self, serializer):
        return serializer.save(status='finished')