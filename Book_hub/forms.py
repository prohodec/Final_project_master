from django import forms
from .models import Reviews, ProductRating, Book


class ReviewForm(forms.ModelForm):

    class Meta:
        model = Reviews
        fields = ('book', 'user', 'text')


class RatingForm(forms.ModelForm):

    class Meta:
        model = ProductRating
        fields = ('book', 'user', 'rating')


class BookAddingForm(forms.ModelForm):

    class Meta:
        model = Book
        fields = ['name', 'tagline', 'description', 'poster', 'file', 'genre', 'category', 'amount']
