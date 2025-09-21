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


class RunApiTestCase(APITestCase):
    def setUp(self):
        self.user_1 = User.objects.create(username='user 1')
        self.user_2 = User.objects.create(username='user 2')
        self.user_3 = User.objects.create(username='user 3')
        self.run_1 = Run.objects.create(comment='comment 1',
                                        athlete=self.user_1)
        self.run_2 = Run.objects.create(comment='comment 2',
                                        athlete=self.user_2)
        self.run_3 = Run.objects.create(comment='comment 3',
                                        athlete=self.user_3)
    
    def test_num_queries(self):
         with self.assertNumQueries(1):
            url = reverse('run-list')
            response = self.client.get(url)
            self.assertEqual(status.HTTP_200_OK, response.status_code)


class UserApiTestCase(APITestCase):
    def setUp(self):
        self.coach = User.objects.create(username='coach 1',
                                         is_staff=True)
        self.athlete = User.objects.create(username='athlete 1',
                                           is_staff=False)
        self.admin = User.objects.create(username='admin',
                                           is_staff=True,
                                           is_superuser=True)

    def test_filter_type_is_coach(self):
        with self.assertNumQueries(1):
            url = reverse('user-list')
            query_params = {'type': 'coach'}
            response = self.client.get(url, query_params=query_params)
            self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.data))
        self.assertEqual(self.coach.id, 
                         response.data[0].get('id'))

    def test_filter_type_is_athlete(self):
        with self.assertNumQueries(1):
            url = reverse('user-list')
            query_params = {'type': 'athlete'}
            response = self.client.get(url, query_params=query_params)
            self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.data))
        self.assertEqual(self.athlete.id,
                         response.data[0].get('id'))

    def test_filter_type_is_wrong(self):
        with self.assertNumQueries(1):
            url = reverse('user-list')
            query_params = {'type': 'blablabla'}
            response = self.client.get(url, query_params=query_params)
            self.assertEqual(status.HTTP_200_OK, response.status_code)            
        self.assertEqual(2, len(response.data))

        expected_user_id_list = {self.athlete.id: '', self.coach.id: ''}
        expected_user_id_list.pop(response.data[0].pop('id'))
        expected_user_id_list.pop(response.data[1].pop('id'))
        self.assertEqual(0, len(expected_user_id_list))

    def test_without_filter(self):
        with self.assertNumQueries(1):
            url = reverse('user-list')
            response = self.client.get(url)
            self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, len(response.data))

        expected_user_id_list = {self.athlete.id: '', self.coach.id: ''}
        expected_user_id_list.pop(response.data[0].pop('id'))
        expected_user_id_list.pop(response.data[1].pop('id'))
        self.assertEqual(0, len(expected_user_id_list))