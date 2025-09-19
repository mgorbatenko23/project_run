from app_run.models import Run
from django.contrib.auth.models import User
from rest_framework.test import APITestCase


class RunTestCase(APITestCase):
    def test_create_model_run(self):
        user = User.objects.create(username='User')
        run_1 = Run.objects.create(athlete=user, comment='my comment')
        run_2 = Run.objects.create(athlete=user)
                       
        self.assertEqual('User', run_1.athlete.username)
        self.assertEqual('my comment', run_1.comment)
        self.assertEqual('User', run_2.athlete.username)
        self.assertIsNone(run_2.comment)