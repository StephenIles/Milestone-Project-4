# Generated by Django 5.1.3 on 2024-11-28 22:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0010_alter_userprofile_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='stripe_subscription_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='subscription_end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
