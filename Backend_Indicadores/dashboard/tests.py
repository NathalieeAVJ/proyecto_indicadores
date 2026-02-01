from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from ventas.models import Sale, SimCard, Customer 
from incidencias.models import Incident, FailureType
from inventory.models import PhoneNumber, SparePart

User = get_user_model()

class DashboardStatsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        
        # Create Dummy Data
        # Incident
        self.phone = PhoneNumber.objects.create(number='555-0100', description='Test Phone')
        self.failure_type = FailureType.objects.create(name='Sin Señal')
        Incident.objects.create(
            title='Test Incident',
            description='Test Description',
            phone_number=self.phone,
            failure_type=self.failure_type,
            start_date=timezone.now(),
            created_by=self.user,
            status='pending'
        )

        # SparePart (Low Stock)
        SparePart.objects.create(
            code='SP001',
            name='Test Part',
            quantity_in_stock=2,
            minimum_stock=5
        )

    def test_get_dashboard_summary(self):
        # We need to make sure the URL name matches what we defined in urls.py
        url = reverse('dashboard-summary') 
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('incidents_open', response.data)
        self.assertIn('monthly_sales', response.data)
        self.assertIn('low_stock_items', response.data)
        
        # Check values
        self.assertEqual(response.data['incidents_open'], 1)
        self.assertEqual(response.data['low_stock_items'], 1)
