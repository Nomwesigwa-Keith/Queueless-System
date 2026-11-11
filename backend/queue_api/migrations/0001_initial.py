from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]
    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("is_superuser", models.BooleanField(default=False, help_text="Designates that this user has all permissions without explicitly assigning them.", verbose_name="superuser status")),
                ("username", models.CharField(max_length=150, unique=True)),
                ("first_name", models.CharField(blank=True, max_length=150)),
                ("last_name", models.CharField(blank=True, max_length=150)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("is_staff", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("date_joined", models.DateTimeField(auto_now_add=True)),
                ("role", models.CharField(choices=[("customer", "Customer"), ("staff", "Staff"), ("admin", "Platform admin")], default="customer", max_length=20)),
                ("groups", models.ManyToManyField(blank=True, related_name="queue_api_user_set", related_query_name="queue_api_user", to="auth.group")),
                ("user_permissions", models.ManyToManyField(blank=True, related_name="queue_api_user_set", related_query_name="queue_api_user", to="auth.permission")),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="Business",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=160)),
                ("location", models.CharField(default="Kampala", max_length=160)),
                ("plan", models.CharField(default="trial", max_length=40)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="businesses", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Service",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=80)),
                ("average_minutes", models.PositiveIntegerField(default=5)),
                ("prefix", models.CharField(max_length=2)),
                ("is_active", models.BooleanField(default=True)),
                ("business", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="services", to="queue_api.business")),
            ],
        ),
        migrations.CreateModel(
            name="Ticket",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=160)),
                ("phone", models.CharField(max_length=30)),
                ("channel", models.CharField(default="SMS", max_length=20)),
                ("number", models.CharField(max_length=20)),
                ("sequence", models.PositiveIntegerField()),
                ("status", models.CharField(choices=[("waiting", "Waiting"), ("called", "Called"), ("served", "Served"), ("skipped", "Skipped"), ("left", "Left")], default="waiting", max_length=20)),
                ("joined_at", models.DateTimeField(auto_now_add=True)),
                ("called_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("business", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="tickets", to="queue_api.business")),
                ("customer", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="tickets", to=settings.AUTH_USER_MODEL)),
                ("service", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="tickets", to="queue_api.service")),
            ],
            options={"ordering": ["joined_at"]},
        ),
    ]
