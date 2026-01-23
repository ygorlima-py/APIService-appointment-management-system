from django.urls import path
from api_rest import views

app_name = 'api_rest'

urlpatterns = [
    path('register/', views.RegisterUser.as_view(), name='register'),
    path('update_user/', views.UpdateUser.as_view(), name='update_user'),

    # URL For customera www.yourdomain.com/api/customer
    path('customer/', views.Customers.as_view(), name='customers'),
    path('customer/<int:pk>/', views.CustomerDetailView.as_view(), name='customers_detail_view'),

    # URL For appointments www.yourdomain.com/api/appointment
    path('appointment/', views.Appointments.as_view(), name='appointment'),
    path('appointment/<int:pk>/', views.AppointmentDetailView.as_view(), name='appointment_detail_view'),

    # URL For dashbords www.yourdomain.com/api/dashboard/daily-summary/q=date
    path('dashboard/daily-summary/', views.DashbordsView.as_view(), name='dashboard'),

    # URL For checkout stripe 
    path('payments/checkout/<int:pk>/', views.CreateCheckoutSession.as_view(), name='checkout'),
    path("success/", views.SuccessView.as_view(), name="success"),
    path("cancel/", views.CancelView.as_view(), name="cancel"),

    path('establishment/', views.RegisterEstablishment.as_view(), name='establishment'),
    path('login/', views.UserTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', views.UserTokenRefreshView.as_view(), name='token_refresh'),

    path('filter-appointment-customer/<int:customer_id>/', views.FilterAppointmentByCustomer.as_view(), name='filter_appointment')
]

