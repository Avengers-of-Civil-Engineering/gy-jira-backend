from rest_framework import serializers, exceptions
from .models import AppImage, User, Project, ProjectUserSetting, Epic, Kanban, Task


class AppImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppImage
        fields = (
            'id',
            'width',
            'height',
            'img',
            'desc',
        )
        read_only_fields = (
            'id',
            'width',
            'height',
        )


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(min_length=5, max_length=20, required=True)
    avatar_id = serializers.CharField(required=False)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)
    password = serializers.CharField(max_length=191, write_only=True)
    avatar = AppImageSerializer(read_only=True)

    def create(self, validated_data):
        username = validated_data.get('username')
        user_tmp = User.objects.filter(username__iexact=username).first()
        if user_tmp is not None:
            raise serializers.ValidationError({'msg': '用户名已注册！'})

        avatar = None
        avatar_id = validated_data.get('avatar_id')
        if avatar_id:
            try:
                avatar = AppImage.objects.get(pk=avatar_id)
            except AppImage.DoesNotExist:
                raise serializers.ValidationError({'msg': f'avatar_id = {avatar_id} does not exist!'})

        phone_number = validated_data['phone_number']
        user_tmp = User.objects.filter(phone_number=phone_number).first()
        if user_tmp is not None:
            raise serializers.ValidationError({'msg': '手机号已注册!'})

        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data.get('email', None),
            first_name=validated_data['first_name'],
            phone_number=validated_data['phone_number'],
            avatar=avatar,
        )
        password = validated_data['password']
        user.set_password(password)
        user.save()
        return user

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'phone_number',
            'avatar_id',
            'avatar',
            'password',
        )
        read_only_fields = (
            'id',
            'avatar',
        )


class ProjectSerializer(serializers.ModelSerializer):
    person = UserSerializer(read_only=True)
    person_id = serializers.IntegerField(label='负责人ID')
    pin = serializers.SerializerMethodField()

    def get_pin(self, obj: Project):
        request = self.context.get('request')
        if request is None:
            return None
        user: User = request.user
        if user.is_anonymous:
            return None
        project_user_setting = ProjectUserSetting.objects.filter(user=user, project=obj).first()
        if project_user_setting is None:
            return None
        return project_user_setting.is_pinned

    class Meta:
        model = Project
        fields = (
            'id',
            'name',
            'person_id',
            'person',
            'organization',
            'pin',
            'create_at',
            'update_at',
        )
        read_only_fields = (
            'id',
            'person',
            'pin',
            'create_at',
            'update_at',
        )


class ProjectTogglePinSerializer(serializers.Serializer):
    new_val = serializers.BooleanField(label='是否收藏')


class EpicSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)
    project_id = serializers.IntegerField(label='项目ID')

    class Meta:
        model = Epic
        fields = (
            'id',
            'name',
            'project_id',
            'project',
            'start',
            'end',
            'create_at',
            'update_at'
        )
        read_only_fields = (
            'id',
            'project',
            'create_at',
            'update_at'
        )


class KanbanSerializer(serializers.ModelSerializer):
    project_id = serializers.IntegerField(label='项目ID')

    class Meta:
        model = Kanban
        fields = (
            'id',
            'name',
            'project_id',
            'rank',
            'create_at',
            'update_at'
        )
        read_only_fields = (
            'id',
            'project_id',
            'create_at',
            'update_at',
        )


class TaskSerializer(serializers.ModelSerializer):
    processor = UserSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)
    epic = EpicSerializer(read_only=True)
    kanban = KanbanSerializer(read_only=True)

    processor_id = serializers.IntegerField(label='经办人ID')
    project_id = serializers.IntegerField(label='项目ID')
    epic_id = serializers.IntegerField(label='史诗ID')
    kanban_id = serializers.IntegerField(label='看板ID')

    class Meta:
        model = Task
        fields = (
            'id',
            'name',
            'processor_id',
            'processor',
            'project_id',
            'project',
            'epic_id',
            'epic',
            'kanban_id',
            'kanban',
            'type_id',
            'note',
            'create_at',
            'update_at',
        )
        read_only_fields = (
            'id',
            'processor',
            'project',
            'epic',
            'kanban',
            'create_at',
            'update_at',
        )
