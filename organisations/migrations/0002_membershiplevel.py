# Generated by Django 3.1.7 on 2021-12-24 16:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organisations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MembershipLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.IntegerField(choices=[(1, 'admin'), (2, 'participant')])),
                ('hierarchy', models.IntegerField(null=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organisations.organization')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='member', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]