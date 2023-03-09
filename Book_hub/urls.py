from django.urls import path
from . import views

urlpatterns = [
    path('', views.BookView.as_view(), name="home"),
    path('review-add/<int:pk>/', views.ReviewAdding.as_view(), name='review_add'),
    path('rating-add/<int:pk>/', views.RatingAdding.as_view(), name='rating_add'),
    path('create-checkout-session/<int:pk>/', views.CreateCheckoutSession.as_view(), name='create-checkout-session'),
    path('cancel/', views.CancelView.as_view(), name='cancel'),
    path('success/', views.SuccessView.as_view(), name='success'),
    path('book-sent/', views.BookSent.as_view(), name='book_sent'),
    path('filter/', views.FilterBooksView.as_view(), name='books_filter'),
    path('search/', views.BookSearch.as_view(), name='book_name_search'),
    path('user_purchased_book/', views.UserPurchasedBook.as_view(), name='purchased_books'),
    path('user_posted_books/', views.UserPostedBook.as_view(), name='posted_books'),
    path('book_delete/', views.BookDelete.as_view(), name='book_delete'),
    path('user_posted_books/book_add/', views.AddBookView.as_view(), name='add_book'),
    path('withdrawal/', views.Withdrawal.as_view(), name='withdrawal'),
    path('withdrawal_status/', views.WithdrawalStatusView.as_view(), name='withdrawal_status'),
    path('<slug:slug>/', views.BookDetailView.as_view(), name='book_detail'),
    path('<int:pk>/edit/', views.BookUpdateView.as_view(), name='book_update'),
    path('webhooks/stripe/', views.stripe_webhook, name='stripe_webhook'),
]
