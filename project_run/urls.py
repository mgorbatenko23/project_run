from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework.routers import DefaultRouter

from  app_run import views


router = DefaultRouter()
router.register(r'api/runs', views.RunViewSet)
router.register(r'api/users', views.UserViewSet)
router.register(r'api/positions', views.PositionViewSet)
router.register(r'api/collectible_item', views.CollectibleItemView)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/company_details/', views.detail_company, name='company-detail'),
    path('', include(router.urls)),
    path('api/runs/<int:pk>/start/', views.RunViewStart.as_view(), name='run-start'),
    path('api/runs/<int:pk>/stop/', views.RunViewStop.as_view(), name='run-stop'),
    path('api/athlete_info/<int:id>/', views.AthleteInfoView.as_view(), name='athlete_info-detail'),
    path('api/challenges/', views.ChallengeView.as_view(), name='challenge-list'),
    path('api/upload_file/', views.FileUploadView.as_view(), name='upload-file'),
    path('api/subscribe_to_coach/<int:id>/', views.SubscribeView.as_view(), name='subscribe-create'),
    path('api/challenges_summary/', views.ChallengeSummaryView.as_view(), name='challenge-summary'),
]