from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Book, Reviews, Genre, ProductRating, Category, SellLogs, UserBalance


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'url')
    list_display_links = ('name', 'id')
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'url')
    list_display_links = ('name', 'id')
    search_fields = ('name',)


class ReviewInline(admin.TabularInline):
    model = Reviews
    extra = 1


class RatingInline(admin.TabularInline):
    model = ProductRating
    extra = 1


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'tagline', 'category', 'genre', 'author', 'get_poster', 'amount', 'publish_date')
    list_display_links = ('name', 'id')
    list_filter = ('category', 'genre')
    search_fields = ('name',)
    save_on_top = True
    inlines = [ReviewInline, RatingInline]
    readonly_fields = ('get_poster',)
    # fieldsets =

    def get_poster(self, obj):
        return mark_safe(f'<img src={obj.poster.url} width=60 height=70>')   # вывод тега, а не как строку

    get_poster.short_description = 'Poster'


@admin.register(Reviews)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'user', 'text')
    list_display_links = ('book', 'id')
    list_filter = ('book', 'user')
    readonly_fields = ('user',)
    search_fields = ('book__name', 'user__username',)


@admin.register(SellLogs)
class SellLogsAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'user')
    list_display_links = ('book', 'id')
    list_filter = ('user',)
    search_fields = ('book__name', 'user__username',)


@admin.register(ProductRating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'user', 'rating')
    list_display_links = ('book', 'id')
    list_filter = ('user', 'book')


@admin.register(UserBalance)
class UserBalanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'balance')
    list_display_links = ('user', 'id')


admin.site.site_title = 'Bookshelf hub'
admin.site.site_header = 'Bookshelf hub'
