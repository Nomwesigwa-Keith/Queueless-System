from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import Business, Service, Ticket, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "role", "email_verified"]

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ["id", "name", "location", "plan", "status", "is_paused", "opening_time", "closing_time", "is_active", "accepting_tickets"]
        read_only_fields = ["status", "accepting_tickets"]

class BusinessDirectorySerializer(serializers.ModelSerializer):
    services = serializers.SerializerMethodField()
    waiting_count = serializers.SerializerMethodField()

    class Meta:
        model = Business
        fields = ["id", "name", "location", "opening_time", "closing_time", "is_paused", "accepting_tickets", "waiting_count", "services"]

    def get_services(self, obj):
        return [{"id": service.id, "name": service.name, "average_minutes": service.average_minutes} for service in obj.services.filter(is_active=True)]

    def get_waiting_count(self, obj):
        return obj.tickets.filter(status__in=["waiting", "called"]).count()

class BusinessRegistrationSerializer(serializers.Serializer):
    business_name = serializers.CharField(max_length=160)
    location = serializers.CharField(max_length=160)
    owner_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirmation = serializers.CharField(write_only=True)
    services = serializers.ListField(child=serializers.CharField(max_length=80), min_length=1)

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirmation"]:
            raise serializers.ValidationError({"password_confirmation": "Passwords do not match."})
        if User.objects.filter(email__iexact=attrs["email"]).exists():
            raise serializers.ValidationError({"email": "An account with this email already exists."})
        return attrs

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    def validate(self, attrs):
        user = authenticate(email=attrs["email"], password=attrs["password"])
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        attrs["user"] = user
        return attrs

class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirmation = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirmation"]:
            raise serializers.ValidationError({"password_confirmation": "Passwords do not match."})
        if User.objects.filter(email__iexact=attrs["email"]).exists():
            raise serializers.ValidationError({"email": "An account with this email already exists."})
        return attrs

class TicketSerializer(serializers.ModelSerializer):
    service = serializers.CharField(source="service.name", read_only=True)
    business = serializers.CharField(source="business.name", read_only=True)
    people_ahead = serializers.SerializerMethodField()
    estimated_wait_minutes = serializers.SerializerMethodField()
    class Meta:
        model = Ticket
        fields = ["id", "number", "name", "phone", "business", "service", "channel", "status", "joined_at", "called_at", "completed_at", "cancelled_at", "people_ahead", "estimated_wait_minutes"]
        read_only_fields = ["number", "status", "joined_at", "people_ahead", "estimated_wait_minutes"]
    def get_people_ahead(self, obj):
        return Ticket.objects.filter(service=obj.service, status="waiting", joined_at__lt=obj.joined_at).count()
    def get_estimated_wait_minutes(self, obj):
        return self.get_people_ahead(obj) * obj.service.average_minutes

class TicketCreateSerializer(serializers.Serializer):
    business_id = serializers.IntegerField(min_value=1)
    name = serializers.CharField(max_length=160)
    phone = serializers.CharField(max_length=30)
    service = serializers.CharField()
    channel = serializers.ChoiceField(choices=["SMS", "WhatsApp"])
