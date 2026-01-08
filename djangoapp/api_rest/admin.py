from django.contrib import admin
from .models import Customer, Appointment

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = "full_name",
    ordering = "-created_at",

@admin.register(Appointment)
class AppoinmentAdmin(admin.ModelAdmin):
    list_display = "service_name",
    ordering = "-created_at",