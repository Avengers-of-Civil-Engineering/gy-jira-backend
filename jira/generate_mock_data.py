import os
from random import choice

from django.utils import timezone
from datetime import datetime, time as dt_time, timedelta
from dateutil import tz

from .models import User, Project, Kanban, Epic, Task

tz_shanghai = tz.gettz('Asia/Shanghai')

MOCK_USER_PASS = os.environ.get('MOCK_USER_PASS', 'thisisunsafe')


def clear_data():
    User.objects.all().delete()
    Project.objects.all().delete()
    Kanban.objects.all().delete()
    Epic.objects.all().delete()
    Task.objects.all().delete()


def generate_mock_data():
    user1 = User(username='aweffr', first_name='aweffr', email='', phone_number='1234567890')
    user2 = User(username='guying', first_name='guying', email='', phone_number='1234567891')

    user1.set_password(MOCK_USER_PASS)
    user2.set_password(MOCK_USER_PASS)

    user1.save()
    user2.save()

    project = Project(
        name='快递管理',
        organization='快递组',
        person=user1
    )
    project.save()

    kanbans = []
    for kanban_name in ('待完成', '开发中', '已完成'):
        kanban = Kanban(
            name=kanban_name,
            project=project
        )
        kanban.save()
        kanbans.append(kanban)

    epics = []
    for epic_name in ('骑手物料表单开发', '骑手地图开发'):
        dt_lo = timezone.datetime.combine(datetime.now().date(), dt_time(0, 0), tzinfo=tz_shanghai)
        dt_hi = dt_lo + timedelta(days=21)
        epic = Epic(
            name=epic_name,
            project=project,
            start=dt_lo,
            end=dt_hi
        )
        epic.save()
        epics.append(epic)

    task_basic_info = [
        ('管理登录界面开发', '请使用JWT完成', 2, choice(epics)),
        ('性能优化', '', 1, choice(epics)),
        ('单元测试', '也就 pet projects 能写写单测~', 1, choice(epics)),
        ('自测', '体现自己的责任心与人品的时候到了~', 1, choice(epics)),
        ('权限管理界面开发', '', 2, choice(epics)),
        ('管理注册界面开发', '请尽快完成', 1, choice(epics)),
        ('UI开发', '', 1, choice(epics)),
    ]

    tasks = []
    for name, note, type_id, epic in task_basic_info:
        task = Task(
            project=project,
            reporter=choice((user1, user2)),
            type_id=type_id,
            epic=epic,
            kanban=choice(kanbans),
            name=name,
            note=note,
            processor=choice((user1, user2, None))
        )
        task.save()
        tasks.append(task)

    return {
        'users': [user1, user2],
        'kanbans': kanbans,
        'epics': epics,
        'tasks': tasks,
    }
