from rest_framework import authentication
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import mixins
from rest_framework import exceptions

from .models import (
    User,
    AppImage,
    Project,
    ProjectUserSetting,
)

from .serializers import (
    UserSerializer,
    AppImageSerializer,
    ProjectSerializer,
)


class AllowPostByAnyOne(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        else:
            return bool(request.user and request.user.is_authenticated)


class UserViewSet(mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    authentication_classes = (
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    )
    permission_classes = (
        AllowPostByAnyOne,
    )

    lookup_field = 'username'

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def retrieve(self, request: Request, *args, **kwargs):
        if request.user.is_anonymous:
            raise exceptions.PermissionDenied

        user_obj: User = self.get_object()
        if user_obj.id != request.user.id:
            raise exceptions.PermissionDenied

        return super().retrieve(request, *args, **kwargs)

    @action(methods=['GET', ], detail=False, url_path="about-me")
    def about_me(self, request: Request, **kwargs):
        if request.user.is_anonymous:
            raise exceptions.PermissionDenied
        return Response(UserSerializer(instance=request.user, context={'request': request}).data)


class AppImageViewSet(mixins.RetrieveModelMixin, mixins.CreateModelMixin, GenericViewSet):
    authentication_classes = (
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticated,
    )

    queryset = AppImage.objects.all()
    serializer_class = AppImageSerializer


class MyObtainAuthTokenAPI(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(instance=user, context={'request': request}).data,
        })


class ProjectViewSet(ModelViewSet):
    authentication_classes = (
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticated,
    )

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    @action(methods=['POST', ], detail=True, url_path="toggle-pin")
    def toggle_pin(self, request: Request, **kwargs):
        project: Project = self.get_object()
        user: User = request.user
        new_val = None
        try:
            new_val = int(request.data.get('newVal'))
        except Exception:
            pass
        if new_val not in (0, 1):
            raise exceptions.ValidationError({'newVal': 'should be 0 or 1'})

        project_user = ProjectUserSetting.objects.filter(project=project, user=user).first()
        if project_user is None:
            project_user = ProjectUserSetting(
                project=project,
                user=user,
                is_pinned=(new_val == 1)
            )
        else:
            project_user.is_pinned = (new_val == 1)
        project_user.save()

        serializer = ProjectSerializer(instance=project, context=self.get_serializer_context())

        return Response(serializer.data)
