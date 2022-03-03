from rest_framework import authentication
from rest_framework import exceptions
from rest_framework import mixins
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django_filters import rest_framework as filters

from .authentication import MySessionAuthentication

from .models import (
    User,
    AppImage,
    Project,
    ProjectUserSetting, Epic, Kanban, Task,
)
from .serializers import (
    UserSerializer,
    AppImageSerializer,
    ProjectSerializer,
    EpicSerializer,
    KanbanSerializer,
    TaskSerializer, ProjectTogglePinSerializer, SortParamsSerializer
)


class AllowPostByAnyOne(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        else:
            return bool(request.user and request.user.is_authenticated)


class UserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    authentication_classes = (
        MySessionAuthentication,
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
        MySessionAuthentication,
        authentication.TokenAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
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


class ProjectFilter(filters.FilterSet):
    name = filters.CharFilter(label='按名称搜索', field_name='name', lookup_expr='icontains')
    personId = filters.NumberFilter(field_name='person_id', lookup_expr='exact')

    createAtMin = filters.DateTimeFilter(field_name='create_at', lookup_expr='gte')
    createAtMax = filters.DateTimeFilter(field_name='create_at', lookup_expr='lte')

    class Meta:
        model = Project
        fields = (
            'organization',
        )


class ProjectViewSet(ModelViewSet):
    authentication_classes = (
        MySessionAuthentication,
        authentication.TokenAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )
    filterset_class = ProjectFilter

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_serializer_class(self):
        if self.action == 'toggle_pin':
            return ProjectTogglePinSerializer
        return super().get_serializer_class()

    @action(methods=['POST', ], detail=True, url_path="toggle-pin")
    def toggle_pin(self, request: Request, **kwargs):
        project: Project = self.get_object()
        user: User = request.user

        req_serializer: ProjectTogglePinSerializer = self.get_serializer(data=request.data)
        if req_serializer.is_valid(raise_exception=True):
            new_val = req_serializer.validated_data['new_val']
            project_user = ProjectUserSetting.objects.filter(project=project, user=user).first()
            if project_user is None:
                project_user = ProjectUserSetting(
                    project=project,
                    user=user,
                    is_pinned=new_val
                )
            else:
                project_user.is_pinned = new_val
            project_user.save()

            serializer = ProjectSerializer(instance=project, context=self.get_serializer_context())

            return Response(serializer.data)


# noinspection DuplicatedCode
class EpicFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    projectId = filters.NumberFilter(label='项目ID', field_name='project_id', lookup_expr='exact')

    class Meta:
        model = Epic
        fields = ()


class EpicViewSet(ModelViewSet):
    authentication_classes = (
        MySessionAuthentication,
        authentication.TokenAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )

    queryset = Epic.objects.all()
    serializer_class = EpicSerializer
    filterset_class = EpicFilter


# noinspection DuplicatedCode
class KanbanFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    projectId = filters.NumberFilter(label='项目ID', field_name='project_id', lookup_expr='exact')

    class Meta:
        model = Kanban
        fields = ()


class KanbanViewSet(ModelViewSet):
    authentication_classes = (
        MySessionAuthentication,
        authentication.TokenAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )

    queryset = Kanban.objects.all()
    serializer_class = KanbanSerializer
    filterset_class = KanbanFilter

    def get_serializer_class(self):
        if self.action == 'reorder':
            return SortParamsSerializer
        return super().get_serializer_class()

    @action(methods=['POST', ], detail=False)
    def reorder(self, request: Request):
        serializer: SortParamsSerializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.sort_kanban(serializer.validated_data)
            return Response({'msg': 'sort kanbans finish!', 'sortParams': serializer.validated_data})


class TaskFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    typeId = filters.NumberFilter(field_name='type_id', lookup_expr='exact')
    projectId = filters.NumberFilter(label='项目ID', field_name='project_id', lookup_expr='exact')
    processorId = filters.NumberFilter(label='经办人ID', field_name='processor_id', lookup_expr='exact')
    epicId = filters.NumberFilter(label='任务组ID', field_name='epic_id', lookup_expr='exact')
    kanbanId = filters.NumberFilter(label='看板ID', field_name='kanban_id', lookup_expr='exact')

    class Meta:
        model = Task
        fields = ()


class TaskViewSet(ModelViewSet):
    authentication_classes = (
        MySessionAuthentication,
        authentication.TokenAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
    )

    queryset = Task.objects.select_related('project', 'project__person', 'epic', 'epic__project', 'kanban').all()
    serializer_class = TaskSerializer
    filterset_class = TaskFilter

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['epic_no_project'] = True
        ctx['project_no_person'] = True
        return ctx

    def get_serializer_class(self):
        if self.action == 'reorder':
            return SortParamsSerializer
        return super().get_serializer_class()

    @action(methods=['POST', ], detail=False)
    def reorder(self, request: Request):
        serializer: SortParamsSerializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.sort_task(serializer.validated_data)
            return Response({'msg': 'sort tasks finish!', 'sortParams': serializer.validated_data})
