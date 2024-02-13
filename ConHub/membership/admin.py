from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Membership)
admin.site.register(Usermembership)
# admin.site.register(Subscription)
# admin.site.register(Payment)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('email', 'price', 'verified', 'date_created', 'user')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display =('user_membership', 'active', 'next_payment_date')   





# @admin.register(Membership)
# class Membershipadmin(admin.ModelAdmin):
#     list_display = ('membership_type', 'paystack_id')

# @admin.register(Usermembership)
# class Usermembershipadmin(admin.ModelAdmin):
#     list_display = ('membership', 'paystack_id')

# @admin.register(Subscription)
# class Subscriptionadmin(admin.ModelAdmin):
#     list_display = ('user_membership', 'paystack_id', 'active')        


