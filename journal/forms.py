import bleach
import re
from django import forms
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from tinymce.widgets import TinyMCE

from .models import Article, ArticleFigure, ArticleSupplementaryFile, Author, Reference, Issue, Keyword, Review


class RegistrationForm(forms.Form):
    """Extended registration with author info collected upfront."""

    # Auth fields
    username = forms.CharField(
        max_length=150, widget=forms.TextInput(attrs={'class': 'form-input'}),
        label=_('Foydalanuvchi nomi *'),
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        label=_('Parol *'),
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        label=_('Parol (qayta) *'),
    )

    # Author fields
    full_name = forms.CharField(
        max_length=255, widget=forms.TextInput(attrs={'class': 'form-input'}),
        label=_('F.I.O. *'),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-input'}),
        label=_('Email *'),
    )
    academic_degree = forms.CharField(
        max_length=100, required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('t.f.n., t.f.d., dotsent...')}),
        label=_('Ilmiy daraja'),
    )
    affiliation = forms.CharField(
        max_length=300, widget=forms.TextInput(attrs={'class': 'form-input'}),
        label=_('Ish joyi / Afiliatsiya *'),
    )
    orcid_id = forms.CharField(
        max_length=25, required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('0000-0000-0000-0000')}),
        label=_('ORCID iD'),
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(_('Bu foydalanuvchi nomi band.'))
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('Bu email allaqachon roʻyxatdan oʻtgan.'))
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2:
            if p1 != p2:
                raise forms.ValidationError(_('Parollar mos kelmadi.'))
            try:
                validate_password(p1)
            except ValidationError as e:
                self.add_error('password1', e)
        return cleaned

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password1'],
        )
        Author.objects.create(
            user=user,
            full_name=data['full_name'],
            email=data['email'],
            academic_degree=data.get('academic_degree', ''),
            affiliation_uz=data['affiliation'],
            orcid_id=data.get('orcid_id', ''),
        )
        return user


class ArticleSubmissionForm(forms.ModelForm):
    agree_to_terms = forms.BooleanField(
        required=True,
        label=_("Men ushbu maqolani jurnal qoidalariga asosan yuboryapman va unda plagiat (ko'chirmachilik) yo'qligini tasdiqlayman.")
    )
    
    class Meta:
        model = Article
        fields = ['article_type', 'category', 'title_uz', 'abstract_uz', 'pdf_file']
        widgets = {
            'article_type': forms.Select(attrs={'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'title_uz': forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('Maqolaning to\'liq sarlavhasi')}),
            'abstract_uz': forms.Textarea(attrs={'class': 'form-input', 'rows': 5, 'placeholder': _('Maqola annotatsiyasi (qisqacha mazmuni)...')}),
            'pdf_file': forms.FileInput(attrs={'class': 'form-input', 'accept': '.pdf,.doc,.docx'}),
        }
        labels = {
            'article_type': _('Maqola turi'),
            'category': _('Yo\'nalish'),
            'title_uz': _('Sarlavha'),
            'abstract_uz': _('Annotatsiya (Qisqacha mazmun)'),
            'pdf_file': _('Maqola fayli (PDF yoki Word)'),
        }
