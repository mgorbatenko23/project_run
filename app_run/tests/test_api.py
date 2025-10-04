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
    Position,
    CollectibleItem,    
)    


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
        with self.assertNumQueries(2):
            url = reverse('user-list')
            query_params = {'type': 'coach'}
            response = self.client.get(url, query_params=query_params)
            self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.data))
        self.assertEqual(self.coach.id, 
                         response.data[0].get('id'))

    def test_filter_type_is_athlete(self):
        with self.assertNumQueries(2):
            url = reverse('user-list')
            query_params = {'type': 'athlete'}
            response = self.client.get(url, query_params=query_params)
            self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.data))
        self.assertEqual(self.athlete.id,
                         response.data[0].get('id'))

    def test_filter_type_is_wrong(self):
        with self.assertNumQueries(2):
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
        with self.assertNumQueries(2):
            url = reverse('user-list')
            response = self.client.get(url)
            self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, len(response.data))

        expected_user_id_list = {self.athlete.id: '', self.coach.id: ''}
        expected_user_id_list.pop(response.data[0].pop('id'))
        expected_user_id_list.pop(response.data[1].pop('id'))
        self.assertEqual(0, len(expected_user_id_list))


class RunStartApiTestCase(APITestCase):
    def setUp(self):
        user = User.objects.create(username='user')
        self.run_status_init = Run.objects.create(comment='comment',
                                             athlete=user)
        self.run_status_in_progress = Run.objects.create(comment='comment',
                                                         athlete=user,
                                                         status='in_progress')
        self.run_status_finished = Run.objects.create(comment='comment',
                                                      athlete=user,
                                                      status='finished')

    def test_status_init_start(self):
        url = reverse('run-start', kwargs={'pk': self.run_status_init.pk})
        response = self.client.post(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.run_status_init.refresh_from_db()
        self.assertEqual('in_progress', self.run_status_init.status)

    def test_status_in_progress_start(self):
        url = reverse('run-start', kwargs={'pk': self.run_status_in_progress.pk})
        response = self.client.post(url)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.run_status_in_progress.refresh_from_db()
        self.assertEqual('in_progress', self.run_status_in_progress.status)

    def test_status_in_finished_start(self):
        url = reverse('run-start', kwargs={'pk': self.run_status_finished.pk})
        response = self.client.post(url)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.run_status_finished.refresh_from_db()
        self.assertEqual('finished', self.run_status_finished.status)


class RunStopApiTestCase(APITestCase):
    def setUp(self):
        user = User.objects.create(username='user')
        self.run_status_init = Run.objects.create(comment='comment',
                                                  athlete=user)
        self.run_status_in_progress = Run.objects.create(comment='comment',
                                                         athlete=user,
                                                         status='in_progress')
        self.run_status_finished = Run.objects.create(comment='comment',
                                                      athlete=user,
                                                      status='finished')

        Position.objects.create(run=self.run_status_in_progress,
                                latitude=54.7216,
                                longitude=20.5247)
        Position.objects.create(run=self.run_status_in_progress,
                                latitude=54.7722,
                                longitude=20.5470)
        Position.objects.create(run=self.run_status_in_progress,
                                latitude=54.9588,
                                longitude=20.4729)

    def test_status_init_start(self):
        url = reverse('run-stop', kwargs={'pk': self.run_status_init.pk})
        response = self.client.post(url)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.run_status_init.refresh_from_db()
        self.assertEqual('init', self.run_status_init.status)

    def test_status_in_progress_start(self):
        url = reverse('run-stop', kwargs={'pk': self.run_status_in_progress.pk})
        response = self.client.post(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.run_status_in_progress.refresh_from_db()
        self.assertEqual('finished', self.run_status_in_progress.status)

    def test_status_in_finished_start(self):
        url = reverse('run-stop', kwargs={'pk': self.run_status_finished.pk})
        response = self.client.post(url)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.run_status_finished.refresh_from_db()
        self.assertEqual('finished', self.run_status_finished.status)

    def test_calc_distance(self):
        url = reverse('run-stop', kwargs={'pk': self.run_status_in_progress.pk})
        response = self.client.post(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.run_status_in_progress.refresh_from_db()
        self.assertEqual('finished', self.run_status_in_progress.status)
        self.assertTrue(self.run_status_in_progress.distance > 0,
                        self.run_status_in_progress.distance)


class AthleteInfoApiTestCase(APITestCase):
    def setUp(self):
        self.user_1 = User.objects.create(username='user 1')
        self.user_2 = User.objects.create(username='user 2')
        self.athlete_info = AthleteInfo.objects.create(athlete=self.user_2,
                                                       goals='цели нет, есть только путь',
                                                       weight=70)

    def test_not_find_user(self):
        url = reverse('athlete_info-detail', kwargs={'id': 23})
        response = self.client.get(url)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        response = self.client.put(url)
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_create_athlete_info_method_get(self):
        url = reverse('athlete_info-detail', kwargs={'id': self.user_1.id})
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, AthleteInfo.objects.filter(athlete=self.user_1.id).count())

        athlete_info = AthleteInfo.objects.first()
        self.assertEqual(athlete_info.pk, self.user_1.pk)
        self.assertEqual(athlete_info.goals, '')
        self.assertEqual(athlete_info.weight, None)

    def test_create_athlete_info_method_put(self):
        url = reverse('athlete_info-detail', kwargs={'id': self.user_1.id})
        response = self.client.put(url)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(1, AthleteInfo.objects.filter(athlete=self.user_1.id).count())

        athlete_info = AthleteInfo.objects.first()
        self.assertEqual(athlete_info.pk, self.user_1.pk)
        self.assertEqual(athlete_info.goals, '')
        self.assertEqual(athlete_info.weight, None)

    def test_get_athlete_info(self):
        url = reverse('athlete_info-detail', kwargs={'id': self.user_2.id})
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual({'goals': 'цели нет, есть только путь',
                          'weight': 70,
                          'user_id': self.user_2.pk}, response.data)
        
    def test_update_athlete_info(self):
        url = reverse('athlete_info-detail', kwargs={'id': self.user_2.id})
        response = self.client.put(url, data={'weight': 80})
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.athlete_info.refresh_from_db()
        self.assertEqual({'goals': 'цели нет, есть только путь',
                          'weight': 80,
                          'user_id': self.user_2.pk}, response.data)


class ChallengeApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='user')
    
    def test_create_challenge_10_run(self):
        for i in range(9):
            Run.objects.create(athlete=self.user,
                               comment=f'comment {i}',
                               status='finished')
        run = Run.objects.create(athlete=self.user,
                               comment='comment 10',
                               status='in_progress')
        url = reverse('run-stop', kwargs={'pk': run.pk})
        response = self.client.post(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, Challenge.objects.count())
        challenge = Challenge.objects.first()
        self.assertEqual(self.user, challenge.athlete)
        self.assertEqual('Сделай 10 Забегов!', challenge.full_name)

    def test_create_challenge_50_km(self):
        run = Run.objects.create(athlete=self.user,
                                 comment='comment 10',
                                 status='in_progress')
        Position.objects.create(run=run,
                                latitude=54.7216,
                                longitude=20.5247)
        Position.objects.create(run=run,
                                latitude=54.6538,
                                longitude=21.3477)
        url = reverse('run-stop', kwargs={'pk': run.pk})
        response = self.client.post(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        challenge = Challenge.objects.first()
        self.assertEqual(self.user, challenge.athlete)
        self.assertEqual('Пробеги 50 километров!', challenge.full_name)


class FileUploadApiTestCase(APITestCase):
    def test_upload_file(self):
        path_file = settings.BASE_DIR / 'app_run' / 'tests' / 'upload_example.xlsx'
        with open(path_file, 'rb') as f_data:
            url = reverse('upload-file')
            response = self.client.post(url, data={'file': f_data})
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(2, CollectibleItem.objects.count())


class PositionApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='user')
        self.run = Run.objects.create(athlete=self.user,
                                      comment='comment 10',
                                      status='in_progress')
        CollectibleItem.objects.create(name='artifact 1',
                                       latitude='20.0001',
                                       longitude='50.0001',
                                       picture='https://example.com/',
                                       value=1)
        CollectibleItem.objects.create(name='artifact 2',
                                       latitude='21.0001',
                                       longitude='51.0001',
                                       picture='https://example.com/',
                                       value=1)

 
    def test_add_collectible_items(self):
        url = reverse('position-list')
        data = {'run': self.run.pk,
                'latitude': 20.0,
                'longitude': 50.0}
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.user.refresh_from_db()
        self.assertEqual(1, self.user.items.count())
        artifact = self.user.items.first()
        self.assertEqual('artifact 1', artifact.name)