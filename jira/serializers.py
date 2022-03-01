import logging

from rest_framework import serializers, exceptions
from rest_framework.request import Request

from .models import AppImage, User, Project, ProjectUserSetting, Epic, Kanban, Task

logger = logging.getLogger(__name__)


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

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if self.context.get('project_no_person'):
            del ret['person']
        return ret

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


# noinspection PyAbstractClass
class ProjectTogglePinSerializer(serializers.Serializer):
    new_val = serializers.BooleanField(label='是否收藏')


class EpicSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)
    project_id = serializers.IntegerField(label='项目ID')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if self.context.get('epic_no_project'):
            del ret['project']
        return ret

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
            'rank',
            'create_at',
            'update_at',
        )


class TaskSerializer(serializers.ModelSerializer):
    reporter = UserSerializer(read_only=True)
    processor = UserSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)
    epic = EpicSerializer(read_only=True)
    kanban = KanbanSerializer(read_only=True)

    reporter_id = serializers.IntegerField(label='报告人ID', required=False, allow_null=True)
    project_id = serializers.IntegerField(label='项目ID')
    processor_id = serializers.IntegerField(label='经办人ID', required=False, allow_null=True)
    epic_id = serializers.IntegerField(label='史诗ID', required=False, allow_null=True)
    kanban_id = serializers.IntegerField(label='看板ID', required=False, allow_null=True)
    type_id = serializers.IntegerField(label="类型ID", default=1)

    def create(self, validated_data):
        task: Task = super().create(validated_data)
        request: Request = self.context.get('request')

        if request is not None and not request.user.is_anonymous:
            task.reporter = request.user
            task.save()

        return task

    class Meta:
        model = Task
        fields = (
            'id',
            'name',
            'reporter_id',
            'reporter',
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
            'rank',
            'create_at',
            'update_at',
        )
        read_only_fields = (
            'id',
            'reporter',
            'processor',
            'project',
            'epic',
            'kanban',
            'rank',
            'create_at',
            'update_at',
        )


# noinspection PyAbstractClass
class SortParamsSerializer(serializers.Serializer):
    from_id = serializers.IntegerField(required=True, label='要重新排序的 itemID')
    reference_id = serializers.IntegerField(required=False, label="目标itemID", allow_null=True, default=None)
    type = serializers.ChoiceField(choices=(("before", "之前"), ("after", "之后")))

    from_kanban_id = serializers.IntegerField(required=False, label="移动task时的源kanbanID", allow_null=True, default=None)
    to_kanban_id = serializers.IntegerField(required=False, label="移动task时的目标kanbanID", allow_null=True, default=None)

    def sort_kanban(self, validated_data):
        from_id = validated_data['from_id']
        reference_id = validated_data['reference_id']
        type = validated_data['type']

        if reference_id is None:
            raise serializers.ValidationError({'msg': 'referenceId is required!'})

        kanban_from = Kanban.objects.get(pk=from_id)

        kanban_to = Kanban.objects.get(pk=reference_id)

        if type == 'before':
            hi = kanban_to.rank
            kanban_to_before = Kanban.objects.filter(rank__lt=kanban_to.rank).first()
            if kanban_to_before is None:
                lo = hi - 100.0
            else:
                lo = kanban_to_before.rank
            new_rank = float(lo + hi) / 2
        elif type == 'after':
            lo = kanban_to.rank
            kanban_to_after = Kanban.objects.filter(rank__gt=kanban_to.rank).first()
            if kanban_to_after is None:
                hi = lo + 100.0
            else:
                hi = kanban_to_after.rank
            new_rank = float(lo + hi) / 2
        else:
            raise serializers.ValidationError({'msg': 'type is invalid'})

        kanban_from.rank = new_rank
        kanban_from.save()

        return kanban_from

    def sort_task(self, validated_data):
        from_id = validated_data['from_id']
        reference_id = validated_data['reference_id']
        type = validated_data['type']
        from_kanban_id = validated_data['from_kanban_id']
        to_kanban_id = validated_data['to_kanban_id']

        if from_kanban_id is None or to_kanban_id is None:
            raise serializers.ValidationError({'msg': 'fromKanbanId, toKanbanId is required!'})

        try:
            kanban_from = Kanban.objects.get(pk=from_kanban_id)
        except Kanban.DoesNotExist:
            raise serializers.ValidationError({'msg': f'fromKanbanId is invalid, fromKanbanId={from_kanban_id}'})

        try:
            kanban_to = Kanban.objects.get(pk=to_kanban_id)
        except Kanban.DoesNotExist:
            raise serializers.ValidationError({'msg': f'toKanbanId is invalid, toKanbanId={to_kanban_id}'})

        task_from = Task.objects.get(pk=from_id)

        if reference_id is None:
            new_rank = 100
        else:
            task_to = Task.objects.get(pk=reference_id)
            if type == 'before':
                hi = task_to.rank
                task_to_before = Task.objects.filter(rank__lt=task_to.rank, kanban=task_to.kanban).first()
                if task_to_before is None:
                    lo = hi - 100.0
                else:
                    lo = task_to_before.rank
                new_rank = float(lo + hi) / 2
            elif type == 'after':
                lo = task_to.rank
                task_to_after = Task.objects.filter(rank__gt=task_to.rank, kanban=task_to.kanban).first()
                if task_to_after is None:
                    hi = lo + 100.0
                else:
                    hi = task_to_after.rank
                new_rank = float(lo + hi) / 2
            else:
                raise serializers.ValidationError({'msg': 'type is invalid'})

        task_from.kanban = kanban_to
        task_from.rank = new_rank
        task_from.save()

        return task_from
