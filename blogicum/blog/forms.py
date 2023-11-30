from .models import Post, Comments
from django import forms


class CommentsForm(forms.ModelForm):

    class Meta:
        model = Comments
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'cols': 80, 'rows': 15}),
        }


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = '__all__'
