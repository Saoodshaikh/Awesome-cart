# Generated by Django 4.1 on 2022-08-30 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_orders_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='email',
            field=models.CharField(default='', max_length=50),
        ),
    ]
