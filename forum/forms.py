from django.forms import ModelForm, Textarea, TextInput
from .models import Post, Response, Reply

from django import forms
from django.core.exceptions import ValidationError


def validate_file_extension(value):
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.mp4', '.avi', '.pdf', '.doc', '.docx']
    ext = value.name.split('.')[-1].lower()
    if ext not in allowed_extensions:
        raise ValidationError('Выбранный файл имеет недопустимое расширение.')


class PostForm(ModelForm):
    media = forms.FileField(label='Здесь вы можете загрузить картинки, видео, файлы', required=False,
                            validators=[validate_file_extension])

    class Meta:
        model = Post
        fields = ['title', 'text', 'postCategory', 'media']
        widgets = {
            'title': Textarea(attrs={'class': 'title_class'}),
            'text': Textarea(attrs={'class': 'text_class'}),
        }

        labels = {
            'title': 'Заголовок',
            'text': 'Текст',
            'postCategory': 'Категория',
        }


class PostResponseForm(ModelForm):
    class Meta:
        model = Response
        fields = ['text']
        widgets = {
            'text': TextInput(attrs={'class': 'text_class'}),
        }


class ReplyForm(ModelForm):
    class Meta:
        model = Reply
        fields = ['text', ]
        widgets = {
            'text': TextInput(attrs={'class': 'text_class'}),
        }
