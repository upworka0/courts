# Generated by Django 2.0.3 on 2018-07-29 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lawyers', '0003_auto_20180213_1123'),
    ]

    operations = [
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_update', models.IntegerField(default=0)),
            ],
        ),
    ]
