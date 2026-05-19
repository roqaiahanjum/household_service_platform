import json
import razorpay
# pyrefly: ignore [missing-import]
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from bookings.models import Booking
from .models import Payment

# Initialize Razorpay Client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def checkout_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Amount in paise (multiply ₹ by 100)
    amount_in_paise = int(booking.total_price * 100)
    
    # Create Razorpay Order
    order_data = {
        'amount': amount_in_paise,
        'currency': 'INR',
        'receipt': f'receipt_booking_{booking.id}',
        'payment_capture': 1  # Auto capture payment
    }
    
    try:
        razorpay_order = razorpay_client.order.create(data=order_data)
        razorpay_order_id = razorpay_order['id']
        
        # Save or update Payment details in database
        payment, created = Payment.objects.get_or_create(
            booking=booking,
            defaults={
                'razorpay_order_id': razorpay_order_id,
                'amount': booking.total_price,
                'currency': 'INR',
                'status': 'pending'
            }
        )
        
        if not created:
            payment.razorpay_order_id = razorpay_order_id
            payment.status = 'pending'
            payment.save()
            
    except Exception as e:
        messages.error(request, f"Error communicating with Razorpay: {str(e)}")
        return redirect('bookings:booking_detail', booking_id=booking.id)

    context = {
        'booking': booking,
        'order_id': razorpay_order_id,
        'razorpay_amount': amount_in_paise,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'customer_name': booking.customer.get_full_name() or booking.customer.username,
        'customer_email': booking.customer.email,
        'customer_phone': getattr(booking.customer, 'phone', '')
    }
    return render(request, 'payment/checkout.html', context)

def init_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.payment_status == 'PAID':
        return JsonResponse({'error': 'Already paid'}, status=400)
        
    amount_in_paise = int(booking.total_price * 100)
    
    payment = Payment.objects.filter(booking=booking, status='pending').first()
    if not payment:
        order_data = {
            'amount': amount_in_paise,
            'currency': 'INR',
            'receipt': f'receipt_booking_{booking.id}',
            'payment_capture': 1
        }
        try:
            razorpay_order = razorpay_client.order.create(data=order_data)
            razorpay_order_id = razorpay_order['id']
            Payment.objects.create(
                booking=booking,
                razorpay_order_id=razorpay_order_id,
                amount=booking.total_price,
                currency='INR',
                status='pending'
            )
        except razorpay.errors.BadRequestError as e:
            return JsonResponse({'error': f'Razorpay Configuration Error: Please check your API keys. Details: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Failed to create order: {str(e)}'}, status=400)
    else:
        razorpay_order_id = payment.razorpay_order_id
        
    return JsonResponse({
        'razorpay_order_id': razorpay_order_id,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'razorpay_amount': amount_in_paise,
        'customer_name': booking.customer.get_full_name() or booking.customer.username,
        'customer_email': booking.customer.email,
        'customer_phone': getattr(booking.customer, 'phone_number', '') or '',
    })


@csrf_exempt
def verify_payment(request):
    if request.method == 'POST':
        # Can be JSON or Form data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
            
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')
        
        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return JsonResponse({'status': 'failed', 'message': 'Missing payment verification params.'}, status=400)
            
        # Verify the signature
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        
        try:
            # Cryptographic verification
            razorpay_client.utility.verify_payment_signature(params_dict)
            
            # Signature is valid. Update DB models.
            payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = 'success'
            payment.save()
            
            # Update Booking details
            booking = payment.booking
            booking.status = Booking.Status.CONFIRMED
            booking.payment_status = 'PAID'
            booking.save()
            
            return JsonResponse({'status': 'success'})
            
        except razorpay.errors.SignatureVerificationError:
            # Payment failed verification
            try:
                payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
                payment.status = 'failed'
                payment.save()
                
                booking = payment.booking
                booking.payment_status = 'FAILED'
                booking.save()
            except Payment.DoesNotExist:
                pass
                
            return JsonResponse({'status': 'failed', 'message': 'Signature verification failed.'}, status=400)
            
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)}, status=500)
            
    return HttpResponseBadRequest("Invalid request method")

def payment_success(request):
    booking_id = request.GET.get('booking_id')
    payment_id = request.GET.get('payment_id')
    booking = get_object_or_404(Booking, id=booking_id)
    payment = get_object_or_404(Payment, razorpay_payment_id=payment_id)
    
    context = {
        'booking': booking,
        'payment': payment
    }
    return render(request, 'payment/success.html', context)

def payment_failed(request):
    booking_id = request.GET.get('booking_id')
    booking = None
    if booking_id:
        booking = get_object_or_404(Booking, id=booking_id)
        
        # If there's an associated payment, mark it as failed
        Payment.objects.filter(booking=booking, status='pending').update(status='failed')
        
        booking.payment_status = 'FAILED'
        booking.save()
        
    context = {
        'booking': booking
    }
    return render(request, 'payment/failed.html', context)
