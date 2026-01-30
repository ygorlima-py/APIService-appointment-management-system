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
                        UpdateUserSerializers,
                        AuthPasswordResetSerializer,
                        AuthPasswordResetConfirmSerializer,
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
from .services.send_email import send_email, send_email_reset_password
from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes

import os
import uuid

User = get_user_model()
DOMAIN = os.getenv("DOMAIN")
DOMAIN_FRONT_END = os.getenv("DOMAIN_FRONT_END")

class RegisterUser(APIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    # Create Refresh token
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        refresh_str = str(refresh)
        response =  Response({"access": access}, status=status.HTTP_201_CREATED)

        response.set_cookie(
            key=settings.SIMPLE_JWT["AUTH_COOKIE"],
            value=refresh,
            httponly=True,
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
            max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
            path="/",            
        )
        return response

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
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.establishments.first()

class UserTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        origin = request.headers.get("Origin")
        if origin and origin not in settings.ALLOWED_REFRESH_ORIGINS:
            print(settings.ALLOWED_REFRESH_ORIGINS)
            return Response({"detail": "Invalid origin"}, status=status.HTTP_403_FORBIDDEN)

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
        origin = request.headers.get("Origin")
        if origin and origin not in settings.ALLOWED_REFRESH_ORIGINS:
            return Response({"detail": "Invalid origin"}, status=status.HTTP_403_FORBIDDEN)

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

class LogOut(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        response = Response({"message": "logout successful"}, status=status.HTTP_200_OK)
        response.delete_cookie(
            key=settings.SIMPLE_JWT["AUTH_COOKIE"],
            path="/"
        )
        return response

# POST /api/customers/
# GET /api/customers/ (List using search terms like ?q= by full_name/phone/email)
class Customers(ListCreateAPIView):
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Customer.objects.filter(created_by=self.request.user)
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
    model = Customer
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Customer.objects.filter(created_by=self.request.user)

class FilterAppointmentByCustomer(ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        customer_id = self.kwargs["customer_id"]
        return Appointment.objects.filter(customer_id=customer_id)

# POST /api/appointment/
# GET /api/appointment/ (List using search terms like ?q= by start_at/end_at/customer_id/status)
class Appointments(ListCreateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    permission_classes = (IsAuthenticated,)
    def get_queryset(self):
        qs = Appointment.objects.filter(created_by=self.request.user)
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
    permission_classes = [IsAuthenticated]
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        return Appointment.objects.filter(created_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.status = "CANCELED"
        obj.save(update_fields=["status"])
        return Response(status=status.HTTP_204_NO_CONTENT)

    
class CreateCheckoutSession(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):   
        
        try:
            appointment = Appointment.objects.get(id=pk)
            establishment = get_object_or_404(Establishment, location=appointment)

        except Appointment.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND

        if not establishment.stripe_details_submitted:
            return Response({
                'message': 'Sua conta não está integrada com a Stripe, acesse configurações e clique em integrar com a stripe',
            })

        elif not (establishment.stripe_charges_enabled and establishment.stripe_payouts_enabled):
            return Response({
                'message': 'Sua conta esta pendente de verificação pela de identidade pela Stripe, pode levar até 48h',
            })

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
                "transfer_data": {"destination": establishment.stripe_account_id}
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

    def get(self, request):
        pk = request.query_params.get("establishment_id")
        establishment = get_object_or_404(Establishment, pk=pk, owner=request.user)
        
        if (establishment.stripe_charges_enabled and establishment.stripe_payouts_enabled):
            return Response({"message": "Você já está conectado com a stripe", "url": f"{DOMAIN}/pages/customers"})

        stripe.api_key = settings.STRIPE_SECRET_KEY
        if not establishment.stripe_account_id:
            account = stripe.Account.create(
                type="express",
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

        return redirect("api_rest:success_connect_stripe")

class StripeTemplateConnectSuccessful(TemplateView):
    template_name = "success_connect_stripe.html"

class AuthPasswordReset(APIView):
    serializer_class = AuthPasswordResetSerializer
    permission_classes = [AllowAny]
    def post(self, request):
        data = request.data
        
        serializer = self.serializer_class(data=data)

        # Verify with serializer if data is valid
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Get email after been validated
        email = serializer.validated_data["email"]

        # Verify if user exists with email, if false, send 
        if not User.objects.filter(email=email).exists():
            return Response({"message": "Foi enviado um email com link de recuperação de senha para o usuário cadastrado na plataforma"})

        # Get user instance with email
        user = User.objects.filter(email=email).first()

        # Generate UUID with id user
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))

        # Generate Token with instance user:
        token = default_token_generator.make_token(user)

        # Generate link frontEnd with token and uid
        link_front_end = f"{DOMAIN_FRONT_END}/pages/change_password.html?uid={uidb64}&token={token}"

        send_email_reset_password(link_front_end, user)

        return Response({"message": "Foi enviado um email com link de recuperação de senha para o usuário cadastrado na plataforma"})

class AuthPasswordResetConfirm(APIView): 
    permission_classes = [AllowAny]
    serializer_class = AuthPasswordResetConfirmSerializer
    
    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)

        if not serializer.is_valid():
            return Response({"message": "Senha inválida"}, status=status.HTTP_400_BAD_REQUEST)

        uid = serializer.validated_data["uid"]
        token = serializer.validated_data["token"]
        password = serializer.validated_data["password"]

        # Convert uid to id
        pk = urlsafe_base64_decode(uid)

        # get user in databas by id
        user = get_object_or_404(User, pk=pk)
        
        # Verify if token is valid
        if not default_token_generator.check_token(user, token):
            return Response({"message": "Token inválido"})

        # Change password in database
        user.set_password(password)
        user.save(update_fields=["password"])

        print(user.pk)
        print(user.check_password(password))

        return Response({"message": "Senha Atualizada com Sucesso"})
        

