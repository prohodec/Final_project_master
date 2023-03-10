# Generated by Django 4.1.7 on 2023-02-27 20:16

import Book_hub.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Book_hub', '0006_alter_book_file_alter_book_name_alter_book_poster_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='file',
            field=models.FileField(unique=True, upload_to=Book_hub.models.book_upload_path, verbose_name='Book file'),
        ),
        migrations.AlterField(
            model_name='book',
            name='poster',
            field=models.ImageField(unique=True, upload_to=Book_hub.models.book_upload_path, verbose_name='Poster'),
        ),
    ]
