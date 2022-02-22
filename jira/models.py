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
