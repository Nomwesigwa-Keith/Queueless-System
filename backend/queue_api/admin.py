from django.contrib import admin
from .models import Business, Notification, Payment, Service, StaffAssignment, Subscription, Ticket, User

admin.site.register(User)
admin.site.register(Business)
admin.site.register(Service)
admin.site.register(Ticket)
admin.site.register(StaffAssignment)
admin.site.register(Notification)
admin.site.register(Subscription)
admin.site.register(Payment)
