from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.db.models.signals import post_save
from .paystack import Paystack
import secrets
import paystack

from django.db.models.signals import post_save
from django.dispatch import receiver

from datetime import timedelta
from django.utils import timezone


# Create your models here.

paystack.api_key = settings.PAYSTACK_SECRET_KEY


MEMBERSHIP_CHOICES = (
    ('premium', 'prm'),
    ('standard', 'std'),
    ('free', 'free'),
)

class Membership(models.Model):
    slug = models.SlugField()
    membership_type = models.CharField(choices=MEMBERSHIP_CHOICES, default='free', max_length=40)
    price = models.IntegerField(default=10000)
    paystack_id = models.CharField(max_length=25)

    def __str__(self):
        return self.membership_type




class Usermembership(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) #for User
    paystack_id = models.CharField(max_length=25)
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.user.username



def post_save_usermembership_create(sender, instance, created, *args, **kwargs):
    if created:
        Usermembership.objects.get_or_create(user=instance)

    user_membership, created = Usermembership.objects.get_or_create(user=instance)

    if user_membership.paystack_id is None or user_membership.paystack_id == '_':
        new_customer_id = paystack.customer.create(email=instance.email)
        user_membership.paystack_id = new_customer_id['id']
        user_membership.save()

post_save.connect(post_save_usermembership_create, sender=settings.AUTH_USER_MODEL)  #for User





class Subscription(models.Model):
    user_membership = models.ForeignKey(Usermembership, on_delete=models.CASCADE)
    paystack_id = models.CharField(max_length=25)
    active = models.BooleanField(default=True)
    next_payment_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user_membership.user.username

    def calculate_next_payment_date(self):
        
        if self.next_payment_date is None:
            # If next_payment_date is not set, set it to the current date plus 30 days
            self.next_payment_date = timezone.now() + timedelta(days=30)
        else:
            # If next_payment_date is already set, add 30 days to it
            self.next_payment_date += timedelta(days=30)

    def save(self, *args, **kwargs):
        if self.active and not self.next_payment_date:
            # Calculate next payment date if subscription is active and next_payment_date is not set
            self.next_payment_date = timezone.now() + timedelta(days=30)
        elif self.active and self.next_payment_date:
            # If subscription is active and next_payment_date is set, add 30 days to it
            self.next_payment_date += timedelta(days=30)

         # Check if the next payment date has passed and update user's membership accordingly
        if self.active and self.next_payment_date and self.next_payment_date < timezone.now():
            self.user_membership.membership = Membership.objects.get(membership_type='free')
            self.user_membership.save()
        super().save(*args, **kwargs)


    @classmethod
    def update_next_payment_dates(cls):
        subscriptions_without_next_payment_date = cls.objects.filter(active=True, next_payment_date__isnull=True)
        for subscription in subscriptions_without_next_payment_date:
            subscription.calculate_next_payment_date()
            subscription.save()    

    





class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)  
    price = models.PositiveIntegerField()
    ref = models.CharField(max_length=200)
    email = models.EmailField()
    verified = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE, blank=True, null=True)
    user_membership = models.ForeignKey(Usermembership, on_delete=models.CASCADE, blank=True, null=True)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, blank=True, null=True,  related_name='payment',)
    

    class Meta:
        ordering = ('-date_created',)

    def _str_(self):
        return f"Payment: {self.price}"

    def save(self, *args, **kwargs):
        while not self.ref:
            ref = secrets.token_urlsafe(50)
            object_with_similar_ref = Payment.objects.filter(ref=ref)
            if not object_with_similar_ref:
                self.ref = ref

        super().save(*args, **kwargs)
    
    def amount_value(self):
        return int(self.price) * 100

    def verify_payment(self):
        paystack = Paystack()
        status, result = paystack.verify_payment(self.ref, self.price)
        if status:
            if result['amount'] / 100 == self.price:
                self.verified = True
                self.save()  # Save the object after verification

                # Update the related subscription to active status
                try:
                    subscription = self.subscription
                    if subscription:
                        subscription.active = True
                        subscription.save()
                except Subscription.DoesNotExist:
                    pass

                return True

        return False




















# class Payment(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)  
#     price = models.PositiveIntegerField()
#     ref = models.CharField(max_length=200)
#     email = models.EmailField()
#     verified = models.BooleanField(default=False)
#     date_created = models.DateTimeField(auto_now_add=True)
#     # membership = models.ForeignKey(Membership, on_delete=models.CASCADE, blank=True, null=True)
#     user_membership = models.ForeignKey(Usermembership, on_delete=models.CASCADE, blank=True, null=True)

#     class Meta:
#         ordering = ('-date_created',)

#     def _str_(self):
#         return f"Payment: {self.price}"

#     def save(self, *args, **kwargs):
#         while not self.ref:
#             ref = secrets.token_urlsafe(50)
#             object_with_similar_ref = Payment.objects.filter(ref=ref)
#             if not object_with_similar_ref:
#                 self.ref = ref

#         super().save(*args, **kwargs)
    
#     def amount_value(self):
#         return int(self.price) * 100

#     # def verify_payment(self):
#     #     paystack = Paystack()
#     #     status, result = paystack.verify_payment(self.ref, self.price)
#     #     if status:
#     #         if result['amount'] / 100 == self.price:
#     #             self.verified = True
#     #         self.save()
#     #     if self.verified:
#     #         return True
#     #     return False    







#     def verify_payment(self):
#         paystack = Paystack()
#         status, result = paystack.verify_payment(self.ref, self.price)
#         if status:
#             if result['amount'] / 100 == self.price:
#                 self.verified = True
#             self.save()
        
#             # Link Payment to Membership, Usermembership, and Subscription
#             # membership, _ = Membership.objects.get_or_create(user=self.user)
#             membership, _ = Membership.objects.get_or_create(membership_type=self.user)
#             # membership, _ = Membership.objects.get_or_create(membership_type=self.user)
#             user_membership, _ = Usermembership.objects.get_or_create(user=self.user)
#             # user_membership_tuple = Usermembership.objects.get_or_create(user=self.user)
#             # user_membership = user_membership_tuple[0]
#             if user_membership.membership is None:
#                 default_membership = Membership.objects.get(membership_type='free')
#                 user_membership.membership = default_membership
#                 user_membership.save()
            
#             user_membership.membership = self.user_membership  # user_membership is set before calling verify_payment
#             user_membership.paystack_id = result.get('customer', {}).get('id', '')  # Paystack returns customer ID in the result
#             user_membership.save()

#             subscription, created = Subscription.objects.get_or_create(user_membership=user_membership)
#             subscription.paystack_id = result.get('id', '')  # Paystack returns subscription ID in the result
#             subscription.active = True  # Subscription is active after successful payment
#             subscription.save()
            
#             return True
#         return False
            











# @receiver(post_save, sender=User)
# def create_usermembership(sender, instance, created, **kwargs):
#     if created:
#         # Check if a Usermembership instance already exists for the user
#         if not hasattr(instance, 'usermembership'):
#             Usermembership.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def save_usermembership(sender, instance, **kwargs):
#     instance.usermembership.save()
















# class Subscription(models.Model):
#     user_membership = models.ForeignKey(Usermembership, on_delete=models.CASCADE)
#     paystack_id = models.CharField(max_length=25)
#     active = models.BooleanField(default=True)

#     def __str__(self):
#         return self.user_membership.user.username
	
#     @property
#     def get_created_date(self):
#         subscription = paystack.Subscription.retrieve(self.paystack_subscription_id)
#         return datetime.fromtimestamp(subscription.created)
		
#     @property
#     def get_next_billing_date(self):
#           subscription = paystack.Subscription.retrieve(self.paystack_subscription_id)
#           return datetime.fromtimestamp(subscription.current_period_end)    







# class Subscription(models.Model):
#     user_membership = models.ForeignKey(Usermembership, on_delete=models.CASCADE)
#     paystack_id = models.CharField(max_length=25)
#     active = models.BooleanField(default=True)
#     next_payment_date = models.DateTimeField(null=True, blank=True)

#     def __str__(self):
#         return self.user_membership.user.username

#     def calculate_next_payment_date(self):
#         if self.next_payment_date is None:
#             # If next_payment_date is not set, set it to the current date plus 30 days
#             self.next_payment_date = timezone.now() + timedelta(days=30)
#         else:
#             # If next_payment_date is already set, add 30 days to it
#             self.next_payment_date += timedelta(days=30)

#     def save(self, *args, **kwargs):
#         if self.active:
#             # Calculate or update next payment date if subscription is active
#             self.calculate_next_payment_date()
#         super().save(*args, **kwargs)










# def verify_payment(self):
#     paystack = Paystack()
#     status, result = paystack.verify_payment(self.ref, self.price)
#     if status:
#         if result['amount'] / 100 == self.price:
#             self.verified = True
#         self.save()
    
#         # Link Payment to Membership, Usermembership, and Subscription
#         # membership = Membership.objects.get_or_create(user=self.user)
#         # user_membership = Usermembership.objects.get_or_create(user=self.user)
#         user_membership_tuple = Usermembership.objects.get_or_create(user=self.user)
#         user_membership = user_membership_tuple[0]
#         if user_membership.membership is None:
#             user_membership.membership = Membership.objects.get(slug='')  # Replace 'default_membership_slug' with the actual slug of the default membership
#             user_membership.save()
        
#         user_membership.membership = self.user_membership  # Assuming user_membership is set before calling verify_payment
#         user_membership.paystack_id = result.get('customer', {}).get('id', '')  # Assuming Paystack returns customer ID in the result
#         user_membership.save()

#         subscription, created = Subscription.objects.get_or_create(user_membership=user_membership)
#         subscription.paystack_id = result.get('id', '')  # Assuming Paystack returns subscription ID in the result
#         subscription.active = True  # Assuming the subscription should be active after successful payment
#         subscription.save()
        
#         return True
#     return False
