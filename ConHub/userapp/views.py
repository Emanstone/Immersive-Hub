from django.shortcuts import render, redirect, HttpResponse
from django.views.generic import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from .models import Userprofile
from membership.models import Membership, Usermembership
import uuid
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

# from django.contrib.auth.mixins import LoginRequiredMixin


# Create your views here.

@method_decorator(csrf_protect, name='dispatch')
class Signup(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'user/signup.html')
    
    def post(self, request):
        if request.method == 'POST':
            email = request.POST.get('email')
            username = request.POST.get('username')
            password = request.POST.get('password')
            password2 = request.POST.get('password2')

            if password != password2:
                return render(request, 'user/signup.html', {'error': 'Passwords do not match'})
            
            # Store the username in session
            request.session['username'] = username

            # Create user object without saving to database
            user = User.objects.create_user(username=username, email=email, password=password, is_active=False)

            # Generate a link for completing the registration
            activation_key = str(uuid.uuid4())
            profile = Userprofile.objects.create(user=user, activation_key=activation_key)
            registration_link = f"http://127.0.0.1:8000/register/{profile.activation_key}/"

            send_mail(
                'Complete Your Registration',
                f'Use this link to complete your registration: {registration_link}',
                'emchadexglobal@gmail.com',
                [email],
                fail_silently=False,
            )

            # Redirect to the registration activation page
            return HttpResponse('Check your email for a link to complete your registration.')

        return render(request, 'user/signup.html')





class RegisterActivation(View):
    def get(self, request, activation_key):
        try:
            # Find the user profile with the given activation key
            profile = Userprofile.objects.get(activation_key=activation_key)

            # Activate the associated user
            user = profile.user
            user.is_active = True
            user.save()

            # Assign 'free' membership to the user if not already assigned
            free_membership = Membership.objects.get(membership_type='free')
            user_membership, created = Usermembership.objects.get_or_create(user=user)
            if created:
                user_membership.membership = free_membership
                user_membership.save()
            elif user_membership.membership is None:
                user_membership.membership = free_membership
                user_membership.save()

            # Render a success page or redirect to registration page
            messages.success(request, 'Activation successful. You can now continue with your registration.')
            return render(request, 'user/register.html', {'user': user})

        except Userprofile.DoesNotExist:
            # Render an error page or redirect to an error page
            messages.error(request, 'Invalid activation key. Please contact support.')
            return redirect('error_page')    








class Register(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'user/register.html')

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            # Retrieve data from the form
            fullname = request.POST.get('fullname')
            country = request.POST.get('country')
            dob = request.POST.get('dob')

            # # Get the user from the request
            # user = request.user

            # Retrieve username from session
            username = request.session.get('username')

            if not username:
                messages.error(request, "Username is required. Please complete the signup process first.")
            #     return redirect('userapp:signup')
            
            try:
                # Retrieve the user instance associated with the username
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # If user does not exist, handle the error accordingly
                return HttpResponse("User does not exist.")

            # Create or update the user profile
            profile, profile_created = Userprofile.objects.get_or_create(user=user)
            profile.fullname = fullname
            profile.country = country
            profile.dob = dob
            profile.save()

            # free_membership = Membership.objects.get(membership_type='free')
            # user_membership, created = Usermembership.objects.get_or_create(user=user, defaults={'membership': free_membership})

            # # Ensure 'free' membership is assigned
            # if created:
            #     user_membership.membership = free_membership
            #     user_membership.save()


            return redirect('userapp:login')  # Redirect to a success page

        return render(request, 'user/register.html')










class Login(View):
    def get(self, request):
        return render(request, 'user/login.html') 
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            return HttpResponse('Username and password are required', status=400)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return HttpResponse('Username not found', status=404)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('content:list')
        else:
            return HttpResponse('Incorrect password, try again', status=401)
    





def Logout(request):
    logout(request)
    return redirect('userapp:home')




class Homepage(View):
    def get(self, request):
        
        return render(request, 'index.html')
    


















# class BaseProfileView(View):

#     def get(self, request, *args, **kwargs):
#         user_membership = get_user_membership(request)
#         user_subscription = get_user_subscription(request)

#         # Get profile information using the get_profile_info method
#         profile_info = self.get_profile_info(request.user)

#         context = {
#             'user_membership': user_membership,
#             'user_subscription': user_subscription,
#             **profile_info  # Include profile_info in the context
#         }
#         return render(request, 'membership/profile.html', context=context)



#     def get_profile_info(self, user):
#         try:
#             user = Userprofile.objects.get(user=user)
            
#             profile_info = {
#                 'profile_image_url': user.profile_image.url if user.profile_image else None,
#                 'username': user.username,
#                 'full_name': user.fullname,
#                 'country': user.country,
#                 'dob': user.dob,
#             }

#             return {'profile_info': profile_info}

#             # return {'profile_info': profile_info, 'profile_complete': profile_complete}

#         except User.DoesNotExist:
#             return {}






# class ProfilePage(LoginRequiredMixin, BaseProfileView):
#     # login_url = 'login'

#     def get(self, request):
#         user_profile = Userprofile.objects.get(user=request.user)
#         if user_profile.profile_image:
#             profile_image_url = user_profile.profile_image.url
#         else:
#             profile_image_url = None  # Or a default image URL
        

#         # combining 2 different dictionaries using the spread syntax : which is formed by **(multoplication operator)
#         context = {**self.get_profile_info(request.user), 
#                    **{'profile_image_url': profile_image_url}}

#         if not context:
#             # return redirect('editprofile')
#             pass

#         return render(request, 'membership/profile.html', context=context)
#         return render(request, 'membership/profile.html')

#     def post(self, request):
#         # Process the submitted form data
#         # Redirect to the profile page
#         return redirect('userapp:profile')





# class EditProfilePage(LoginRequiredMixin, View):
#     login_url = 'login'
#     def get(self, request):
        
#         # context = self.get_profile_info(request.user)
#         try:
#             user = Userprofile.objects.get(user=request.user)
#         except Userprofile.DoesNotExist:
#             return redirect('userapp:signup')

#         user_profile = Userprofile.objects.get(user=request.user)
#         if user_profile.profile_image:
#             profile_image_url = user_profile.profile_image.url
#         else:
#             profile_image_url = None  # Or a default image URL

#         # context = {'profile_image_url': user_profile.profile_image.url,}   


#         context = {
#             'profile_info': {
#                 'profile_image_url': user.profile_image.url if user.profile_image else None,
#                 'username': user.username,
#                 'fullname': user.fullname,
#                 'email': user.email,
#                 'country': user.country,
#                 'dob': user.dob,
#             },

#             'form_data': {
#             'username': user.username,
#                 'fullname': user.fullname,
#                 'email': user.email,
#                 'country': user.country,
#                 'dob': user.dob,
#             },
#         }

#         if not context:
#             return redirect('editprofile')

#         return render(request, 'usertemp/editprofile.html', context=context)


#     def post(self, request):
#         profile_image = request.FILES.get('postimage')
#         username = request.POST.get('Username')
#         fullname = request.POST.get('Fullname')
#         email = request.POST.get('email')
#         address = request.POST.get('Country')
#         dob = request.POST.get('dob')
        

#         user = Userprofile.objects.get(user=request.user)

#         # Get all form fields to be validated
#         fields = {
#             'username': username,
#             'fullname': fullname,
#             'email': user.email,
#             'country': country,
#             'dob': dob,
#         }

#         # Validate each field, ignoring empty fields and preventing 'none' values
#         for field_value in fields.items():
#             if field_value and field_value != 'none':
#                 if not field_value:
#                     # If the field is empty, skip validation
#                     continue


#         # Process the uploaded profile image (if any)
#         if profile_image:
#             user.profile_image = profile_image
#             user.save()

#         # Update author information
#         user.username = username
#         user.fullname = fullname
#         user.email = email
#         user.country = country
#         user.dob = dob
#         user.save()
#         # messages.success(request, 'Profile Updated Successfully')
#         return redirect('profilepage')




# class Dashboard(View, LoginRequiredMixin):
    
#     def get(self, request):

#         try:
#             user_profile = Userprofile.objects.get(user=request.user)
#         except Userprofile.DoesNotExist:
#             # Create a profile for superusers who don't have one
#             if request.user.is_superuser:
#                 Userprofile.objects.create(user=request.user)
#             else:
#                 user_profile = None

#         context = {
#             'user_profile': user_profile,            
#         }

#         return render(request, 'index.html', context=context)        



























# class Signup(View):
#     def get(self, request, *args, **kwargs):
#         return render(request, 'user/signup.html')
    
#     def post(self, request):
#         if request.method == 'POST':
#             email = request.POST.get('email')
#             username = request.POST.get('username')
#             password = request.POST.get('password')
#             password2 = request.POST.get('password2')

#             if password != password2:
#               return render(request, 'user/signup.html', {'error': 'Passwords do not match'})

#             # Create a user without saving it to the database
#             user = User.objects.create_user(username=username, email=email, password=password, is_active=False)
#             # Generate a link for completing the registration
#             activation_key = str(uuid.uuid4())
#             profile = Userprofile.objects.create(user=user, activation_key=activation_key)
#             registration_link = f"http://127.0.0.1:8000/register/{profile.activation_key}/"

#             # Send registration link to the user's email
#             send_mail(
#                 'Complete Your Registration',
#                 f'Use this link to complete your registration: {registration_link}',
#                 'emchadexglobal@gmail.com',
#                 [email],
#                 fail_silently=False,
#             )
#             return HttpResponse('Check your mail for link to complete your registration')



# class RegisterActivation(View):
#     def get(self, request, activation_key):
#         try:
#             # Find the user profile with the given activation key
#             profile = Userprofile.objects.get(activation_key=activation_key)
#             # Activate the associated user
#             user = profile.user
#             user.is_active = True
#             user.save()
#             # Render a success page or redirect to registration page
#             messages.success(request, 'Activation successful. You can now continue with your registration.')
#             # return redirect('register')
#             return render(request, 'user/register.html', {'user': user})

#         except Userprofile.DoesNotExist:
#             # Render an error page or redirect to an error page
#             messages.error(request, 'Invalid activation key. Please contact support.')
#             return redirect('error_page')
    



# class RegisterActivation(View):
#     def get(self, request, activation_key):
#         try:
#             # Find the user profile with the given activation key
#             profile = Userprofile.objects.get(activation_key=activation_key)

#             # Activate the associated user
#             user = profile.user
#             user.is_active = True
#             user.save()

#             # Assign 'free' membership to the user if not already assigned
#             free_membership = Membership.objects.get(membership_type='free')
#             user_membership, created = Usermembership.objects.get_or_create(user=user)
#             if created:
#                 user_membership.membership = free_membership
#                 user_membership.save()
#             elif user_membership.membership is None:
#                 user_membership.membership = free_membership
#                 user_membership.save()

#             # Render a success page or redirect to registration page
#             messages.success(request, 'Activation successful. You can now continue with your registration.')
#             return render(request, 'user/register.html', {'user': user})

#         except Userprofile.DoesNotExist:
#             # Render an error page or redirect to an error page
#             messages.error(request, 'Invalid activation key. Please contact support.')
#             return redirect('error_page')

