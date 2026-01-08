from rest_framework.response import Response 
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView #type:ignore
from rest_framework.views import APIView
from .models import Customer, Appointment
from .serializers import CustomerSerializer, AppointmentSerializer
from django.db.models import Q, Count, Sum
from datetime import date as date_cls


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
    
# GET /api/customers/id
# PUT /api/customers/id
# PATCH /api/customers/id
# DELET /api/customers/id
class CustomerDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.is_active = False
        obj.save(update_fields=["is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)
    
# POST /api/appointment/
# GET /api/appointment/ (List using search terms like ?q= by start_at/end_at/customer_id/status)
class Appointments(ListCreateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer


    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get("q")

        if q:
            qs = (qs
                .filter(
                Q(start_at__icontains=q) |
                Q(end_at__icontains=q) |
                Q(customer_id__icontains=q) |
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
    

