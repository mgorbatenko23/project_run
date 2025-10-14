import pdb
import collections
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Count, Q, Sum, Min, Max, Avg
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
from rest_framework import views
from rest_framework import parsers
from django_filters.rest_framework import DjangoFilterBackend
from openpyxl import load_workbook

from app_run.models import (
    Run,
    AthleteInfo,
    Challenge,
    Position,
    CollectibleItem,
    Subscribe,
)    
from app_run.serializers import (
    RunSerializer,
    UserSerializer,
    AthleteInfoSerializer,
    ChallengeSerializer,
    PositionSerializer,
    CollectibleItemSerializer,
    UserDetailSerializer,
    UserDetailCoachSerializer,
    UserDetailAthleteSerializer,
    SubscribeSerializer,    
)
from app_run import utils


@api_view()
def detail_company(request):
    """ Название компании, слоган, адрес """
    return Response(settings.ABOUT_COMPANY)


class RunViewSet(viewsets.ModelViewSet):
    """ Забеги """
    class RunPagination(PageNumberPagination):
        page_size_query_param = 'size'

    queryset = Run.objects.select_related('athlete').all()
    serializer_class = RunSerializer
    pagination_class = RunPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'athlete']
    ordering_fields = ['created_at']


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ Атлеты и тренеры """
    class Userpagination(PageNumberPagination):
        page_size_query_param = 'size'

    queryset = User.objects.prefetch_related('athletes')\
                        .annotate(runs_finished=Count('athletes__status',
                                                     filter=Q(athletes__status='finished')))
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

    def get_serializer_class(self):
        if self.kwargs.get('pk'):
            if self.get_object().is_staff:
                return UserDetailCoachSerializer
            else:
                return UserDetailAthleteSerializer
        else:
            return UserSerializer


class RunViewStart(mixins.UpdateModelMixin, generics.GenericAPIView):
    """ Начало забега """
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
    """ Завершение забега """
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
            return obj

    def perform_update(self, serializer):
        run_object = self.get_object()

        total_distance = run_object.get_total_distance()
        run_time_seconds = 0
        run_avg_speed = 0

        run_date_time = run_object.positions.aggregate(Min('date_time'), Max('date_time'))
        if (run_date_time['date_time__min'] is not None
                and run_date_time['date_time__max'] is not None):
            run_time_seconds = utils.get_seconds_between_dates(run_date_time['date_time__max'],
                                                               run_date_time['date_time__min'])
            run_avg_speed = run_object.positions.aggregate(Avg('speed'))['speed__avg']

        run_finished = serializer.save(status='finished',
                                       distance=total_distance,
                                       run_time_seconds=run_time_seconds,
                                       speed=run_avg_speed)

        run_challenges = self.get_queryset().filter(athlete=run_finished.athlete,
                                                    status='finished') \
                                            .aggregate(total_finished=Count('id'),
                                                       total_distance=Sum('distance'))

        if run_challenges['total_finished'] == 10:
            Challenge.objects.create(athlete=run_finished.athlete,
                                     full_name='Сделай 10 Забегов!')
        if run_challenges['total_distance'] >= 50:
            Challenge.objects.create(athlete=run_finished.athlete,
                                     full_name='Пробеги 50 километров!')
        if total_distance >= 2 and run_time_seconds <= 600:
            Challenge.objects.create(athlete=run_finished.athlete,
                                    full_name='2 километра за 10 минут!')

        return run_finished


class AthleteInfoView(generics.RetrieveUpdateAPIView):
    """ Дополнительная информация об атлете """
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
    """ Челенджи """
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['athlete']


class PositionViewSet(viewsets.ModelViewSet):
    """ Кооординаты атлета """
    queryset = Position.objects.select_related('run').all()
    serializer_class = PositionSerializer
    http_method_names = ['get', 'post', 'delete', 'head', 'options', 'trace']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['run']

    def perform_create(self, serializer):
        run_object = serializer.validated_data['run']
        last_position = run_object.positions.last()

        if last_position:
            current_latitude = serializer.validated_data['latitude']
            current_longitude = serializer.validated_data['longitude']

            distance_last_position = utils.get_distance_in_km([
                                        (last_position.latitude, last_position.longitude),
                                        (current_latitude, current_longitude)
                                        ])
            distance_total = distance_last_position + last_position.distance

            current_date = serializer.validated_data['date_time']
            date_last_position = last_position.date_time
            total_seconds = utils.get_seconds_between_dates(current_date, date_last_position)
            speed_between_positions = (distance_last_position * 1000) / total_seconds

            position = serializer.save(distance=distance_total,
                                       speed=speed_between_positions)
        else:
            position = serializer.save()

        CollectibleItem.objects.exclude(
            Q(latitude__range=(-90, 90)) & Q(longitude__range=(-180, 180))).delete()
        for artifact in CollectibleItem.objects.all():
            distance = utils.get_distance_to_object(
                            (artifact.latitude, artifact.longitude),
                            (position.latitude, position.longitude))
            if distance < 100:
                user = position.run.athlete
                user.items.add(artifact)


class CollectibleItemView(viewsets.ReadOnlyModelViewSet):
    """ Коллекция предметов(артефакты) собираемые атлетом """
    queryset = CollectibleItem.objects.all()
    serializer_class = CollectibleItemSerializer


class FileUploadView(views.APIView):
    """ Загрузка коллекции предметов(артефактов) из файла """
    parser_classes = [parsers.MultiPartParser]

    def post(self, request):        
        workbook = load_workbook(filename=request.FILES.get('file'))
        sheet = workbook.active
        correct_row = []
        errors_row = []
        headers = ['name', 'uid', 'value', 'latitude', 'longitude', 'picture']
        for i, row in enumerate(sheet):
            if i == 0:
                continue
            data = {header: cell.value for header, cell in zip(headers, row)}
            if CollectibleItemSerializer(data=data).is_valid():
                correct_row.append(data)
            else:
                errors_row.append(list(data.values()))

        serializer = CollectibleItemSerializer(data=correct_row, many=True)
        serializer.is_valid()
        serializer.save()        

        return Response(data=errors_row, status=status.HTTP_200_OK)


class SubscribeView(generics.CreateAPIView):
    queryset = Subscribe.objects.all()
    serializer_class = SubscribeSerializer

    def create(self, request, *args, **kwargs):
        get_object_or_404(User, id=self.kwargs['id'])
        response = super().create(request, *args, **kwargs)
        response.status_code = status.HTTP_200_OK
        return response

    def get_serializer(self, *args, **kwargs):
        serializer = super().get_serializer(*args, **kwargs)
        serializer.initial_data['coach'] = self.kwargs['id']
        return serializer


class ChallengeSummaryView(views.APIView):
    def get(self, request):
        queryset = Challenge.objects \
                            .select_related('athlete') \
                            .filter(athlete__is_staff=False) \
                            .order_by('full_name') \
                            .all()
        
        record = collections.defaultdict(list)
        results = []
        qs_list = list(queryset)
        first_challenge = qs_list[0].full_name
        for challenge in qs_list:
            if first_challenge != challenge.full_name:
                results.append(dict(record))
                first_challenge = challenge.full_name
                record = collections.defaultdict(list)
            record['name_to_display'] = challenge.full_name
            record['athletes'].append({'id': challenge.athlete_id,
                                  'full_name': f'{challenge.athlete.first_name} {challenge.athlete.last_name}',
                                  'username': challenge.athlete.username})
        else:
            results.append(dict(record))

        return Response(results)