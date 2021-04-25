# Generated by Django 3.1.7 on 2021-04-25 05:35

import api.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_orderitem_cancelled'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='ShipperID',
            field=models.ForeignKey(default=api.models.Shipper.get_random_shipper, on_delete=django.db.models.deletion.CASCADE, to='api.shipper'),
        ),
        migrations.CreateModel(
            name='OrderHistory',
            fields=[
                ('OrderHistoryID', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('ShippingStatus', models.CharField(max_length=40)),
                ('StatusDateTime', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('OrderItemID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.orderitem')),
            ],
        ),
    ]
