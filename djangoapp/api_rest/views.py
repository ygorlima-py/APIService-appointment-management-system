from rest_framework.response import Response 
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, ListAPIView #type:ignore
from rest_framework.views import APIView
from django.views.generic import TemplateView
from rest_framework import permissions
from django.contrib.auth import get_user_model 
from django.views import View
from django.http import HttpResponse
from .models import Customer, Appointment, UserPayment, Establishment
from .serializers import (CustomerSerializer,
                        AppointmentSerializer,
                        UserRegistrationSerializer,
                        RegisterEstablishmentSerializer
                        )
from django.db.models import Q, Count, Sum
from datetime import date as date_cls
from rest_framework import status
from drf_spectacular.utils import extend_schema
import stripe
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from .services.send_email import send_email
from decimal import Decimal, ROUND_HALF_UP
import os

DOMAIN = os.getenv("DOMAIN")

class RegisterUser(CreateAPIView):
    model = get_user_model()
    permission_classes = [
        permissions.AllowAny # Or anon users can't register
    ]
    serializer_class = UserRegistrationSerializer

    # Create Refresh token
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = get_user_model().objects.get(email=response.data["email"])
        refresh = RefreshToken.for_user(user)
        response.data['refresh'] = str(refresh)
        response.data['access'] = str(refresh.access_token)
        return response

class UserTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # Get refresh's cookie
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE"])
        if not refresh_token:
            return Response({'detail': 'Refresh token not found in cookies'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TokenRefreshSerializer(data={"refresh": refresh_token})
        serializer.is_valid(raise_exception=True)

        response = Response(serializer.validated_data, status=status.HTTP_200_OK)
            # Atualiza o cookie com novo refresh se ROTATE_REFRESH_TOKENS=True
        if 'refresh' in response.data:
            new_refresh = response.data['refresh']
            del response.data['refresh']

            response.set_cookie(
                key=settings.SIMPLE_JWT["AUTH_COOKIE"],
                value=new_refresh,
                httponly=True,
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
                max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
                path="/",            
            )
        return response

# Nesta view geramos os tokens, definimos os cookies HttpOnly para refresh e retorna apenas o access no JSON
class UserTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request,*args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            refresh_token = response.data['refresh']

            # Remove o Refresh do json e deixa apenas no cookie
            del response.data['refresh']

            # Define o cookie HttpOnly para refresh
            response.set_cookie(
                key=settings.SIMPLE_JWT["AUTH_COOKIE"],
                value=refresh_token,
                httponly=True, 
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
                max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()), 
                path="/",              
            )      
        return response
        
# POST /api/customers/
# GET /api/customers/ (List using search terms like ?q= by full_name/phone/email)
class Customers(ListCreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get("q")

        if q:
            qs = (qs
                .filter(
                Q(full_name__icontains=q) |
                Q(phone__icontains=q) |
                Q(email__icontains=q)
                ))
        
        return qs
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        return Response({"id": response.data["id"]}, status=status.HTTP_201_CREATED)
    
# GET /api/customers/id
# PUT /api/customers/id
# PATCH /api/customers/id
# DELET /api/customers/id
class CustomerDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class FilterAppointmentByCustomer(ListAPIView):
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        customer_id = self.kwargs["customer_id"]
        return Appointment.objects.filter(customer_id=customer_id)

# POST /api/appointment/
# GET /api/appointment/ (List using search terms like ?q= by start_at/end_at/customer_id/status)
class Appointments(ListCreateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    permission_classes = (IsAuthenticated,)
    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get("q")

        if q:
            qs = (qs
                .filter(
                Q(start_at__icontains=q) |
                Q(customer__phone__icontains=q) |
                Q(status__icontains=q)
                ))
        
        return qs

# GET /api/appointment/id
# PUT /api/appointment/id
# PATCH /api/appointment/id
# DELET /api/appointment/id
class AppointmentDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.status = "CANCELED"
        obj.save(update_fields=["status"])
        return Response(status=status.HTTP_204_NO_CONTENT)

class DashbordsView(APIView):
    def get(self, request):  
        
        date = self.request.query_params.get("date")
        
        if not date:
            return Response({"detail": "put ?date=YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            day = date_cls.fromisoformat(date)

        except ValueError:
            return Response({"detail": "Invalid format. Use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)

        qs = Appointment.objects.filter(start_at__date=day)

        data = qs.filter(start_at__date=date).aggregate(
            total=Count("id"),
            scheduled=Count("id", filter=Q(status="SCHEDULED")),
            canceled=Count("id", filter=Q(status="CANCELED")),
            done=Count("id", filter=Q(status="DONE")),
            total_price_done=Sum("price", filter=Q(status="DONE")),
        )

        result = dict(
            date=date,
            total_appointments=data["total"],
            total_appointments_scheduled=data["scheduled"],
            total_appointment_canceled=data["canceled"],
            total_appointment_done=data["done"],
            total_appointment_price_done=data["total_price_done"],
        )

        return Response(result)
    
class CreateCheckoutSession(APIView):

    def get(self, request, pk):   
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        try:
            appointment = Appointment.objects.get(id=pk)

        except Appointment.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND
        
        if UserPayment.objects.filter(appointment=appointment).exists():
            return Response({
                'message': 'este agendamento ja foi enviado para pagamento. Solicite ao cliente para verificar sua caixa de email',
            })

        # Get cutomer create appointment
        customer = appointment.customer
        unit_amount = int((Decimal(str(appointment.price)) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

        # Crete page in stripe for payment
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[
                {
                    "price_data": {
                        "currency":"brl",
                        "product_data": {
                            "name": f"Reserva em {appointment.location.name} em nome de {appointment.customer.full_name}",
                            },
                        "unit_amount": unit_amount,       
                    }, 
                    "quantity": 1,
                }
            ],
            success_url=f"http://{DOMAIN}/api/success",
            cancel_url=f"http://{DOMAIN}/api/cancel",
        )


        # Save local register talking "I started payment"
        payment = UserPayment.objects.create(
            customer=customer,
            appointment=appointment,
            stripe_customer_id="",
            stripe_checkout_id=session["id"],
            stripe_product_id="",
            amount_cents=int(unit_amount),
            price=appointment.price,
            currency="brl",
            has_paid=False,
        )

        url_checkout_stripe = session["url"]
        send_email(url_checkout_stripe, appointment.id)

        return Response(
            {
                "message": f'Pagamento enviado com sucesso. Solicite ao seu cliente que verifique sua caixa de email',
            },
            status=status.HTTP_201_CREATED,
        )

       
    
class SuccessView(TemplateView):
    template_name = "success_checkout.html"

class CancelView(TemplateView):
    template_name = "cancel_checkout.html"
    
class RegisterEstablishment(ListCreateAPIView):
    serializer_class = RegisterEstablishmentSerializer
    
    def get_queryset(self):
        return Establishment.objects.filter(owner=self.request.user)
    


