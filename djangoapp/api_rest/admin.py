from django.contrib import admin
from .models import Customer, Appointment, UserPayment, Establishment

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = "full_name",
    ordering = "-created_at",

@admin.register(Appointment)
class AppoinmentAdmin(admin.ModelAdmin):
    list_display = "payment_method",
    ordering = "-created_at",

@admin.register(UserPayment)
class UserPaymentAdmin(admin.ModelAdmin):
    list_display = "customer", "appointment", "has_paid",
    ordering = "-created_at",

@admin.register(Establishment)
class EstablishmentAdmin(admin.ModelAdmin):
    list_display = "name", "city", "cnpj",
    orderin = "created_at",