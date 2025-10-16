from django.contrib.auth.models import User
from rest_framework import serializers

from app_run.models import(
    Run,
    AthleteInfo,
    Challenge,
    Position,
    CollectibleItem,
    Subscribe,
)    


class AthleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'last_name', 'first_name']


class RunSerializer(serializers.ModelSerializer):
    athlete_data = AthleteSerializer(source='athlete', read_only=True)
    speed = serializers.SerializerMethodField()

    class Meta:
        model = Run
        fields = ['id',
                  'comment',
                  'status',
                  'created_at',
                  'athlete',
                  'distance',
                  'speed',
                  'run_time_seconds',
                  'athlete_data',
                  ]
        
        read_only_fields = ['speed']

    def get_speed(self, obj):
        if obj.speed:
            return round(obj.speed, 2)
        return obj.speed


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    runs_finished = serializers.SerializerMethodField(read_only=True)
    rating = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id',
                  'date_joined',
                  'username',
                  'last_name',
                  'first_name',
                  'type',
                  'runs_finished',
                  'rating',
                  ]

    def get_type(self, obj):
        return 'coach' if obj.is_staff else 'athlete'

    def get_runs_finished(self, obj):
        return obj.runs_finished

    def get_rating(self, obj):
        return self.context['avg_ratings'][obj.id]
    

class AthleteInfoSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AthleteInfo
        fields = ['goals', 'weight', 'user_id']

    def get_user_id(self, obj):        
        return obj.pk
    
    def validate_weight(self, value):
        if 0 < value < 900:
            return value
        raise serializers.ValidationError('The weight must be between 1 and 900')


class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = '__all__'


class PositionSerializer(serializers.ModelSerializer):
    date_time = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S.%f')
    speed = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()

    class Meta:
        model = Position
        fields = ['id',
                  'run',
                  'latitude',
                  'longitude',
                  'date_time',
                  'speed',
                  'distance',
                  ]
        
        read_only_fields = ['speed', 'distance']

    def get_speed(self, obj):
        if obj.speed:
            return round(obj.speed, 2)
        return obj.speed
    
    def get_distance(self, obj):
        if obj.distance:
            return round(obj.distance, 2)
        return obj.distance

    def validate_run(self, run):
        if run.status in ['init', 'finished']:
            raise serializers.ValidationError('Run must be status in_progress')
        return run
        
    def validate_latitude(self, value):
        if -90 <= value <= 90:
            return value
        raise serializers.ValidationError('The latitude must be between -90 and 90')
    
    def validate_longitude(self, value):
        if -180 <= value <= 180:
            return value
        raise serializers.ValidationError('The longitude must be between -180 and 180')


class CollectibleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectibleItem
        fields = ['id', 'name', 'uid', 'latitude', 'longitude', 'picture', 'value']

    def validate_latitude(self, value):
        if -90 <= value <= 90:
            return value
        raise serializers.ValidationError('The latitude must be between -90 and 90')
    
    def validate_longitude(self, value):
        if -180 <= value <= 180:
            return value
        raise serializers.ValidationError('The longitude must be between -180 and 180')


class UserDetailSerializer(UserSerializer):
    items = CollectibleItemSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ['id',
                  'date_joined',
                  'username',
                  'last_name',
                  'first_name',
                  'type',
                  'runs_finished',                   
                  'items',
                  'rating',
                  ]
    

class UserDetailCoachSerializer(UserSerializer):
    athletes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id',
                  'date_joined',
                  'username',
                  'last_name',
                  'first_name',
                  'type',
                  'athletes',
                  'rating',
                  ]
    
    def get_athletes(self, obj):
        qs = obj.subscribes_coach.all()
        return [_obj.athlete_id for _obj in qs]

class UserDetailAthleteSerializer(UserSerializer):
    items = CollectibleItemSerializer(read_only=True, many=True)
    coach = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id',
                  'date_joined',
                  'username',
                  'last_name',
                  'first_name',
                  'type',
                  'runs_finished',                   
                  'items',
                  'coach',
                  ]
        
    def get_coach(self, obj):
        athlete = obj.subscribes_athlete.first()
        if athlete:
            return athlete.coach_id


        
class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = ['id', 'athlete', 'coach']

    def validate_athlete(self, obj):
        if not obj.is_staff:
            return obj
        raise serializers.ValidationError('Only users with the type athlete can subscribe')

    def validate_coach(self, obj):
        if obj.is_staff:
            return obj
        raise serializers.ValidationError('User must be type coach')


class RateCoachSerializer(serializers.Serializer):
    athlete = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(is_staff=False),
                                                 required=True)
    coach_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(is_staff=True),
                                               required=True)
    rating = serializers.IntegerField(max_value=5, min_value=1, required=True)


class AnalyticsForCoachSerializer(serializers.Serializer):
    coach_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(is_staff=True),
                                                  required=True)