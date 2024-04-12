# Generated by Django 4.0.8 on 2024-04-12 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0014_rename_coursecompletionstatus_coursecompletionstatusperuser'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='is_active',
        ),
        migrations.AddField(
            model_name='customer',
            name='customer_resources',
            field=models.ManyToManyField(related_name='customer_resources', to='exam.customerresources'),
        ),
        migrations.AddField(
            model_name='customer',
            name='roles',
            field=models.ManyToManyField(related_name='customer_roles', to='exam.role'),
        ),
        migrations.AddField(
            model_name='customer',
            name='status',
            field=models.CharField(default='active', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='customerresources',
            name='access_type',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='resources',
            name='customer_resources',
            field=models.ManyToManyField(related_name='resources', to='exam.customerresources'),
        ),
        migrations.AddField(
            model_name='resources',
            name='parent_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='resources',
            name='status',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='resources',
            name='user_role_privileges',
            field=models.ManyToManyField(related_name='resources', to='exam.userroleprivileges'),
        ),
        migrations.AddField(
            model_name='user',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive'), ('archived', 'Archived')], default='active', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='userroleprivileges',
            name='has_read',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='userroleprivileges',
            name='has_write',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userroleprivileges',
            name='role',
            field=models.CharField(default='default_value_here', max_length=50),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(default='default_role', max_length=50),
        ),
    ]
