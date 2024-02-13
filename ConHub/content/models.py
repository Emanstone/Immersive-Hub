from django.db import models
from membership.models import Membership
from django.utils.text import slugify
from django.urls import reverse
from embed_video.fields import EmbedVideoField

# Create your models here.

class Video(models.Model):
    slug = models.SlugField(max_length=255, unique=True, default='video-slug')
    title = models.CharField(max_length=150, blank=True)
    description = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now=True)
    video_file = models.FileField(upload_to="video/%Y", null=True)
    

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-date_created']
    
    def get_absolute_url(self):
        return reverse('content:vdetail', kwargs={'slug':self.slug})




class Contentpd(models.Model):
    slug = models.SlugField(max_length=255, unique=True)
    title = models.CharField(max_length=150)
    description = models.TextField()
    allowed_memberships = models.ManyToManyField(Membership)
    position = models.IntegerField()
    pdf_file = models.FileField(upload_to='pdfs/')
    date_created = models.DateTimeField(auto_now_add=True)
    # thumbnails = models.ImageField()


    def save(self, *args, **kwargs):
        if not self.slug or self.slug != slugify(f'pdf-{self.title}'):  # Check for missing or outdated slug
            self.slug = slugify(f'pdf-{self.title}')  # Generate slug with prefix
        super().save(*args, **kwargs)


    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-date_created']
    

    def get_absolute_url(self):
        return reverse('content:pdetail', kwargs={'cpdf_slug':self.slug})




class Content(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=150)
    description = models.TextField()
    allowed_memberships = models.ManyToManyField(Membership)
    position = models.IntegerField()
    date_created = models.DateTimeField(auto_now_add=True)
    video_url = EmbedVideoField()
    video = models.ForeignKey(Video, on_delete=models.SET_NULL, null=True, blank=True)
    pdf_content = models.ForeignKey(Contentpd, on_delete=models.SET_NULL, null=True, blank=True)
    # thumbnails = models.ImageField()


    def save(self, *args, **kwargs):
        if not self.slug or self.slug != slugify(f'video-{self.title}'):  # Check for missing or outdated slug
            self.slug = slugify(f'video-{self.title}')  # Generate slug with prefix
        super().save(*args, **kwargs)



    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-date_created']
    
    def get_absolute_url(self):
        return reverse('content:detail', kwargs={'slug':self.slug})

    



















# To associate a PDF file with a Content object:

# content_instance = Content.objects.get(id=1)  # Get the desired content object
# content_pdf = Contentpd.objects.create(pdf_file="path/to/your/pdf.pdf")  # Create a Contentpd object with the PDF
# content_instance.pdf_content = content_pdf  # Link the Contentpd object to the Content object
# content_instance.save()  # Save the changes


# To access the PDF file from a Content object:

# content_instance = Content.objects.get(id=1)
# if content_instance.pdf_content:
#     pdf_file = content_instance.pdf_content.pdf_file.url  # Get the URL of the PDF file