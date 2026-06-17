from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_created')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_updated')
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()

class Address(BaseModel):
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100)
    is_business = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.address_line1}, {self.city}, {self.country}"

class Document(BaseModel):
    DOCUMENT_TYPES = [
        ('id', 'ID Document'),
        ('proof_of_address', 'Proof of Address'),
        ('business_reg', 'Business Registration'),
        ('tax_clearance', 'Tax Clearance'),
        ('bank_statement', 'Bank Statement'),
        ('profile_picture', 'Profile Picture'),
        ('other', 'Other')
    ]

    DOCUMENT_STATUS = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    document_number = models.CharField(max_length=100, blank=True, null=True)
    file = models.FileField(upload_to='documents/%Y/%m/%d/')
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    mime_type = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=DOCUMENT_STATUS, default='pending')
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_documents')
    expires_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_document_type_display()}"

    def verify(self, user):
        self.status = 'verified'
        self.verified_at = timezone.now()
        self.verified_by = user
        self.save()

    def reject(self, user, reason):
        self.status = 'rejected'
        self.notes = reason
        self.save()
