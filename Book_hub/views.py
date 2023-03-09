import re
import stripe
import os
from django.db.models import Avg, Q
from stripe.error import SignatureVerificationError
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.utils.html import strip_tags
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, UpdateView
from django.views.generic.base import View
from django.views.generic.edit import FormView
from .models import Book, SellLogs, UserBalance, Category, Genre, WithdrawalRequest
from django.contrib.auth.models import User
from .forms import ReviewForm, RatingForm, BookAddingForm
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.views.generic import TemplateView

stripe.api_key = settings.STRIPE_SECRET_KEY


class GenreCategory:

    def get_genres(self):
        return Genre.objects.all()

    def get_category(self):
        return Category.objects.all()


class BookView(GenreCategory, ListView):
    model = Book
    queryset = Book.objects.all()
    paginate_by = 6
    ordering = ['id']


class BookDetailView(GenreCategory, DetailView):
    model = Book
    slug_field = 'url'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['STRIPE_PUBLIC_KEY'] = settings.STRIPE_PUBLIC_KEY
        user = self.request.user
        if user.is_authenticated:
            if SellLogs.objects.filter(user=user, book=context['book']):
                context['user_owner'] = True

        return context


class ReviewAdding(LoginRequiredMixin, View):

    def post(self, request, pk):
        form = ReviewForm(request.POST)
        redirect_url = Book.objects.get(id=pk)
        if form.is_valid():
            form.save()

        return redirect('book_detail', redirect_url.url)


class CreateCheckoutSession(LoginRequiredMixin, View):

    def post(self, request, pk):
        book = Book.objects.get(id=pk)
        DOMAIN = "http://127.0.0.1:8000"
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': book.amount,
                        'product_data': {
                            'name': book.name
                        },
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                "product_id": book.id,
                "customer_id": request.user.id
            },
            mode='payment',
            success_url=DOMAIN + '/success/',
            cancel_url=DOMAIN + '/cancel/',
        )
        return JsonResponse({
            'id': checkout_session.id
        })


class SuccessView(TemplateView):
    template_name = "Book_hub/success.html"


class CancelView(TemplateView):
    template_name = "Book_hub/cancel.html"


class BookSent(LoginRequiredMixin, View):

    def post(self, request):
        book = Book.objects.get(id=request.POST['book_id'])
        text_content = strip_tags('<h1>Thank you for using our site, here is your book: </h1>')
        email_subject = 'Sending a book'
        from_email = settings.EMAIL_HOST_USER
        to_email = request.POST['user_email']

        email = EmailMessage(email_subject, text_content, from_email, [to_email], reply_to=[from_email])
        file_path = book.file.url
        file_path = file_path[1:]

        with open(file_path, 'rb') as f:
            file_data = f.read()
            email.attach(f'{book.name}.pdf', file_data, 'application/pdf')

        email.send(fail_silently=False)

        return render(request, 'Book_hub/book_detail.html',
                      {'book': book, 'message': 'The book has been emailed to you'})


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        print(e)
        return HttpResponse(status=400)
    except SignatureVerificationError as e:
        # Invalid signature
        print(e)
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        product_id = session['metadata']['product_id']
        customer_id = session['metadata']['customer_id']
        book = Book.objects.get(id=product_id)
        user = User.objects.get(id=customer_id)

        sell_log = SellLogs(user=user, book=book)
        sell_log.save()

        user_balance_replenishment = UserBalance.objects.filter(user=book.author)
        if user_balance_replenishment:
            user_balance_replenishment = user_balance_replenishment.first()
            user_balance_replenishment.balance += book.amount
            user_balance_replenishment.save()
        else:
            user_balance_replenishment = UserBalance(user=book.author, balance=book.amount)
            user_balance_replenishment.save()

        text_content = strip_tags('<h1>Thank you for using our site, here is your book: </h1>')
        email_subject = 'Sending a book'
        from_email = settings.EMAIL_HOST_USER
        to_email = session['customer_details']['email']

        email = EmailMessage(email_subject, text_content, from_email, [to_email], reply_to=[from_email])
        file_path = book.file.url
        file_path = file_path[1:]

        with open(file_path, 'rb') as f:
            file_data = f.read()
            email.attach(f'{book.name}.pdf', file_data, 'application/pdf')

        email.send(fail_silently=False)

    return HttpResponse(status=200)


class RatingAdding(LoginRequiredMixin, View):

    def post(self, request, pk):
        form = RatingForm(request.POST)
        book = Book.objects.get(id=pk)

        if form.is_valid():
            try:
                form.save()
            except ValidationError:

                return render(request, 'Book_hub/book_detail.html',
                              {'book': book, 'error': 'You`ve already rated this book'})

        return redirect('book_detail', book.url)


class FilterBooksView(GenreCategory, ListView):
    template_name = 'Book_hub/book_list.html'
    paginate_by = 6

    def get_queryset(self):
        min_rating = float(self.request.GET.get('min_rating'))
        max_rating = float(self.request.GET.get('max_rating'))

        if min_rating == 1 and max_rating == 5:
            queryset = Book.objects.all()
            if 'genre' in self.request.GET:
                queryset = queryset.filter(genre__name__in=self.request.GET.getlist('genre'))
            if 'category' in self.request.GET:
                queryset = queryset.filter(category__name__in=self.request.GET.getlist('category'))

            return queryset.order_by('id')
        else:
            queryset = Book.objects.annotate(avg_rating=Avg('productrating__rating')).filter(
                Q(avg_rating__gte=min_rating) &
                Q(avg_rating__lte=max_rating))
            # Q для более сложных запросов с and or not, annotate для добавленрия "аннотации" к каждому обьекту
            # записи из запроса, принимает агрегатную функцию или sqlвыражения для зисчисления и заполения доп поля (
            # тут авг)
            if 'genre' in self.request.GET:
                queryset = queryset.filter(genre__name__in=self.request.GET.getlist('genre'))
            if 'category' in self.request.GET:
                queryset = queryset.filter(category__name__in=self.request.GET.getlist('category'))

            return queryset.order_by('id')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['query_params'] = self.request.META.get('QUERY_STRING', '')
        context['query_params'] = re.sub(r'&?page=\d+&', '', context['query_params'])    # для замены ?page=x& на ''
        return context


class BookSearch(ListView):
    template_name = 'Book_hub/book_list.html'
    paginate_by = 6

    def get_queryset(self):
        return Book.objects.filter(name__icontains=self.request.GET.get('book_name'))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['book_name'] = f"&book_name={self.request.GET.get('book_name')}"   # для сейва пагинации
        return context


class UserPurchasedBook(LoginRequiredMixin, ListView):
    template_name = 'Book_hub/user_purchased_book.html'
    paginate_by = 6

    def get_queryset(self):
        return Book.objects.filter(selllogs__user=self.request.user).order_by('id')


class UserPostedBook(LoginRequiredMixin, ListView):
    template_name = 'Book_hub/user_posted_books_list.html'
    paginate_by = 6

    def get_queryset(self):
        return Book.objects.filter(author=self.request.user).order_by('id')


class BookDelete(LoginRequiredMixin, View):

    def post(self, request):
        book = Book.objects.get(id=int(request.POST['book_id']))
        book_name = book.name
        file_path = book.file.path
        poster_path = book.poster.path
        dir_path = os.path.dirname(poster_path)

        if book.author_id == request.user.id:
            book.delete()
            if os.path.isfile(file_path):
                os.remove(file_path)
            if os.path.isfile(poster_path):
                os.remove(poster_path)
            if os.path.isdir(dir_path):
                os.rmdir(dir_path)
            return render(request, 'Book_hub/delete_status.html', {'book_name': book_name})
        else:
            return render(request, 'Book_hub/delete_status.html', {'error': 'Something went wrong, please try again'
                                                                            ' later or email us'})


class AddBookView(LoginRequiredMixin, FormView):
    template_name = 'Book_hub/book_adding.html'
    form_class = BookAddingForm
    success_url = reverse_lazy('posted_books')

    def form_valid(self, form):
        book = form.save(commit=False)
        book.author = self.request.user
        book.save()

        return super().form_valid(form)


class BookUpdateView(LoginRequiredMixin, UpdateView):
    model = Book
    form_class = BookAddingForm
    template_name = 'Book_hub/book_adding.html'
    success_url = reverse_lazy('posted_books')

    def form_valid(self, form):
        user = self.request.user
        book = self.get_object()    # книга данного вью

        if user != book.author:
            return HttpResponse('You are not book owner')

        return super().form_valid(form)


class WithdrawalStatusView(TemplateView):
    template_name = "Book_hub/withdrawal_status.html"


class Withdrawal(LoginRequiredMixin, View):

    def get(self, request):
        user_balance = UserBalance.objects.filter(user=request.user)

        if not user_balance:
            user_balance = 0
        else:
            user_balance = user_balance[0].balance

        return render(request, 'Book_hub/user_cash_withdrawal.html', {'user_balance': user_balance})

    def post(self, request):
        amount = int(request.POST['user_amount'])
        if amount:
            balance = UserBalance.objects.get(user=request.user)
            balance.balance -= amount
            balance.save()
            wr = WithdrawalRequest.objects.create(user=request.user, amount=amount)
            wr.save()
            return redirect('withdrawal_status')
        else:
            return redirect('home')

