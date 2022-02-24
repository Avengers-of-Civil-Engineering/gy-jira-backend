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
    list_filter = ('project',)
    list_display = ('project', 'name', 'rank', 'update_at')


@admin.register(Epic)
class EpicAdmin(admin.ModelAdmin):
    list_filter = ('project',)


@admin.register(ProjectUserSetting)
class ProjectUserSettingAdmin(admin.ModelAdmin):
    list_filter = ('project', 'user')
    list_display = ('project', 'user', 'is_pinned')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_filter = ('project',)
