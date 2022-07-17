# Generated by Django 2.2.19 on 2022-07-14 20:47

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_auto_20220710_1501'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientvolume',
            name='amount',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Минимальное количество ингридиентов 1')], verbose_name='Количество'),
        ),
    ]