from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import serializers

from app_run.serializers import (
    UserSerializer,
    AthleteInfoSerializer,
    PositionSerializer,
    CollectibleItemSerializer,
)    

from app_run.models import Run


class UserSerializeTestCase(TestCase):
    def setUp(self):
        self.coach = User.objects.create(username='coach',
                                         is_staff=True)
        self.athlete = User.objects.create(username='athlete',
                                           is_staff=False)

    def test_get_type_coach(self):
        serializer = UserSerializer()
        self.assertEqual('coach', serializer.get_type(self.coach))

    def test_get_type_athlete(self):
        serializer = UserSerializer()
        self.assertEqual('athlete', serializer.get_type(self.athlete))


class AthleteInfoSerializerTestCase(TestCase):
    def test_validate_weight(self):
        serializer = AthleteInfoSerializer()
        self.assertEqual(23, serializer.validate_weight(23))
    
    def test_validate_weight_error(self):
        serializer = AthleteInfoSerializer()
        self.assertRaises(serializers.ValidationError,
                          serializer.validate_weight, 0)
        self.assertRaises(serializers.ValidationError,
                          serializer.validate_weight, 900)


class PositionSerializerTestCase(TestCase):
    def test_validate_run(self):
        serializer = PositionSerializer()
        athlete = User.objects.create(username='user')
        run_status_init = Run.objects.create(athlete=athlete,
                                             comment='comment 1')
        run_status_in_progress = Run.objects.create(athlete=athlete,
                                                    comment='comment 1',
                                                    status='in_progress')
        run_status_finished = Run.objects.create(athlete=athlete,
                                                 comment='comment 1',
                                                 status='finished')
        self.assertRaises(serializers.ValidationError,
                          serializer.validate_run, run_status_init)
        self.assertRaises(serializers.ValidationError,
                          serializer.validate_run, run_status_finished)
        self.assertEqual(serializer.validate_run(run_status_in_progress),
                         run_status_in_progress)
                                      
    def test_validate_latitude(self):
        serializer = PositionSerializer()
        self.assertEqual(23, serializer.validate_latitude(23))
    
    def test_validate_latitude_error(self):
        serializer = PositionSerializer()
        self.assertRaises(serializers.ValidationError,
                          serializer.validate_latitude, 91)
        self.assertRaises(serializers.ValidationError,
                          serializer.validate_latitude, -91)
    
    def test_validate_longitude(self):
        serializer = PositionSerializer()
        self.assertEqual(23, serializer.validate_longitude(23))

    def test_validate_longitude_error(self):
        serializer = PositionSerializer()
        self.assertRaises(serializers.ValidationError,
                          serializer.validate_longitude, 181)
        self.assertRaises(serializers.ValidationError,
                          serializer.validate_longitude, -181)
        

class CollectibleItemSerializerTestCase(TestCase):
    def test_validate_latitude(self):
        serializer = CollectibleItemSerializer()
        self.assertEqual(23, serializer.validate_latitude(23))
    
    def test_validate_latitude_error(self):
        serializer = CollectibleItemSerializer()
        self.assertRaises(serializers.ValidationError,
                          serializer.validate_latitude, 91)
        self.assertRaises(serializers.ValidationError,
                          serializer.validate_latitude, -91)
    
    def test_validate_longitude(self):
        serializer = CollectibleItemSerializer()
        self.assertEqual(23, serializer.validate_longitude(23))

    def test_validate_longitude_error(self):
        serializer = CollectibleItemSerializer()
        self.assertRaises(serializers.ValidationError,
                          serializer.validate_longitude, 181)
        self.assertRaises(serializers.ValidationError,
                          serializer.validate_longitude, -181)