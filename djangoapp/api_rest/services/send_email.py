from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings
from django.core.mail import EmailMessage
from api_rest.models import Appointment

# Lembrete: Transformar em classe

def get_appointment(appointment_id):
    return Appointment.objects.filter(pk=appointment_id).first()

def create_template_stripe(link_stripe, appointment):
    # Render html:
    html_content = render_to_string(
        template_name='appointment_email.html', 
        context={
            'appointment': appointment,
            'link_stripe': link_stripe,
        }
    )
    return html_content

def send_email(link_stripe, appointment_id):
    appointment = get_appointment(appointment_id)

    html_appointment = create_template_stripe(link_stripe, appointment)
    email = EmailMessage(
        subject=f"Reserva {appointment.location.name} cliente {appointment.customer}",
        from_email="smart.voucher@globalhost.app.br",
        body=html_appointment,
        to=[appointment.customer.email],
    )
    email.content_subtype = "html"
    email.send()

    return "Sucessful"

def create_template_reset_password(link_change_password):
    html_content = render_to_string(
        template_name="reset_password_email.html",
        context={
            "link_change_password": link_change_password,
        }
    )
    return html_content

def send_email_reset_password(link_change_password, user):
    html_reset_password = create_template_reset_password(link_change_password)
    print(link_change_password)
    email = EmailMessage(
        subject=f"Recuperação de senha",
        from_email="smart.voucher@globalhost.app.br",
        body=html_reset_password,
        to=[user.email],
    )
    email.content_subtype = "html"
    email.send()
    


if __name__ == "__main__":
    send_email()