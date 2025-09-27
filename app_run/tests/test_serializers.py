from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import serializers

from app_run.serializers import UserSerializer, AthleteInfoSerializer


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