# Generated by Django 4.1.7 on 2023-04-21 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LoanPool',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('loan_id', models.IntegerField(null=True)),
                ('status', models.PositiveSmallIntegerField()),
                ('status_name', models.CharField(max_length=255, null=True)),
                ('payload', models.TextField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'ghl_loandatapool',
            },
        ),
    ]
