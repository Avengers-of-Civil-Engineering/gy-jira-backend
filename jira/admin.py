from django.contrib import admin

from .models import User, AppImage, Project, Kanban, Epic, ProjectUserSetting, Task


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(AppImage)
class AppImageAdmin(admin.ModelAdmin):
    pass


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass


@admin.register(Kanban)
class KanbanAdmin(admin.ModelAdmin):
    pass


@admin.register(Epic)
class EpicAdmin(admin.ModelAdmin):
    pass


@admin.register(ProjectUserSetting)
class ProjectUserSettingAdmin(admin.ModelAdmin):
    pass


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass
