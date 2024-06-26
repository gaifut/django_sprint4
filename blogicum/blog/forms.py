from .models import Post, Comments
from django import forms


class CommentsForm(forms.ModelForm):

    class Meta:
        model = Comments
        fields = ('text',)


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)
