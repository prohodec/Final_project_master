from django import template
from Book_hub.models import Book

register = template.Library()


@register.inclusion_tag('Book_hub/tags/last_added_books.html')  # inclusion tag last books
def get_last_books():
    books = Book.objects.order_by('-publish_date')[:3]
    return {'last_books': books}
