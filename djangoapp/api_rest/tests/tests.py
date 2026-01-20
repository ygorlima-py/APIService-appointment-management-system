from django.test import TestCase
from ..models import Customer, Appointment
from django.utils import timezone
from datetime import datetime
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from .mixins import AuthenticatedTestMixin

User = get_user_model()

class TestCustomer(AuthenticatedTestMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.url = "/api/customer/"

        self.customer = Customer.objects.create(
            full_name="Roberto Usuario Teste",
            phone="+66 812345678",
            id_document="123456789",
            email="roberto@email.com",
            is_active=True,
        )

    def test_if_two_users_cannot_be_created_with_the_same_email_address(self):
        self.authenticate_client()

        payload = dict(
            full_name="Roberto Usuario Teste",
            phone="+66 812345678",
            id_document="987654321",
            email="roberto@email.com",
            is_active=True,
        )
        
        response = self.client.post(
            self.url,
            data=payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_if_two_users_cannot_be_created_with_the_same_id_document(self):
        self.authenticate_client()
        payload = dict(
            full_name="Ronaldo Usuario Teste",
            phone="+66 812345678",
            id_document="123456789",
            email="ronaldo@email.com",
            is_active=True,
        )
        
        response = self.client.post(
            self.url,
            data=payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_what_happens_in_the_database_when_a_customer_is_deleted(self):
        self.authenticate_client()
            
        url_delete = f"{self.url}{self.customer.id}/"
        before_counting_appointments = Customer.objects.count()

        response = self.client.delete(url_delete)

        # UPDATE DATABASE STATUS
        self.customer.refresh_from_db()

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertEqual(
            self.customer.is_active,
            False,
        )

        after_counting_appointments = Customer.objects.count()

        self.assertEqual(
            before_counting_appointments,
            after_counting_appointments
        )

class TestAppointments(AuthenticatedTestMixin, APITestCase):
    def setUp(self): 
        super().setUp()

        self.url = "/api/appointment/"

        self.location = "UNIT-2"

        self.customer = Customer.objects.create(
            full_name="Carlos Usuario Teste",
            phone="+66 812345678",
            id_document="123456789",
            email="joao@email.com",
            is_active=True,
        )

        start_existing = timezone.make_aware(
            datetime(2026, 1, 10, 9, 0, 0) # 10/Jan/2026 09:00:00
        )

        end_existing = timezone.make_aware(
            datetime(2026, 1, 10, 10, 0, 0) # 10/Jan/2026 10:00:00
        )
    
        self.existing = Appointment.objects.create(
            customer=self.customer,
            service_name="washing and drying",
            location=self.location,
            start_at=start_existing,
            end_at=end_existing,
            status="SCHEDULED",
            price=60.00,
            payment_method="TRANSFER",
        )

    def test_overlap_detect_conflict_between_appointments(self):

        """Verifica se detecta conflito de horário entre agendamentos"""
        new_start = timezone.make_aware(
            datetime(2026, 1, 10, 9, 30, 0) # 10/Jan/2026 09:30:00
        )

        new_end = timezone.make_aware(
            datetime(2026, 1, 10, 10, 30, 0) # 10/Jan/2026 10:30:00
        )

        payload = dict(
            customer=self.customer.id,
            service_name="Washing",
            location=self.location,
            start_at=new_start.isoformat(),
            end_at=new_end.isoformat(),
            status="SCHEDULED",
            price=95.00,
            payment_method="PIX",
        )

        self.authenticate_client()
        response = self.client.post(
            self.url,
            data=payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_to_verify_if_one_service_can_begin_exactly_when_the_other_ends(self):


        new_start = timezone.make_aware(
            datetime(2026, 1, 10, 10, 00, 0) # 10/Jan/2026 10:00:00
        )

        new_end = timezone.make_aware(
            datetime(2026, 1, 10, 11, 00, 0) # 10/Jan/2026 11:00:00
        )

        payload = dict(
            customer=self.customer.id,
            service_name="Washing",
            location=self.location,
            start_at=new_start.isoformat(),
            end_at=new_end.isoformat(),
            status="SCHEDULED",
            price=95.00,
            payment_method="PIX",
        )

        self.authenticate_client()
        response = self.client.post(
            self.url,
            data=payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_what_happens_in_the_database_when_a_appointment_is_deleted(self):

        url_delete = f"{self.url}{self.existing.id}/"
        before_counting_appointments = Appointment.objects.count()

        self.authenticate_client()
        response = self.client.delete(url_delete)

        # UPDATE DATABASE STATUS
        self.existing.refresh_from_db()

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertEqual(
            self.existing.status,
            "CANCELED",
        )

        after_counting_appointments = Appointment.objects.count()

        self.assertEqual(
            before_counting_appointments,
            after_counting_appointments
        )

    def test_to_create_appointment_with_customer_inactive(self):

        self.customer.is_active = False
        self.customer.save()

        start = timezone.make_aware(
            datetime(2026, 1, 12, 10, 00, 0) 
        )

        end = timezone.make_aware(
            datetime(2026, 1, 12, 11, 00, 0) 
        )

        payload = dict(
            customer=self.customer.id,
            service_name="Washing",
            location=self.location,
            start_at=start.isoformat(),
            end_at=end.isoformat(),
            status="SCHEDULED",
            price=95.00,
            payment_method="PIX",
        )

        self.authenticate_client()
        response = self.client.post(
            self.url,
            data=payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

class TestDashboard(AuthenticatedTestMixin, APITestCase):
    
    def setUp(self):
        super().setUp()
        self.location = "UNIT-2"
        self.url = "/api/dashboard/daily-summary/?date="
        self.customer = Customer.objects.create(
            full_name="Roberto Usuario Teste",
            phone="+66 812345678",
            id_document="123456789",
            email="roberto@email.com",
            is_active=True,
        )

        start = timezone.make_aware(
            datetime(2026, 1, 10, 9, 0, 0) # 10/Jan/2026 09:00:00
        )

        end = timezone.make_aware(
            datetime(2026, 1, 10, 10, 0, 0) # 10/Jan/2026 10:00:00
        )
    
        self.appointment = Appointment.objects.create(
            customer=self.customer,
            service_name="washing and drying",
            location=self.location,
            start_at=start,
            end_at=end,
            status="SCHEDULED",
            price=60.00,
            payment_method="TRANSFER",
        )

    def test_with_date_format_iso(self):
   
        date = timezone.make_aware(
            datetime(2026, 1, 10, 10)
        ).strftime("%Y-%m-%d")

        print(date)

        url_test = f"{self.url}{date}"
        
        self.authenticate_client()
        response = self.client.get(url_test)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

class RegisterUserTest(AuthenticatedTestMixin, APITestCase):
    def setUp(self):
        self.register_url = reverse("api_rest:register")
        self.valid_data = {
            "username": "testuser123",
            "first_name": "test first name",
            "last_name": "test last name",
            "email": "test@email.com.br",
            "password": "teste123456",
            "password_confirm": "teste123456",
        }

    def test_if_register_user_success(self):
        response = self.client.post(self.register_url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)


        