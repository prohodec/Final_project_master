# Generated by Django 4.1.7 on 2023-03-03 16:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Book_hub', '0009_remove_reviews_name_reviews_user_selllogs'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productrating',
            name='created_at',
        ),
    ]
