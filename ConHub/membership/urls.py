from django.urls import path
# from .views import initiate_payment, verify_payment, , paymentview

from .views import Membershipselect, verify_payment, initiate_payment, profile, cancelSubscription, confirmCancelSubscription

app_name = 'membership'
urlpatterns = [
    path('confirm/', confirmCancelSubscription, name='confirm'),
    path('cancel/', cancelSubscription, name='cancel'),
    path('profile/', profile, name='profile'),
    path('initiatep/', initiate_payment, name='ipayment'),
    path('verifyp/<str:ref>/', verify_payment, name='verify_payment'),  
    path('', Membershipselect.as_view(), name='mselect'), 
]
