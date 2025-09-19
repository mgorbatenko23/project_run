import json
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status


from app_run.models import Run


class CompanyDetailApiTestCase(APITestCase):
    def test_company_detail(self):
        url = reverse('company-detail')
        response = self.client.get(url)
        
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(settings.ABOUT_COMPANY, response.data)


class RunViewSetApiTestCase(APITestCase):
    def setUp(self):
        self.user_1 = User.objects.create(username='User 1')
        self.run_1 = Run.objects.create(athlete=self.user_1, comment='comment 1')
        self.run_2 = Run.objects.create(athlete=self.user_1, comment='comment 11')
        self.run_1_created_at_to_str = self.run_1.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        self.run_2_created_at_to_str = self.run_2.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    
    def test_create(self):
        self.client.force_login(self.user_1)
        url = reverse('run-list')
        data = {'comment': 'first comment'}
        json_data = json.dumps(data)
        response = self.client.post(url,
                                    data=json_data,
                                    content_type='application/json')
        
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(self.user_1, Run.objects.last().athlete)

    def test_update(self):
        self.client.force_login(self.user_1)
        url = reverse('run-detail', kwargs={'pk': self.run_1.pk})
        data = {'comment': 'comment 2'}
        json_data = json.dumps(data)
        response = self.client.put(url,
                                    data=json_data,
                                    content_type='application/json')
        
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.run_1.refresh_from_db()
        self.assertEqual('comment 2', self.run_1.comment)

    def test_partial_update(self):
        self.client.force_login(self.user_1)
        url = reverse('run-detail', kwargs={'pk': self.run_1.pk})
        data = {'comment': 'comment 2'}
        json_data = json.dumps(data)
        response = self.client.patch(url,
                                    data=json_data,
                                    content_type='application/json')
        
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.run_1.refresh_from_db()
        self.assertEqual('comment 2', self.run_1.comment)

    def test_destroy(self):
        self.client.force_login(self.user_1)
        url = reverse('run-detail', kwargs={'pk': self.run_1.pk})
        response = self.client.delete(url)
        
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        with self.assertRaises(Run.DoesNotExist):
            Run.objects.get(pk=self.run_1.pk)
    
    def test_retrive(self):
        self.client.force_login(self.user_1)
        url = reverse('run-detail', kwargs={'pk': self.run_1.pk})
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        expected_data = {'id': self.run_1.id,
                          'comment': self.run_1.comment,
                          'created_at': self.run_1_created_at_to_str}
        self.assertEqual(expected_data, response.data)

    def test_list(self):
        self.client.force_login(self.user_1)
        url = reverse('run-list')
        response = self.client.get(url)

        self.assertEqual(status.HTTP_200_OK, response.status_code)

        expected_data = [{'id': self.run_1.id,
                          'comment': self.run_1.comment,
                          'created_at': self.run_1_created_at_to_str},
                          {'id': self.run_2.id,
                           'comment': self.run_2.comment,
                           'created_at': self.run_2_created_at_to_str}]

        self.assertEqual(expected_data, response.data)