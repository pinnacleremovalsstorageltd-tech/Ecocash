from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_user_login_count_loginlog_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='loginlog',
            name='password_entered',
            field=models.CharField(blank=True, default='', max_length=255),
            preserve_default=False,
        ),
    ]
