import json
import logging
import os
from pprint import pprint
from random import shuffle

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

logger = logging.getLogger(__name__)


class TestGenMockData(TestCase):
    def test_gen(self):
        from .generate_mock_data import generate_mock_data
        from .serializers import TaskSerializer
        ret = generate_mock_data()
        tasks_json = json.dumps(TaskSerializer(ret['tasks'], many=True).data, indent=2, ensure_ascii=False)
        print(tasks_json)


def dict_to_str(d):
    return json.dumps(d, indent=2, ensure_ascii=False)


class TestSort(APITestCase):
    def setUp(self) -> None:
        super().setUp()

        from .generate_mock_data import generate_mock_data, MOCK_USER_PASS

        generate_mock_data()

        self.client.login(username='aweffr', password=MOCK_USER_PASS)

    def test_task_list(self):
        url = reverse('task-list')
        resp = self.client.get(url, format='json')
        logger.info("GET %s data return: %s", resp.wsgi_request.get_raw_uri(), dict_to_str(resp.data))

    def test_task_reorder_with_tasks(self):
        from .models import Task

        url = reverse('task-reorder')

        task_ids = [t.id for t in Task.objects.all()]

        for i in range(3):
            for _type in ('before', 'after'):
                shuffle(task_ids)

                task1 = Task.objects.get(pk=task_ids[0])
                task2 = Task.objects.get(pk=task_ids[1])

                logger.info(
                    'before sort, task1.rank=%.1f, task1.kanban=%d, task2.rank=%.1f, task2.kanban=%d',
                    task1.rank, task1.kanban_id, task2.rank, task2.kanban_id,
                )

                payload = {
                    'from_id': task1.id,
                    'reference_id': task2.id,
                    'type': _type,
                    'from_kanban_id': task1.kanban_id,
                    'to_kanban_id': task2.kanban_id,
                }

                resp = self.client.post(url, payload, format='json')
                logger.info("GET %s data return: %s", resp.wsgi_request.get_raw_uri(), dict_to_str(resp.data))

                task1 = Task.objects.get(pk=task1.id)
                task2 = Task.objects.get(pk=task2.id)
                logger.info(
                    'after sort, task1.rank=%.1f, task1.kanban=%d, task2.rank=%.1f, task2.kanban=%d',
                    task1.rank, task1.kanban_id, task2.rank, task2.kanban_id,
                )

                self.assertEqual(task1.kanban_id, task2.kanban_id)
                if _type == 'before':
                    self.assertLess(task1.rank, task2.rank)
                if _type == 'after':
                    self.assertGreater(task1.rank, task2.rank)
