# Generated by Django 4.1 on 2022-08-22 07:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0007_remove_customuser_username"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="customuser",
            name="policy_agreement",
        ),
    ]