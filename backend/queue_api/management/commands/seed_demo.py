from django.core.management.base import BaseCommand
from queue_api.models import Business, Service, StaffAssignment, Subscription, User

class Command(BaseCommand):
    help = "Create the QueueLess demo users, business, and services."

    def handle(self, *args, **options):
        accounts = [
            ("customer@queueless.demo", "customer123", "customer", "Demo Customer"),
            ("staff@queueless.demo", "staff123", "staff", "Amina Staff"),
            ("admin@queueless.demo", "admin123", "admin", "QueueLess Admin"),
        ]
        users = {}
        for email, password, role, name in accounts:
            user, created = User.objects.get_or_create(email=email, defaults={"username": email, "role": role, "first_name": name})
            user.role = role
            user.set_password(password)
            user.save()
            users[role] = user
            self.stdout.write(f"{'Created' if created else 'Updated'} {email}")
        business = Business.objects.filter(name="Amina's Hair Salon").first()
        if business:
            business.name = "Amara Salon"
            business.save(update_fields=["name"])
        else:
            business, _ = Business.objects.get_or_create(name="Amara Salon", defaults={"owner": users["admin"], "location": "Kampala", "status": "approved"})
        business.status = "approved"
        business.is_active = True
        business.save(update_fields=["status", "is_active"])
        for name, prefix in [("Haircut", "A"), ("Braids", "B"), ("Manicure", "C")]:
            Service.objects.get_or_create(business=business, name=name, defaults={"prefix": prefix, "average_minutes": 5})
        StaffAssignment.objects.get_or_create(business=business, user=users["staff"])
        Subscription.objects.get_or_create(business=business)
        self.stdout.write(self.style.SUCCESS("QueueLess demo data is ready."))
