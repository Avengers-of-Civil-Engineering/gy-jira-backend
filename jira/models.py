from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class AppImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)

    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    img = models.ImageField(width_field='width', height_field='height')
    desc = models.CharField(max_length=191, blank=True, null=False, verbose_name="图片备注")

    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.img.name

    class Meta:
        verbose_name = verbose_name_plural = '图片'


class User(AbstractUser):
    phone_number = models.CharField(max_length=191, blank=True, null=True, verbose_name="手机号码", unique=True)
    avatar = models.ForeignKey(AppImage, on_delete=models.SET_NULL, db_constraint=False, null=True, blank=True)


class Project(models.Model):
    name = models.CharField(max_length=191, verbose_name='名称')
    person = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='负责人')
    organization = models.CharField(max_length=191, verbose_name='部门')

    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = verbose_name_plural = '项目'


class ProjectUserSetting(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='+')
    is_pinned = models.BooleanField(verbose_name='是否收藏')

    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = verbose_name_plural = '项目用户设置'


class Epic(models.Model):
    name = models.CharField(max_length=191)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='epics')
    start = models.DateTimeField(verbose_name='开始时间')
    end = models.DateTimeField(verbose_name='结束时间')

    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = verbose_name_plural = '史诗'


class Kanban(models.Model):
    name = models.CharField(max_length=191)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='kanbans')
    rank = models.IntegerField(verbose_name='排序参考值', default=0)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = verbose_name_plural = '看板'


class Task(models.Model):
    name = models.CharField(max_length=191, verbose_name='名称')
    processor = models.ForeignKey(User, verbose_name='经办人', blank=True, null=True, on_delete=models.SET_NULL, related_name='tasks')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    epic = models.ForeignKey(Epic, on_delete=models.SET_NULL, blank=True, null=True, related_name='tasks')
    kanban = models.ForeignKey(Kanban, on_delete=models.SET_NULL, blank=True, null=True, related_name='tasks')
    type_id = models.IntegerField(verbose_name='类型ID')
    note = models.TextField(verbose_name='说明', blank=True, null=False)

    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = verbose_name_plural = '任务'
