# Generated by Django 5.1.2 on 2024-11-09 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productApp', '0008_remove_order_parent_order_id_remove_order_product_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='seat_number',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]