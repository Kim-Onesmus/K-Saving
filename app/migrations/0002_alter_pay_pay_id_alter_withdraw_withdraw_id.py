# Generated by Django 5.0.1 on 2024-02-04 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pay',
            name='pay_id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='withdraw',
            name='withdraw_id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
