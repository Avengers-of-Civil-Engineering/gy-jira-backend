from pprint import pprint
from django.urls import include, path

from .views import MyObtainAuthTokenAPI, UserViewSet, AppImageViewSet
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'images', views.AppImageViewSet)

pprint(router.get_urls())


urlpatterns = [
    path('', include(router.urls)),
    path('api-token-auth/', MyObtainAuthTokenAPI.as_view(), name="token_login"),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
