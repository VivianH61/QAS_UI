# Generated by Django 4.0.6 on 2022-08-01 04:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='email',
            field=models.CharField(default='lanxin.hu@ey.com', max_length=100),
            preserve_default=False,
        ),
    ]