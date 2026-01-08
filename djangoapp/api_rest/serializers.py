from rest_framework import serializers 
from .models import Customer, Appointment

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = "__all__"

    def validate(self, attrs):
        new_start_date = attrs.get("start_at")
        new_end_date = attrs.get("end_at")
        location = attrs.get("location")

        # (If it's a patch, retrieve current values ​​when they're not included in the payload)
        if self.instance:
            new_start_date = new_start_date or self.instance.start_at
            new_end_date = new_end_date or self.instance.end_t
            location = location or self.instance.location 

        conflict = (
            Appointment
            .objects
            .filter(
                location=location,
                start_at__lt=new_end_date,
                end_at__gt=new_start_date,
            ))
        
        if self.instance:
            conflict = conflict.exclude(id=self.instance.id)

        if conflict.exists():
            raise serializers.ValidationError("This time slot is already booked at this location.")

        return attrs
    
    