import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UserPayment, Appointment, Establishment
from django.shortcuts import get_object_or_404

@csrf_exempt
def stripe_webhook(request):
    payload = request.body.decode('utf-8')
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
        payload=payload, 
        sig_header=sig_header,
        secret=settings.STRIPE_WEBHOOK_SECRET,
    )
        
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print("Erro de assinatura")
        return HttpResponse(status=400)
    
    # Verify if event is type checkout.session.completed
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        session_id = session["id"]
        
        payment = UserPayment.objects.filter(stripe_checkout_id=session_id).first()
        appointment = Appointment.objects.filter(pk=payment.appointment.id).first()
        
        if payment:
            payment.has_paid=True
            payment.save(update_fields=["has_paid"])

            appointment.status = 'CONFIRMED'
            appointment.save(update_fields=["status"])
    
    # Verify if event is update account
    elif event["type"] == "account.updated":
        account = event["data"]["object"] # Get event information
        establishment = get_object_or_404(Establishment, stripe_account_id=account["id"]) # Get establishment by stripe_account_id 

        establishment.stripe_charges_enabled = bool(account["charges_enabled"])
        establishment.stripe_payouts_enabled = bool(account["payouts_enabled"])
        establishment.stripe_details_submitted = bool(account["details_submitted"])
        establishment.save(update_fields=[
            "stripe_charges_enabled",
            "stripe_payouts_enabled",
            "stripe_details_submitted",
        ])

    return HttpResponse(status=200)


