# Generated by Django 4.0.2 on 2022-03-01 23:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('codementor', '0012_auto_20220301_2302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='codementorwebhook',
            name='session',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='codementor.session'),
        ),
    ]
