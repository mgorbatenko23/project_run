from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from app_run.models import Run
from app_run.serializers import RunSerializer


class RunSerializerTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='User')
        self.run = Run.objects.create(athlete=self.user, comment='my comment')

    def test_serialization(self):
        run_created_at_to_str = self.run.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        serializer_data = RunSerializer(instance=self.run).data
        expected_data = {'id': self.run.id,
                         'comment': 'my comment',
                         'created_at': run_created_at_to_str
                         }

        self.assertEqual(expected_data, serializer_data)

    def test_deserialization(self):
        serializer = RunSerializer(data={'comment': 'my comment'})        
        
        self.assertTrue(serializer.is_valid())
        
        obj = serializer.save(athlete=self.user)
        
        self.assertEqual(self.user, obj.athlete)
        self.assertEqual('my comment', obj.comment)