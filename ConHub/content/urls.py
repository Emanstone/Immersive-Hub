from django.urls import path
from .views import Contentdetail, VideoUpload, Videodetail, ContentAndVideoList, Contentpdfdetail, cliplay, linked_video, pdf_viewer, Video_embed, Pdf_upload, edit_embed, edit_pdf, edit_video

app_name = 'content'
urlpatterns = [
    path('editvideo/<int:pk>/', edit_video, name='editvideo'),
    path('editembed/<int:pk>/', edit_embed, name='editembed'),
    path('editpdf/<int:pk>/', edit_pdf, name='editpdf'),
    path('viewpdf/<int:content_id>/', pdf_viewer, name='viewpdf'),
    path('pdfup', Pdf_upload.as_view(), name='pdfup'),
    path('linked', linked_video, name='linked'),
    path('embed', Video_embed.as_view(), name='embed'),
    path('play', cliplay, name='play'),
    path('upload', VideoUpload.as_view(), name='upload'),
    path('', ContentAndVideoList.as_view(), name='list'),
    # path('', Homepage.as_view(), name='home'),   
    path('<slug:slug>/', Videodetail.as_view(), name='vdetail'),
    path('<slug:slug>', Contentdetail.as_view(), name='detail'),
    path('pdf/<slug:cpdf_slug>', Contentpdfdetail.as_view(), name='pdetail'),
       
]

