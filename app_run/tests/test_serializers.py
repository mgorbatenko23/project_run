from django.contrib.auth.models import User
from django.test import TestCase

from app_run.serializers import UserSerializer


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

