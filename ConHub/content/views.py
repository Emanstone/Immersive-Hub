from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, View, CreateView
from .models import Content, Video, Contentpd
from membership.models import Usermembership, Membership, MEMBERSHIP_CHOICES
from django.http import HttpResponse
from .forms import ContentpdForm, VideoForm
from django.contrib import messages
import pdfkit


# Create your views here.

class ContentAndVideoList(ListView):
    model = Content  # Use either Content or Video as the base model
    template_name = 'content/contentlist.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        videos = Video.objects.all()  # Fetch all videos
        docs = Contentpd.objects.all()  # Fetch all PDFs
        context['videos'] = videos
        context['articles'] = docs
        return context



class Contentdetail(DetailView):
    model = Content
    template_name = 'content/contentdetail.html'



class Videodetail(DetailView):
    model = Video 
    template_name = 'content/videodetail.html'




# # class Contentpdfdetail(View):
# #     model = Video 
# #     template_name = 'content/pdfdetail.html'
    


class Contentpdfdetail(View):
    def get(self, request, cpdf_slug, *args, **kwargs):
        content_qs = Contentpd.objects.filter(slug=cpdf_slug)

        from membership.views import get_user_subscription, get_user_membership
        user_membership = get_user_membership(request)
        user_subscription = get_user_subscription(request)


        if content_qs:
            conpdf = content_qs.first()

        context = {
            'object': conpdf,
            'user_membership': user_membership,
            'user_subscription': user_subscription,
        }

        try:
            user_membership = Usermembership.objects.filter(user=request.user).first()

            if user_membership and user_membership.membership:
                user_membership_type = user_membership.membership.membership_type
                pdf_allowed_mtypes = conpdf.allowed_memberships.all()

                if pdf_allowed_mtypes.filter(membership_type=user_membership_type).exists():
                    context['object'] = conpdf

        except TypeError:
            pass

        return render(request, 'content/pdfdetail.html', context=context)






class VideoUpload(CreateView):
    model = Video
    fields = ['video_file', 'title', 'description']
    template_name = 'content/videoupload.html'
    success_url = reverse_lazy('content:list')

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.instance.user = self.request.user
            self.object = form.save()
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))
        


class Video_embed(CreateView):

    model = Content
    fields = ['slug', 'title', 'description', 'allowed_memberships', 'position', 'video_url', 'video', 'pdf_content']
    template_name = 'content/embed.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subs'] = Membership.objects.all()
        context['videos'] = Video.objects.all()
        context['pdfs'] = Contentpd.objects.all()
        return context

    success_url = reverse_lazy('content:list')


    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)        
    




class Pdf_upload(CreateView):

    model = Contentpd
    fields = ['slug', 'title', 'description', 'allowed_memberships', 'position', 'pdf_file']
    template_name = 'content/pdf_upload.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sub'] = Membership.objects.all()
        return context

    success_url = reverse_lazy('content:list')


    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)        





def cliplay(request):
    videos = Video.objects.all()
    return render(request, 'content/clip_play.html', {"videos": videos})




def linked_video(request):
    links = Content.objects.all()

    from membership.views import get_user_subscription, get_user_membership    # lazy import
    user_membership = get_user_membership(request)
    user_subscription = get_user_subscription(request)
    

    context = {
            'user_membership': user_membership,
            'user_subscription': user_subscription,
            'links': links,
        }


    return render(request, 'content/link_play.html', context=context)





def pdf_viewer(request, content_id):
    # Get the Contentpd object based on the content_id parameter
    mypdf = get_object_or_404(Contentpd, id=content_id)

    if mypdf:
        # Get the path to the PDF file
        pdf_path = mypdf.pdf_file.path

        # Open and read the PDF file
        with open(pdf_path, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{mypdf.pdf_file.name}"'
            return response
    else:
        return HttpResponse("PDF not found.")






def edit_embed(request, pk):
    # Retrieve the instance of MyModel using the provided primary key (pk)
    embeded = get_object_or_404(Content, pk=pk)

    if request.method == 'POST':
        # If the form is submitted, update the instance with the new data
        embeded.slug = request.POST.get('slug')
        embeded.title = request.POST.get('title')
        embeded.description = request.POST.get('description')
        embeded.save()
        # Redirect to a success URL or display a success message
        return redirect('content:list')

    # Render the template with the instance data
    return render(request, 'content/edit_embed.html', {'embeded': embeded})





def edit_pdf(request, pk):
    # Retrieve the instance of MyModel using the provided primary key (pk)
    pdf = get_object_or_404(Contentpd, pk=pk)

    if request.method == 'POST':
        # If the form is submitted, populate the form with the POST data and the instance
        form = ContentpdForm(request.POST, instance=pdf)
        if form.is_valid():
            # Save the form if it's valid
            form.save()
            # Redirect to a success URL or display a success message
            return redirect('content:list')
    else:
        # If it's a GET request, create a form instance and populate it with the instance data
        form = ContentpdForm(instance=pdf)

    # Render the template with the form
    return render(request, 'content/edit_pdf.html', {'form': form})





def edit_video(request, pk):
    # Retrieve the instance of MyModel using the provided primary key (pk)
    vid = get_object_or_404(Video, pk=pk)

    if request.method == 'POST':
        # If the form is submitted, populate the form with the POST data and the instance
        form = VideoForm(request.POST, instance=vid)
        if form.is_valid():
            # Save the form if it's valid
            form.save()
            # Redirect to a success URL or display a success message
            return redirect('content:list')
    else:
        # If it's a GET request, create a form instance and populate it with the instance data
        form =VideoForm(instance=vid)

    # Render the template with the form
    return render(request, 'content/edit_video.html', {'form': form})









# messages.warning(request, '')
# messages.info(request, '')
# messages.error(request, '')   
    

# messages.ERROR:'danger'


