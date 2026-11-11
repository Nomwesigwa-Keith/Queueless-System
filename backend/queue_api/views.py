from django.db import transaction
from django.db.models import Max
from django.contrib.auth import authenticate
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from datetime import timedelta
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Business, Notification, Payment, Service, StaffAssignment, Subscription, Ticket, User
from .serializers import BusinessDirectorySerializer, BusinessRegistrationSerializer, BusinessSerializer, RegisterSerializer, TicketCreateSerializer, TicketSerializer, UserSerializer

def business_for(user):
    return Business.objects.filter(owner=user).first() or Business.objects.filter(staff_assignments__user=user, staff_assignments__is_active=True).first() or Business.objects.filter(status="approved", is_active=True).first()

def role_required(user, roles):
    return user.role in roles

class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        user = authenticate(email=request.data.get("email"), password=request.data.get("password"))
        if not user:
            return Response({"detail": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data,
        })

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.create_user(
            username=serializer.validated_data["email"],
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            first_name=serializer.validated_data["name"],
            role="customer",
        )
        user.email_verification_token = get_random_string(48)
        user.save(update_fields=["email_verification_token"])
        send_mail("Verify your QueueLess email", f"Use this verification token: {user.email_verification_token}", None, [user.email], fail_silently=True)
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)

class EmailVerifyView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        user = User.objects.filter(email_verification_token=request.data.get("token")).first()
        if not user:
            return Response({"detail": "Invalid verification token."}, status=400)
        user.email_verified = True
        user.email_verification_token = ""
        user.save(update_fields=["email_verified", "email_verification_token"])
        return Response({"detail": "Email verified successfully."})

class BusinessRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def post(self, request):
        data = BusinessRegistrationSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        values = data.validated_data
        owner = User.objects.create_user(username=values["email"], email=values["email"], password=values["password"], first_name=values["owner_name"], role="owner")
        owner.email_verification_token = get_random_string(48)
        owner.save(update_fields=["email_verification_token"])
        send_mail("Verify your QueueLess business email", f"Use this verification token: {owner.email_verification_token}", None, [owner.email], fail_silently=True)
        business = Business.objects.create(owner=owner, name=values["business_name"], location=values["location"], status="pending")
        for index, name in enumerate(values["services"]):
            Service.objects.create(business=business, name=name, prefix=chr(65 + index))
        subscription = Subscription.objects.create(business=business)
        Payment.objects.create(subscription=subscription, amount_ugx=15000, kind="setup")
        refresh = RefreshToken.for_user(owner)
        return Response({"business": BusinessSerializer(business).data, "access": str(refresh.access_token), "refresh": str(refresh), "user": UserSerializer(owner).data}, status=201)

class BusinessDirectoryView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = BusinessDirectorySerializer

    def get_queryset(self):
        queryset = Business.objects.filter(status="approved", is_active=True).prefetch_related("services")
        query = self.request.query_params.get("q", "").strip()
        location = self.request.query_params.get("location", "").strip()
        if query:
            queryset = queryset.filter(name__icontains=query)
        if location:
            queryset = queryset.filter(location__icontains=location)
        return queryset.order_by("name")

class PasswordChangeView(APIView):
    def post(self, request):
        old = request.data.get("current_password")
        new = request.data.get("new_password", "")
        if not old or len(new) < 8 or not authenticate(email=request.user.email, password=old):
            return Response({"detail": "Current password is incorrect or the new password is too short."}, status=400)
        request.user.set_password(new)
        request.user.save(update_fields=["password"])
        return Response({"detail": "Password changed successfully."})

class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        user = User.objects.filter(email__iexact=request.data.get("email", "")).first()
        if user:
            user.password_reset_token = get_random_string(48)
            user.password_reset_expires = timezone.now() + timedelta(hours=1)
            user.save(update_fields=["password_reset_token", "password_reset_expires"])
        return Response({"detail": "If that email exists, reset instructions have been created.", "demo_token": user.password_reset_token if user else None})

class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        user = User.objects.filter(password_reset_token=request.data.get("token"), password_reset_expires__gt=timezone.now()).first()
        if not user or len(request.data.get("new_password", "")) < 8:
            return Response({"detail": "The reset token is invalid or expired."}, status=400)
        user.set_password(request.data["new_password"])
        user.password_reset_token = ""
        user.password_reset_expires = None
        user.save(update_fields=["password", "password_reset_token", "password_reset_expires"])
        return Response({"detail": "Password reset successfully."})

class TicketListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        query = Ticket.objects.select_related("service", "business")
        service = self.request.query_params.get("service")
        if self.request.user.role == "customer":
            query = query.filter(customer=self.request.user)
        else:
            query = query.filter(business=business_for(self.request.user))
        return query.filter(service__name=service) if service else query
    def get_serializer_class(self):
        return TicketCreateSerializer if self.request.method == "POST" else TicketSerializer
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        data = TicketCreateSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        business = Business.objects.filter(
            id=data.validated_data["business_id"],
            status="approved",
            is_active=True,
        ).first()
        current_time = timezone.localtime().time()
        if not business or not business.accepting_tickets or not (business.opening_time <= current_time <= business.closing_time):
            return Response({"detail": "This business is not currently accepting tickets."}, status=400)
        service = business.services.filter(name=data.validated_data["service"], is_active=True).first()
        if not service:
            return Response({"detail": "Service not found."}, status=status.HTTP_400_BAD_REQUEST)
        latest = Ticket.objects.filter(business=business, service=service).aggregate(max_sequence=Max("sequence"))["max_sequence"] or 0
        values = data.validated_data.copy()
        values.pop("service")
        values.pop("business_id")
        ticket = Ticket.objects.create(business=business, service=service, customer=request.user, sequence=latest + 1, number=f"{service.prefix}-{latest + 1}", **values)
        Notification.objects.create(ticket=ticket, channel=ticket.channel, message=f"{ticket.number} created.")
        return Response(TicketSerializer(ticket).data, status=status.HTTP_201_CREATED)

class TicketDetailView(generics.RetrieveAPIView):
    serializer_class = TicketSerializer
    def get_queryset(self):
        return Ticket.objects.filter(customer=self.request.user)

class TicketStatusView(APIView):
    def post(self, request, pk):
        if request.user.role not in ["staff", "owner", "admin"]:
            return Response({"detail": "Staff access required."}, status=403)
        ticket = Ticket.objects.filter(pk=pk, business=business_for(request.user)).first()
        if not ticket:
            return Response({"detail": "Ticket not found for this business."}, status=404)
        new_status = request.data.get("status")
        if new_status not in dict(Ticket.STATUS_CHOICES):
            return Response({"detail": "Invalid ticket status."}, status=400)
        ticket.status = new_status
        if new_status == "called": ticket.called_at = timezone.now()
        if new_status in ["served", "skipped", "left"]: ticket.completed_at = timezone.now()
        ticket.save(update_fields=["status", "called_at", "completed_at"])
        return Response(TicketSerializer(ticket).data)

class TicketCancelView(APIView):
    def post(self, request, pk):
        ticket = Ticket.objects.filter(pk=pk, customer=request.user).first()
        if not ticket or ticket.status not in ["waiting", "called"]:
            return Response({"detail": "Ticket cannot be cancelled."}, status=400)
        ticket.status = "left"
        ticket.cancelled_at = timezone.now()
        ticket.completed_at = timezone.now()
        ticket.save(update_fields=["status", "cancelled_at", "completed_at"])
        return Response(TicketSerializer(ticket).data)

class BusinessView(APIView):
    def get(self, request):
        business = business_for(request.user)
        return Response(BusinessSerializer(business).data) if business else Response({"detail": "Business not found."}, status=404)
    def patch(self, request):
        if not role_required(request.user, ["owner", "admin"]):
            return Response({"detail": "Owner access required."}, status=403)
        business = business_for(request.user)
        serializer = BusinessSerializer(business, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class BusinessPauseView(APIView):
    def post(self, request):
        if not role_required(request.user, ["owner", "staff", "admin"]):
            return Response({"detail": "Staff access required."}, status=403)
        business = business_for(request.user)
        business.is_paused = bool(request.data.get("paused", True))
        business.save(update_fields=["is_paused", "updated_at"])
        return Response(BusinessSerializer(business).data)

class BusinessStaffView(APIView):
    def get(self, request):
        business = business_for(request.user)
        return Response(UserSerializer(User.objects.filter(staff_assignments__business=business, staff_assignments__is_active=True), many=True).data)
    def post(self, request):
        if request.user.role not in ["owner", "admin"]:
            return Response({"detail": "Owner access required."}, status=403)
        business = business_for(request.user)
        staff = User.objects.filter(email__iexact=request.data.get("email"), role="staff").first()
        if not staff:
            return Response({"detail": "A staff account with that email was not found."}, status=404)
        StaffAssignment.objects.update_or_create(business=business, user=staff, defaults={"is_active": True})
        return Response(UserSerializer(staff).data, status=201)

class AdminBusinessStatusView(APIView):
    def post(self, request, pk):
        if request.user.role != "admin":
            return Response({"detail": "Admin access required."}, status=403)
        business = Business.objects.get(pk=pk)
        new_status = request.data.get("status")
        if new_status not in dict(Business.STATUS_CHOICES):
            return Response({"detail": "Invalid business status."}, status=400)
        business.status = new_status
        business.is_active = business.status != "suspended"
        business.save(update_fields=["status", "is_active", "updated_at"])
        return Response(BusinessSerializer(business).data)

class BusinessStatsView(APIView):
    def get(self, request):
        business = business_for(request.user)
        qs = Ticket.objects.filter(business=business)
        subscription = getattr(business, "subscription", None)
        return Response({
            "served": qs.filter(status="served").count(),
            "waiting": qs.filter(status="waiting").count(),
            "skipped": qs.filter(status="skipped").count(),
            "total": qs.count(),
            "by_service": [{"service": s.name, "total": qs.filter(service=s).count()} for s in business.services.all()],
            "subscription": {
                "plan": subscription.plan if subscription else business.plan,
                "status": subscription.status if subscription else "unconfigured",
                "setup_fee_ugx": subscription.setup_fee_ugx if subscription else 15000,
                "monthly_fee_ugx": subscription.monthly_fee_ugx if subscription else 10000,
                "payments": subscription.payments.count() if subscription else 0,
            },
        })

class BusinessListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BusinessSerializer
    queryset = Business.objects.all()

    def get_queryset(self):
        if self.request.user.role != "admin":
            return Business.objects.none()
        return super().get_queryset()
