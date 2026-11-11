from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [("customer", "Customer"), ("owner", "Business owner"), ("staff", "Staff"), ("admin", "Platform admin")]
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="customer")
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=128, blank=True)
    password_reset_token = models.CharField(max_length=128, blank=True)
    password_reset_expires = models.DateTimeField(null=True, blank=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

class Business(models.Model):
    STATUS_CHOICES = [("pending", "Pending"), ("approved", "Approved"), ("suspended", "Suspended")]
    name = models.CharField(max_length=160)
    location = models.CharField(max_length=160, default="Kampala")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="businesses")
    plan = models.CharField(max_length=40, default="trial")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    is_paused = models.BooleanField(default=False)
    opening_time = models.TimeField(default="08:00")
    closing_time = models.TimeField(default="18:00")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    @property
    def accepting_tickets(self):
        return self.status == "approved" and self.is_active and not self.is_paused

class StaffAssignment(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="staff_assignments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="staff_assignments")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("business", "user")

class Service(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=80)
    average_minutes = models.PositiveIntegerField(default=5)
    prefix = models.CharField(max_length=2)
    is_active = models.BooleanField(default=True)

class Ticket(models.Model):
    STATUS_CHOICES = [("waiting", "Waiting"), ("called", "Called"), ("served", "Served"), ("skipped", "Skipped"), ("left", "Left")]
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="tickets")
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name="tickets")
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="tickets")
    name = models.CharField(max_length=160)
    phone = models.CharField(max_length=30)
    channel = models.CharField(max_length=20, default="SMS")
    number = models.CharField(max_length=20)
    sequence = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="waiting")
    joined_at = models.DateTimeField(auto_now_add=True)
    called_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["joined_at"]

class Notification(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="notifications")
    channel = models.CharField(max_length=20)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered = models.BooleanField(default=False)

class Subscription(models.Model):
    PLAN_CHOICES = [("trial", "Trial"), ("monthly", "Monthly")]
    business = models.OneToOneField(Business, on_delete=models.CASCADE, related_name="subscription")
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default="trial")
    setup_fee_ugx = models.PositiveIntegerField(default=15000)
    monthly_fee_ugx = models.PositiveIntegerField(default=10000)
    status = models.CharField(max_length=20, default="trial")
    started_at = models.DateTimeField(auto_now_add=True)
    next_billing_at = models.DateTimeField(null=True, blank=True)

class Payment(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="payments")
    amount_ugx = models.PositiveIntegerField()
    kind = models.CharField(max_length=20, choices=[("setup", "Setup"), ("monthly", "Monthly")])
    status = models.CharField(max_length=20, default="pending")
    provider_reference = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
