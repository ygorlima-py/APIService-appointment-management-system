from django.db import models
import uuid

from django.core.exceptions import ValidationError

# Create your models here.
class Customer(models.Model):
    full_name = models.CharField(
        max_length=255,
        null=False,
        blank=False,
    )

    phone = models.CharField(
        max_length=50,
        null=False,
        blank=False,
    )

    email = models.EmailField(
        max_length=100,
        null=False,
        blank=False,
        unique=True,
    )

    id_document = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        unique=True,
    )
    
    notes = models.TextField(
        max_length=500,
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.full_name}"
    

class Appointment(models.Model):
    
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Scheduled"
        CONFIRMED = "CONFIRMED", "Confirmed"
        CANCELED = "CANCELED", "Canceled"
        DONE = "DONE", "Done"

    class Payment(models.TextChoices):
        CASH = "CASH", "Cash"
        PIX = "PIX", "Pix"
        CARD = "CARD", "Card"
        TRANSFER = "TRANSFER", "Transfer"
    
    class Units(models.TextChoices):
        UNIT_1 = 'UNIT-1', "Unit 1"
        UNIT_2 = 'UNIT-2', "Unit 2"
        UNIT_3 = 'UNIT-3', "Unit 3"
        UNIT_4 = 'UNIT-4', "Unit 4"


    customer = models.ForeignKey(
            Customer,
            on_delete=models.CASCADE,
            related_name="Appoinments",
            )
    
    service_name = models.CharField(
        max_length=255,
        null=False,
        blank=False,
    )

    location = models.CharField(
                choices=Units.choices,
                blank=True,
                default="UNIT-1",
                )

    start_at = models.DateTimeField(
        null=True,
        blank=True, 
    )

    end_at = models.DateTimeField(
        null=True,
        blank=True, 
    )

    status = models.CharField(choices=Status.choices)

    price = models.DecimalField(
        decimal_places=2,
        max_digits=10,
    )

    payment_method = models.CharField(choices=Payment.choices)

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.end_at <= self.start_at:
            raise ValidationError("The end date must not be later than the start date.")
        
        if not self.customer.is_active:
            raise ValidationError("This client is inactive; no services can be scheduled for them.")

    def save(self, *args, **kwargs):
        self.full_clean() # > call all verify
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.service_name

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
        return f"{self.customer.full_name} - {self.appointment.service_name} - Pago {self.has_paid}"


