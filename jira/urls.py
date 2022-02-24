from pprint import pprint
from django.urls import include, path

from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'images', views.AppImageViewSet)
router.register(r'projects', views.ProjectViewSet)
router.register(r'epics', views.EpicViewSet)
router.register(r'kanban', views.KanbanViewSet)
router.register(r'tasks', views.TaskViewSet)

pprint(router.get_urls())

urlpatterns = [
    path('', include(router.urls)),
    path('api-token-auth/', views.MyObtainAuthTokenAPI.as_view(), name="token_login"),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
