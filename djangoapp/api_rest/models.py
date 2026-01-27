from django.db import models
import uuid
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class Customer(models.Model):
    full_name = models.CharField(max_length=255, null=False, blank=False,)
    phone = models.CharField(max_length=50, null=False, blank=False,)
    email = models.EmailField(max_length=100, null=False, blank=False,)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customers", blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.full_name}"
    
class Establishment(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    cnpj = models.CharField(max_length=30, blank=False, null=False)
    cep = models.CharField(max_length=8, blank=True, null=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=50)
    adress = models.CharField(max_length=255)
    number = models.CharField(max_length=10)
    phone = models.CharField(max_length=25)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="establishments")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    stripe_onboarding_token = models.UUIDField(default=uuid.uuid4, blank=True, null=True)
    stripe_account_id = models.CharField(max_length=255, null=True, blank=True)
    stripe_charges_enabled = models.BooleanField(default=False)
    stripe_payouts_enabled = models.BooleanField(default=False)
    stripe_details_submitted = models.BooleanField(default=False)


    def __str__(self) -> str:
        return f"{self.name}"
    
class Appointment(models.Model):
    
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Agendado"
        CONFIRMED = "CONFIRMED", "Confirmado"
        CANCELED = "CANCELED", "Cancelado"

    class Payment(models.TextChoices):
        PIX = "PIX", "Pix"
        CARD = "CARD", "Cartão de crédito"
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="appoinments")    
    location = models.ForeignKey(Establishment, on_delete=models.CASCADE, related_name="appointments")  
    start_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(choices=Status.choices)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    payment_method = models.CharField(choices=Payment.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    observation = models.TextField(max_length=500, null=True, blank=True)
    number_people = models.IntegerField(default=1)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="appointments", blank=True, null=True)


    def __str__(self) -> str:
        return f"Agendamento de {self.customer.full_name}"

    def save(self, *args, **kwargs):
        self.full_clean() # > call all verify
        return super().save(*args, **kwargs)

class UserPayment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=255)
    stripe_checkout_id = models.CharField(max_length=255)
    stripe_product_id = models.CharField(max_length=255)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    amount_cents = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    has_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.customer.full_name} - Pago {self.has_paid}"
