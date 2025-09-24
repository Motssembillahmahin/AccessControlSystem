from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import AccessLog

class AccessLogTests(APITestCase):
    def setUp(self):
        self.access_log = AccessLog.objects.create(
            card_id="C1001",
            door_name="Main Entrance",
            access_granted=True
        )

    def test_create_access_log(self):
        url = reverse('accesslog-list')
        data = {
            'card_id': 'C1002',
            'door_name': 'Side Door',
            'access_granted': False
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AccessLog.objects.count(), 2)

    def test_get_access_logs(self):
        url = reverse('accesslog-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_single_access_log(self):
        url = reverse('accesslog-detail', args=[self.access_log.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['card_id'], 'C1001')

    def test_update_access_log(self):
        url = reverse('accesslog-detail', args=[self.access_log.id])
        data = {
            'card_id': 'C1001',
            'door_name': 'Main Entrance Updated',
            'access_granted': False
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.access_log.refresh_from_db()
        self.assertEqual(self.access_log.door_name, 'Main Entrance Updated')

    def test_delete_access_log(self):
        url = reverse('accesslog-detail', args=[self.access_log.id])
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(AccessLog.objects.count(), 0)

    def test_filter_by_card_id(self):
        url = reverse('accesslog-list') + '?card_id=C1001'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['card_id'], 'C1001')