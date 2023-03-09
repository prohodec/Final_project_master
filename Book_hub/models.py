from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.core.exceptions import ValidationError


class Category(models.Model):
    name = models.CharField('Category', max_length=100, unique=True)
    description = models.TextField('Description')
    url = models.SlugField(max_length=150, unique=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.url:
            self.url = slugify(self.name)
        super(Category, self).save(*args, **kwargs)


class Genre(models.Model):
    name = models.CharField('Genre', max_length=100, unique=True)
    description = models.TextField('Description')
    url = models.SlugField(max_length=150, unique=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.url:
            self.url = slugify(self.name)
        super(Genre, self).save(*args, **kwargs)


def book_upload_path(instance, filename):
    return f'books/{instance.url}/{filename}'


class Book(models.Model):
    name = models.CharField('Book name', max_length=50, unique=True)
    tagline = models.CharField('Tagline for book', max_length=50, default='')
    description = models.TextField('Description')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    poster = models.ImageField('Poster', upload_to=book_upload_path, unique=True)
    file = models.FileField('Book file', upload_to=book_upload_path, unique=True)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    amount = models.PositiveIntegerField(default=0, help_text='Sum in cents(leave 0 for free post)')
    publish_date = models.DateTimeField(auto_now=True)
    url = models.SlugField(max_length=150, unique=True, blank=True, help_text='leave it for autogenerate')

    def save(self, *args, **kwargs):
        if not self.url:
            self.url = slugify(self.name)
        super(Book, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_rating(self):
        marks = ProductRating.objects.filter(book_id=self.id)
        marks_number = len(marks)
        if marks_number == 0:
            return 'no one rate'
        marks_sum = 0
        for mark in marks:
            marks_sum += mark.rating
        avg = marks_sum / marks_number
        return avg

    def get_price(self):
        return f'{(self.amount/100):.2f}'

    def get_absolute_url(self):
        return reverse('book_detail', kwargs={'slug': self.url})


class ProductRating(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()

    def save(self, *args, **kwargs):
        if ProductRating.objects.filter(book=self.book, user=self.user).exists():
            raise ValidationError("You've already rated this book")
        super(ProductRating, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.book} - {self.rating}'


class Reviews(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    text = models.TextField('Message', max_length=5000)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.book.name}.{self.user.username} - {self.text}'

    def is_user_owner(self):
        if SellLogs.objects.filter(user_id=self.user.id, book_id=self.book):
            return True
        else:
            return False


class SellLogs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} - {self.book.name}'


class UserBalance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.PositiveIntegerField(default=0, help_text='Sum in cents(leave 0 for free post)')

    def __str__(self):
        return f'{self.user} - {self.balance}'


class WithdrawalRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=0)
