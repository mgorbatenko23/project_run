from datetime import datetime
import json
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status

from app_run.models import(
    Run,
    AthleteInfo,
    Challenge,
    CollectibleItem,    
)    


class CompanyDetailApiTestCase(APITestCase):
    def test_company_detail(self):
        url = reverse('company-detail')
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(settings.ABOUT_COMPANY, response.data)


class RunApiTestCase(APITestCase):
    fixtures = ['data_db']

    def test_num_queries(self):
         with self.assertNumQueries(1):
            url = reverse('run-list')
            response = self.client.get(url)
            self.assertEqual(status.HTTP_200_OK, response.status_code)


class UserApiTestCase(APITestCase):
    fixtures = ['data_db']

    def test_filter_type_is_coach(self):
        with self.assertNumQueries(2):
            url = reverse('user-list')
            query_params = {'type': 'coach'}
            response = self.client.get(url, query_params=query_params)
            self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, len(response.data), response.data)
        for obj in response.data:
            self.assertEqual('coach', obj['type'])

    def test_filter_type_is_athlete(self):
        with self.assertNumQueries(2):
            url = reverse('user-list')
            query_params = {'type': 'athlete'}
            response = self.client.get(url, query_params=query_params)
            self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(5, len(response.data), response.data)
        for obj in response.data:
            self.assertEqual('athlete', obj['type'])

    def test_filter_type_is_wrong(self):
        with self.assertNumQueries(2):
            url = reverse('user-list')
            query_params = {'type': 'blablabla'}
            response = self.client.get(url, query_params=query_params)
            self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(7, len(response.data), response.data)
        for obj in response.data:
            self.assertTrue(obj['type'] in ['coach', 'athlete'])

    def test_without_filter(self):
        with self.assertNumQueries(2):
            url = reverse('user-list')
            response = self.client.get(url)
            self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(7, len(response.data), response.data)
        for obj in response.data:
            self.assertTrue(obj['type'] in ['coach', 'athlete'])


class RunStartApiTestCase(APITestCase):
    fixtures = ['data_db']

    def test_status_init_start(self):
        url = reverse('run-start', kwargs={'pk': 1})
        response = self.client.post(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        run = Run.objects.get(pk=1)
        self.assertEqual('in_progress', run.status)

    def test_status_in_progress_start(self):
        url = reverse('run-start', kwargs={'pk': 2})
        response = self.client.post(url)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        run = Run.objects.get(pk=2)
        self.assertEqual('in_progress', run.status)

    def test_status_in_finished_start(self):
        url = reverse('run-start', kwargs={'pk': 3})
        response = self.client.post(url)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        run = Run.objects.get(pk=3)
        self.assertEqual('finished', run.status)


class RunStopApiTestCase(APITestCase):
    fixtures = ['data_db']

    def test_status_init_stop(self):
        url = reverse('run-stop', kwargs={'pk': 1})
        response = self.client.post(url)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        run = Run.objects.get(pk=1)
        self.assertEqual('init', run.status)

    def test_status_in_progress_stop(self):
        url = reverse('run-stop', kwargs={'pk': 2})
        response = self.client.post(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        run = Run.objects.get(pk=2)
        self.assertEqual('finished', run.status)

    def test_status_in_finished_stop(self):
        url = reverse('run-stop', kwargs={'pk': 3})
        response = self.client.post(url)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        run = Run.objects.get(pk=3)
        self.assertEqual('finished', run.status)

    def test_calc_distance(self):
        url = reverse('run-stop', kwargs={'pk': 2})
        response = self.client.post(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        run = Run.objects.get(pk=2)
        self.assertEqual('finished', run.status)
        self.assertEqual(0.61, round(run.distance, 2))


class AthleteInfoApiTestCase(APITestCase):
    fixtures = ['data_db']

    def test_not_find_user(self):
        url = reverse('athlete_info-detail', kwargs={'id': 23})
        response = self.client.get(url)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        response = self.client.put(url)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_create_athlete_info_method_get(self):
        url = reverse('athlete_info-detail', kwargs={'id': 2})
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, AthleteInfo.objects.filter(athlete=2).count())

        athlete_info = AthleteInfo.objects.get(pk=2)
        self.assertEqual(athlete_info.pk, 2)
        self.assertEqual(athlete_info.goals, '')
        self.assertEqual(athlete_info.weight, None)

    def test_create_athlete_info_method_put(self):
        url = reverse('athlete_info-detail', kwargs={'id': 2})
        response = self.client.put(url)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(1, AthleteInfo.objects.filter(athlete=2).count())

        athlete_info = AthleteInfo.objects.get(pk=2)
        self.assertEqual(athlete_info.pk, 2)
        self.assertEqual(athlete_info.goals, '')
        self.assertEqual(athlete_info.weight, None)

    def test_get_athlete_info(self):
        url = reverse('athlete_info-detail', kwargs={'id': 1})
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual({'goals': 'цели нет, есть только путь',
                          'weight': 70,
                          'user_id': 1}, response.data, response.data)
        
    def test_update_athlete_info(self):
        url = reverse('athlete_info-detail', kwargs={'id': 1})
        response = self.client.put(url, data={'weight': 80})
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual({'goals': 'цели нет, есть только путь',
                          'weight': 80,
                          'user_id': 1}, response.data, response.data)


class ChallengeApiTestCase(APITestCase):
    fixtures = ['data_db']
    
    def test_create_challenge_10_run(self):
        url = reverse('run-stop', kwargs={'pk': 12})
        response = self.client.post(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, Challenge.objects.count())
        challenge = Challenge.objects.first()
        self.assertEqual(3, challenge.athlete_id)
        self.assertEqual('Сделай 10 Забегов!', challenge.full_name)

    def test_create_challenge_50_km(self):
        url = reverse('run-stop', kwargs={'pk': 13})
        response = self.client.post(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        challenge = Challenge.objects.get(full_name='Пробеги 50 километров!')
        self.assertEqual(3, challenge.athlete_id)


class FileUploadApiTestCase(APITestCase):
    def test_upload_file(self):
        path_file = settings.BASE_DIR / 'app_run' / 'tests' / 'upload_example.xlsx'
        with open(path_file, 'rb') as f_data:
            url = reverse('upload-file')
            response = self.client.post(url, data={'file': f_data})
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, CollectibleItem.objects.count())


class PositionApiTestCase(APITestCase):
    fixtures = ['data_db']
 
    def test_add_collectible_items(self):
        url = reverse('position-list')
        data = {'run': 14,
                'latitude': 20.0001,
                'longitude': 50.0001,
                'date_time': '2025-10-10T18:15:00.000000'}
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        user = User.objects.get(pk=5)
        self.assertEqual(1, user.items.count())
        artifact = user.items.get(uid='artifact1')
        self.assertTrue('artifact1', artifact.uid)