from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [("queue_api", "0001_initial")]
    operations = [
        migrations.AddField(model_name="user", name="email_verified", field=models.BooleanField(default=False)),
        migrations.AddField(model_name="user", name="email_verification_token", field=models.CharField(blank=True, max_length=128)),
        migrations.AddField(model_name="user", name="password_reset_token", field=models.CharField(blank=True, max_length=128)),
        migrations.AddField(model_name="user", name="password_reset_expires", field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name="business", name="status", field=models.CharField(choices=[("pending", "Pending"), ("approved", "Approved"), ("suspended", "Suspended")], default="pending", max_length=20)),
        migrations.AddField(model_name="business", name="is_paused", field=models.BooleanField(default=False)),
        migrations.AddField(model_name="business", name="opening_time", field=models.TimeField(default="08:00")),
        migrations.AddField(model_name="business", name="closing_time", field=models.TimeField(default="18:00")),
        migrations.AddField(model_name="business", name="updated_at", field=models.DateTimeField(auto_now=True)),
        migrations.AddField(model_name="ticket", name="cancelled_at", field=models.DateTimeField(blank=True, null=True)),
        migrations.CreateModel(name="StaffAssignment", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("is_active", models.BooleanField(default=True)), ("created_at", models.DateTimeField(auto_now_add=True)),
            ("business", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="staff_assignments", to="queue_api.business")),
            ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="staff_assignments", to=settings.AUTH_USER_MODEL)),
        ], options={"unique_together": {("business", "user")}}),
        migrations.CreateModel(name="Notification", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("channel", models.CharField(max_length=20)), ("message", models.TextField()),
            ("sent_at", models.DateTimeField(auto_now_add=True)), ("delivered", models.BooleanField(default=False)),
            ("ticket", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notifications", to="queue_api.ticket")),
        ]),
        migrations.CreateModel(name="Subscription", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("plan", models.CharField(choices=[("trial", "Trial"), ("monthly", "Monthly")], default="trial", max_length=20)),
            ("setup_fee_ugx", models.PositiveIntegerField(default=15000)), ("monthly_fee_ugx", models.PositiveIntegerField(default=10000)),
            ("status", models.CharField(default="trial", max_length=20)), ("started_at", models.DateTimeField(auto_now_add=True)),
            ("next_billing_at", models.DateTimeField(blank=True, null=True)),
            ("business", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="subscription", to="queue_api.business")),
        ]),
        migrations.CreateModel(name="Payment", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("amount_ugx", models.PositiveIntegerField()), ("kind", models.CharField(choices=[("setup", "Setup"), ("monthly", "Monthly")], max_length=20)),
            ("status", models.CharField(default="pending", max_length=20)), ("provider_reference", models.CharField(blank=True, max_length=120)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("subscription", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="payments", to="queue_api.subscription")),
        ]),
    ]
