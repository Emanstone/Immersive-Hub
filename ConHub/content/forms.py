from django import forms
from .models import Contentpd, Video

class ContentpdForm(forms.ModelForm):
    class Meta:
        model = Contentpd
        fields = ['slug', 'title', 'description']



class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'description']