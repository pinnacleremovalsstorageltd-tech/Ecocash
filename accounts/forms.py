from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from phonenumber_field.formfields import PhoneNumberField

from .models import User, PartnerProfile, Document

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': _('Enter your username or email'),
            'autofocus': True,
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': _('Enter your password'),
            'autocomplete': 'current-password'
        })
    )
    remember_me = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'custom-checkbox'}))

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def clean(self):
        return self.cleaned_data

    def get_user(self):
        return None

class UserRegistrationForm(UserCreationForm):
    company_name = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('Enter your company name')}), error_messages={'required': _('Company name is required')})
    business_registration_number = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('Enter business registration number')}), error_messages={'required': _('Business registration number is required')})
    business_type = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('Business type')}), error_messages={'required': _('Business type is required')})
    contact_number = PhoneNumberField(required=True, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('Enter your contact number')}), error_messages={'required': _('Contact number is required'), 'invalid': _('Please enter a valid phone number')})
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': _('info@yourcompany.com')}), error_messages={'required': _('Email address is required'), 'invalid': _('Please enter a valid email address')})
    position = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('CEO, Manager, etc.')}), error_messages={'required': _('Position is required')})
    mobile_number = PhoneNumberField(required=False, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('Enter your mobile number')}), error_messages={'invalid': _('Please enter a valid phone number')})
    alternative_email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': _('personal@email.com')}), error_messages={'invalid': _('Please enter a valid email address')})
    security_question = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={'class': 'form-input'}), error_messages={'required': _('Security question is required')})
    security_answer = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('Enter your security answer')}), error_messages={'required': _('Security answer is required')})
    terms = forms.BooleanField(required=True, widget=forms.CheckboxInput(attrs={'class': 'custom-checkbox'}), error_messages={'required': _('You must agree to the terms and conditions')})

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'company_name',
            'business_registration_number', 'business_type', 'phone_number',
            'security_question', 'security_answer', 'terms', 'password1', 'password2'
        ]

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError(_('This username is already taken.'))
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(_('This email address is already registered.'))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.user_type = 'partner'
        user.account_status = 'pending'
        user.company_name = self.cleaned_data['company_name']
        user.business_registration_number = self.cleaned_data['business_registration_number']
        user.business_type = self.cleaned_data['business_type']
        user.phone_number = self.cleaned_data['contact_number']
        user.security_question = self.cleaned_data['security_question']
        user.security_answer = self.cleaned_data['security_answer']
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'date_of_birth', 'gender', 'company_name', 'business_type', 'industry', 'years_in_business', 'employee_count']

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.exclude(pk=self.instance.pk).filter(email__iexact=email).exists():
            raise ValidationError(_('This email address is already taken.'))
        return email

class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['language', 'timezone', 'notification_preferences']

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['document_type', 'file']

    def clean_file(self):
        file = self.cleaned_data['file']
        if file.size > 10 * 1024 * 1024:
            raise ValidationError(_('File size must be less than 10MB.'))
        allowed_types = [
            'application/pdf',
            'image/jpeg',
            'image/png',
            'image/gif',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ]
        if file.content_type not in allowed_types:
            raise ValidationError(_('File type not supported. Please upload PDF, JPG, PNG, or DOC.'))
        return file

class UserFilterForm(forms.Form):
    search = forms.CharField(required=False)
    user_type = forms.ChoiceField(choices=[('', 'All Types')] + list(User.USER_TYPES), required=False)
    account_status = forms.ChoiceField(choices=[('', 'All Status')] + list(User.ACCOUNT_STATUS), required=False)
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    sort_by = forms.ChoiceField(choices=[('-date_joined', 'Newest'), ('date_joined', 'Oldest'), ('username', 'Username A-Z'), ('-username', 'Username Z-A')], required=False)

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        if date_from and date_to and date_from > date_to:
            raise ValidationError(_('Start date must be before end date.'))
        return cleaned_data
