from rest_framework import serializers 
from .models import Customer, Appointment, Establishment
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"

        

class AppointmentSerializer(serializers.ModelSerializer):
    status = serializers.CharField(default="SCHEDULED")
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), write_only=True, source="customer", required=False)
    customer_name = serializers.CharField(source="customer.full_name", read_only=True)
    location_name = serializers.CharField(source="location.name", read_only=True)
    payment_method_label = serializers.CharField(source="get_payment_method_display", read_only=True)


    class Meta:
        model = Appointment
        fields = [
            "id", "start_at",
            "number_people","payment_method",
            "payment_method_label", "customer_id",
            "customer_name", "price",
            "location_id", "location_name", 
            "status","status_label",
            "observation", "created_at",
            "updated_at",
            ]

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        if request and request.user:
            establishment = Establishment.objects.filter(owner=user).first()
            
            if establishment:
                validated_data['location'] = establishment

        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        customer_data = validated_data.pop('customer', None)
                
        return super().update(instance, validated_data)

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8,)
    password_confirm = serializers.CharField(write_only=True,)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "password",
            "password_confirm",
        ]

    def validate(self, data):
        password = data.get('password')
        password_confirm = data.get('password_confirm')
     
        if not password or not password_confirm:
            raise serializers.ValidationError({
                'message': 'Senha é obrigatória'
            })

        if password != password_confirm:
            raise serializers.ValidationError({"password": "As senhas não coencidem"})
        return data
    
    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("password_confirm")

        user = User.objects.create_user(**validated_data, password=password)
        return user 
    
class UpdateUserSerializers(serializers.ModelSerializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    username = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True, min_length=8, required=False)
    password_confirm = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'password_confirm']

    def validate(self, data):
        password = data.get('password')
        password_confirm = data.get('password_confirm')
        # Trata string vazia como "não enviado"
        if password == "":
            password = None
            data['password'] = None

        if password_confirm == "":
            password_confirm = None
            data['password_confirm'] = None

        # Atualização: só valide se algum foi enviado
        if password or password_confirm:
            if not password or not password_confirm:
                raise serializers.ValidationError({'password': 'Envie password e password_confirm'})
            if password != password_confirm:
                raise serializers.ValidationError({'password': 'As senhas não coincidem'})

        return data
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        validated_data.pop('password_confirm', None)
        instance = super().update(instance, validated_data)
        if password:
            instance.set_password(password)
            instance.save()
        return instance

class RegisterEstablishmentSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = Establishment
        fields = "__all__"
        read_only_fields = ["id"]