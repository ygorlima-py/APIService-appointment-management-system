from django.urls import path
from api_rest import views

app_name = 'api_rest'

urlpatterns = [
    path('customers/', views.Customers.as_view(), name='customers'),
    path('customers/<int:pk>/', views.CustomerDetailView.as_view(), name='customers_detail_view'),
    path('appointment/', views.Appointments.as_view(), name='appointment'),
    path('appointment/<int:pk>/', views.AppointmentDetailView.as_view(), name='appointment_detail_view'),
    path('dashboard/daily-summary/', views.DashbordsView.as_view(), name='dashboard'),
]

