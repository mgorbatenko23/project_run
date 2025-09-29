from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import filters
from rest_framework import viewsets
from rest_framework import generics
from rest_framework import mixins
from rest_framework.exceptions import ParseError
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend

from app_run.models import Run, AthleteInfo, Challenge, Position
from app_run.serializers import (
    RunSerializer,
    UserSerializer,
    AthleteInfoSerializer,
    ChallengeSerializer,
    PositionSerializer,
)
from app_run import utils


@api_view()
def detail_company(request):
    return Response(settings.ABOUT_COMPANY)


class RunPagination(PageNumberPagination):
    page_size_query_param = 'size'


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.select_related('athlete').all()
    serializer_class = RunSerializer
    pagination_class = RunPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'athlete']
    ordering_fields = ['created_at']


class Userpagination(PageNumberPagination):
    page_size_query_param = 'size'


class UserViewSet(viewsets.ReadOnlyModelViewSet):
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


class RunViewStart(mixins.UpdateModelMixin, generics.GenericAPIView):
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


class RunViewStop(mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = Run.objects.select_related('athlete').prefetch_related('positions').all()
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
            self.obj = obj
            return obj

    def perform_update(self, serializer):
        coordinates = [(obj.latitude, obj.longitude) for obj in self.obj.positions.all()]
        run_finished = serializer.save(status='finished', distance=utils.get_distance_in_km(coordinates))
        run_stats = self.get_queryset().filter(athlete=run_finished.athlete,
                                               status='finished').aggregate(
                                                   total_finished=Count('id'),
                                                   total_distance=Sum('distance'))

        if run_stats['total_finished'] == 10:
            Challenge.objects.create(athlete=run_finished.athlete,
                                     full_name='Сделай 10 Забегов!')
        if run_stats['total_distance'] >= 50:
            Challenge.objects.create(athlete=run_finished.athlete,
                                     full_name='Пробеги 50 километров!')
        return run_finished


class AthleteInfoView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.select_related('athlete_info').all()
    serializer_class = AthleteInfoSerializer
    http_method_names = ['get', 'put', 'head', 'options', 'trace']
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        response.status_code = status.HTTP_201_CREATED
        return response

    def perform_update(self, serializer):
        return serializer.save(athlete=self.user)
        
    def get_object(self):
        qs_users = self.get_queryset()
        self.user = get_object_or_404(qs_users, id=self.kwargs['id'])
        if getattr(self.user, 'athlete_info', False):
            return self.user.athlete_info
        else:
            return AthleteInfo.objects.create(athlete=self.user)
        

class ChallengeView(generics.ListAPIView):
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['athlete']


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    http_method_names = ['get', 'post', 'delete', 'head', 'options', 'trace']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['run']