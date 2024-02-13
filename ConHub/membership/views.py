from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .models import Payment
from content.views import ContentAndVideoList

from django.views.generic import ListView, View
from .models import Membership, Usermembership, Subscription
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from .paystack import Paystack
import paystack


# Create your views here.

def profile(request):
    Subscription.update_next_payment_dates()
    # Subscription.update_subscription_status()

    user_membership = get_user_membership(request)
    user_subscription = get_user_subscription(request)

    if user_subscription:
        next_payment_date = user_subscription.next_payment_date
    else:
        if user_membership and user_membership.membership.membership_type == 'free':
            next_payment_date = None  # No payment required for free membership


    context ={
        'user_membership': user_membership,
        'user_subscription': user_subscription,
        'next_pay_date': next_payment_date
    }
    return render(request, 'membership/profile.html', context=context)



def get_user_membership(request):
    user_membership_qs = Usermembership.objects.filter(user=request.user)
    if user_membership_qs.exists():
        return user_membership_qs.first()
    return None



def get_user_subscription(request):
    
    user_subscription_qs = Subscription.objects.filter(user_membership=get_user_membership(request))
    if user_subscription_qs.exists():
        user_subscription = user_subscription_qs.first()
        return user_subscription
    return None



def get_selected_membership(request):

    membership_type = request.session['selected_membership_type']
    selected_membership_qs = Membership.objects.filter(membership_type=membership_type)
    if selected_membership_qs.exists():
        return selected_membership_qs.first()
    return None
   


            

class Membershipselect(ListView):
    model = Membership
    template_name = 'membership/membership_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        current_membership = get_user_membership(self.request)
        context['current_membership'] = str(current_membership.membership)
        return context

    def post(self, request, **kwargs):
        selected_membership_type = request.POST.get('membership_type')

        # Retrieve user's current membership and subscription
        user_membership = get_user_membership(request)
        user_subscription = get_user_subscription(request)

        # Check if the selected membership type exists
        selected_membership_qs = Membership.objects.filter(membership_type=selected_membership_type)
        if selected_membership_qs.exists():
            selected_membership = selected_membership_qs.first()
        else:
            messages.error(request, 'Selected membership type does not exist.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # Validate if the user already has the selected membership
        if user_membership.membership == selected_membership:
            if user_subscription:
                messages.info(request, 'You already have this membership.')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # Store the selected membership type in the session
        request.session['selected_membership_type'] = selected_membership_type

        # Redirect to the payment initiation page
        return HttpResponseRedirect(reverse('membership:ipayment'))





def initiate_payment(request):

    selected_membership = get_selected_membership(request)
    context = {
        'selected_membership': selected_membership
    }

    if request.method == "POST":
        price = selected_membership.price
        email = request.POST['email']
        selected_membership = request.POST.get('membership_type')

        publickey = settings.PAYSTACK_PUBLIC_KEY

        # payment = Payment.objects.create(price=price, email=email, user=request.user)
        payment = Payment.objects.create(price=price, email=email, user=request.user)
        payment.save()

        context = {
            'payment': payment,
            'field_values': request.POST,
            'paystack_pub_key': publickey,
            'amount_value': payment.amount_value(),
            'selected_membership': selected_membership,
        }
        return render(request, 'membership/make_payment.html', context)
    
    return render(request, 'membership/payment.html', context)



# def verify_payment(request, ref):
#     payment = get_object_or_404(Payment, ref=ref)
#     verified = payment.verify_payment()

#     if verified:
#         print(request.user.username, " payment successfull")
#         return ContentAndVideoList.as_view()(request)
#     else:
#         return render(request, "membership/make_payment.html")
            



def verify_payment(request, ref):

    payment = get_object_or_404(Payment, ref=ref)
    verified = payment.verify_payment()

    if verified:
        # Update user's membership and subscription
        update_transactions(request, subscription_id=payment.ref)

        print(request.user.username, " payment successful")
        return ContentAndVideoList.as_view()(request)
    else:
        return render(request, "membership/make_payment.html")

def update_transactions(request, subscription_id):
    user_membership = get_user_membership(request)
    selected_membership = get_selected_membership(request)

    user_membership.membership = selected_membership
    user_membership.save()

    sub, created = Subscription.objects.get_or_create(user_membership=user_membership)
    sub.paystack_subscription_id = subscription_id
    sub.active = True
    sub.save()

    try:
        del request.session['selected_membership_type']
    except:
        pass  

    messages.info(request, f"Successfully created {selected_membership} membership.")
    return redirect('content:list')







def cancelSubscription(request):
    user = request.user
    try:
        # Retrieve the user's subscription
        subscription = Subscription.objects.get(user_membership__user=user)
        
        # Check if the subscription is active
        if subscription.active:
            # Cancel the subscription
            subscription.active = False
            subscription.save()
            messages.success(request, 'Subscription cancelled successfully.')
        else:
            messages.warning(request, 'Your subscription is not active.')

    except Subscription.DoesNotExist:
        messages.error(request, 'You do not have an active subscription.')

    return redirect('membership:confirm')




def confirmCancelSubscription(request):
    user = request.user
    try:
        # Retrieve the user's subscription
        subscription = Subscription.objects.get(user_membership__user=user)
        if not subscription.active:
            messages.error(request, 'Your subscription is not active.')
            return redirect('membership:profile')
        
        return render(request, 'membership/confirm_cancel.html', {'subscription': subscription})
    
    except Subscription.DoesNotExist:
        messages.error(request, 'You do not have an active subscription.')
        return redirect('membership:mselect')  
    

















# def initiate_payment(request):
#     selected_membership = get_selected_membership(request)
#     context = {
#         'selected_membership': selected_membership
#     }

#     if request.method == "POST":
#         selected_membership_type = request.POST.get('membership_type')  # Get the selected membership type from the form
#         price = selected_membership.price
#         email = request.POST['email']
#         user_membership = get_user_membership(request)

#         # Store the selected membership type in the session
#         request.session['selected_membership_type'] = selected_membership_type

#         publickey = settings.PAYSTACK_PUBLIC_KEY

#         payment = Payment.objects.create(user_membership=user_membership, price=price, email=email, user=request.user)
#         payment.save()

#         context = {
#             'payment': payment,
#             'field_values': request.POST,
#             'paystack_pub_key': publickey,
#             'amount_value': payment.amount_value(),
#             'selected_membership': selected_membership_type,  # Pass the selected membership type instead of the object
#         }
#         return render(request, 'membership/make_payment.html', context)
    
#     return render(request, 'membership/payment.html', context)




# def verify_payment(request, ref):
#     selected_membership = request.POST.get('membership_type')
#     payment = Payment.objects.get(ref=ref)
    
#     # Create or get the Membership object based on the selected_membership_type
#     # membership, created = Membership.objects.get_or_create(membership_type=selected_membership)
#     membership, created = Membership.objects.get_or_create(membership_type=selected_membership)
    
#     # Update the Payment object with the selected Membership
#     payment.membership = membership
#     payment.save()
    
#     payment = get_object_or_404(Payment, ref=ref)
#     verified = payment.verify_payment()

#     if verified:
#         print(request.user.username, " payment successfull")
#         return ContentAndVideoList.as_view()(request)
#     else:
#         return render(request, "membership/make_payment.html")

    





# def update_transactions(request, subscription_id):
#     user_membership = get_user_membership(request)
#     selected_membership = get_selected_membership(request)

#     user_membership.membership = selected_membership
#     user_membership.save()

#     sub, created = Subscription.objects.get_or_create(user_membership = user_membership)
#     sub.paystack_subscription_id = subscription_id
#     sub.active = True
#     sub.save()

#     try:
#         del request.session['selected_membership_type']
#     except:
#         pass  

#     messages.info(request, 'successfully created {} membership.format(selected_membership)')
#     return redirect('content:list')  

