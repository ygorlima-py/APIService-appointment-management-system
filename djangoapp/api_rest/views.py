from rest_framework.response import Response 
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView, ListAPIView, RetrieveUpdateAPIView, UpdateAPIView#type:ignore
from rest_framework.views import APIView
from django.views.generic import TemplateView
from rest_framework import permissions
from django.contrib.auth import get_user_model 
from django.views import View
from django.shortcuts import redirect
from django.http import HttpResponse
from .models import Customer, Appointment, UserPayment, Establishment
from .serializers import (CustomerSerializer,
                        AppointmentSerializer,
                        UserRegistrationSerializer,
                        RegisterEstablishmentSerializer,
                        UpdateUserSerializers
                        )
from django.db.models import Q, Count, Sum
from datetime import date as date_cls
from rest_framework import status
from drf_spectacular.utils import extend_schema
import stripe
from django.conf import settings
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from .services.send_email import send_email
from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import get_object_or_404
import os
import uuid

User = get_user_model()
DOMAIN = os.getenv("DOMAIN")

class RegisterUser(APIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


    # Create Refresh token
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        data = UserRegistrationSerializer(user).data
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        return Response(data, status=status.HTTP_201_CREATED)
    
    def get(self, request):
        serializer = UserRegistrationSerializer(request.user)
        return Response(serializer.data)

class UpdateUser(UpdateAPIView):
    serializer_class = UpdateUserSerializers
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.establishments

class UpdateEstablishment(UpdateAPIView):
    serializer_class = RegisterEstablishmentSerializer

    def get_object(self):
        return self.request.user.establishments.first()

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

        stripe.api_key = settings.STRIPE_SECRET_KEY
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
            success_url=f"{DOMAIN}/api/success",
            cancel_url=f"{DOMAIN}/api/cancel",
            payment_intent_data={
                "transfer_data": {"destination": appointmen.location.stripe_account_id}
            }
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
    permission_classes = [IsAuthenticated]

    serializer_class = RegisterEstablishmentSerializer
    
    def get_queryset(self):
        return Establishment.objects.filter(owner=self.request.user)

class EstablishmentStripeConnect(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        establishment = get_object_or_404(Establishment, pk=pk, owner=request.user)

        stripe.api_key = settings.STRIPE_SECRET_KEY
        if not establishment.stripe_account_id:
            account = stripe.Account.create(
                type="standard",
                country="BR",
                email=request.user.email,
                business_profile={
                    "name": establishment.name,
                },
                capabilities = {
                    "card_payments": {"requested": True},
                    "transfers": {"requested": True},
                }
            )

            establishment.stripe_account_id = account["id"]
            establishment.save(update_fields=["stripe_account_id"])

            establishment.stripe_onboarding_token = uuid.uuid4()
            establishment.save(update_fields=["stripe_onboarding_token"])

        account_link = stripe.AccountLink.create(
            account=establishment.stripe_account_id,
            refresh_url=f"{DOMAIN}/api/stripe/connect/refresh?state={establishment.stripe_onboarding_token}",
            return_url=f"{DOMAIN}/api/stripe/connect/return?state={establishment.stripe_onboarding_token}",
            type="account_onboarding",
        )

        return Response({"url": account_link["url"]}, status=status.HTTP_200_OK)

class StripeConnectRefresh(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        token = request.query_params.get("state")
        establishment = get_object_or_404(Establishment, stripe_onboarding_token=token)
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
        account_link = stripe.AccountLink.create(
            account=establishment.stripe_account_id,
            refresh_url=f"{DOMAIN}/api/stripe/connect/refresh?state={establishment.stripe_onboarding_token}",
            return_url=f"{DOMAIN}/api/stripe/connect/return?state={establishment.stripe_onboarding_token}",
            type="account_onboarding",
        )

        return redirect(account_link['url'])

class StripeConnectReturn(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.query_params.get("state")
        establishment = get_object_or_404(Establishment, stripe_onboarding_token=token)

        stripe.api_key = settings.STRIPE_SECRET_KEY
        account = stripe.Account.retrieve(establishment.stripe_account_id)

        print("requirements.currently_due:", account["requirements"]["currently_due"])
        print("requirements.past_due:", account["requirements"]["past_due"])
        print("requirements.pending_verification:", account["requirements"]["pending_verification"])
        print("disabled_reason:", account.get("requirements", {}).get("disabled_reason"))

        establishment.stripe_charges_enabled = bool(account["charges_enabled"])
        establishment.stripe_payouts_enabled = bool(account["payouts_enabled"])
        establishment.stripe_details_submitted = bool(account["details_submitted"])
        establishment.stripe_onboarding_token = None
        establishment.save(update_fields=[
            "stripe_charges_enabled",
            "stripe_payouts_enabled",
            "stripe_details_submitted",
            "stripe_onboarding_token",
        ])

        return redirect("api_rest:success")