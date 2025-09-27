from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import filters
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.generics import GenericAPIView
from rest_framework.exceptions import ParseError
from rest_framework import mixins
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework import status

from app_run.models import Run, AthleteInfo
from app_run.serializers import RunSerializer, UserSerializer, AthleteInfoSerializer


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
                        .annotate(runs_finished=Count('athletes__status',
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


class RunViewStart(mixins.UpdateModelMixin, GenericAPIView):
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


class RunViewStop(mixins.UpdateModelMixin, GenericAPIView):
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


class AthleteInfoView(mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      GenericAPIView):
    queryset = AthleteInfo.objects.all()
    serializer_class = AthleteInfoSerializer
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)    

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        response.status_code = status.HTTP_201_CREATED
        return response

    def perform_update(self, serializer):
        return serializer.save(athlete=self.user)
        
    def get_object(self):
        self.user = get_object_or_404(User.objects.all(), id=self.kwargs['id'])
        athlete_info, _ = self.get_queryset().get_or_create(athlete=self.user)
        return athlete_info