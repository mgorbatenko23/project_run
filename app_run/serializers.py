from django.contrib.auth.models import User
from rest_framework import serializers

from app_run.models import(
    Run,
    AthleteInfo,
    Challenge,
    Position,
    CollectibleItem,
)    


class AthleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'last_name', 'first_name']


class RunSerializer(serializers.ModelSerializer):
    athlete_data = AthleteSerializer(source='athlete', read_only=True)

    class Meta:
        model = Run
        fields = ['id',
                  'comment',
                  'status',
                  'created_at',
                  'athlete',
                  'distance',
                  'run_time_seconds',
                  'athlete_data']


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    runs_finished = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'date_joined', 'username', 'last_name', 'first_name', 'type', 'runs_finished']

    def get_type(self, obj):
        return 'coach' if obj.is_staff else 'athlete'

    def get_runs_finished(self, obj):
        return obj.runs_finished
    

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

    class Meta:
        model = Position
        fields = ['id', 'run', 'latitude', 'longitude', 'date_time']

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
        raise serializers.ValidationError('Thw longitude must be between -180 and 180')


class UserDetailSerializer(UserSerializer):
    items = CollectibleItemSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ['id', 'date_joined', 'username', 'last_name', 'first_name', 'type', 'runs_finished', 'items']