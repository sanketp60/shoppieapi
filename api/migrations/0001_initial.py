# Generated by Django 3.1.7 on 2021-04-06 07:50

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('ProductID', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('Name', models.CharField(max_length=50)),
                ('Description', models.CharField(max_length=50)),
                ('Category', models.CharField(max_length=50)),
                ('UnitWeight', models.FloatField()),
                ('Picture', models.CharField(max_length=300)),
            ],
        ),
    ]
