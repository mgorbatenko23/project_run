import json
from django.urls import reverse
from django.conf import settings
from rest_framework.test import APITestCase
from rest_framework import status


from app_run.models import Run


class CompanyDetailApiTestCase(APITestCase):
    def test_company_detail(self):
        url = reverse('company-detail')
        response = self.client.get(url)
        
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(settings.ABOUT_COMPANY, response.data)