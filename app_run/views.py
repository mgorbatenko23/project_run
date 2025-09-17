from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view()
def detail_company(request):
    return Response(settings.ABOUT_COMPANY)