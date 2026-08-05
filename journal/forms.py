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
    """Form for registered users to submit a new article (draft)."""

    keywords_text = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('saraton, immunoterapiya, kimyoterapiya...')}),
        label=_('Kalit so\u02bblar (vergul bilan ajrating)'),
    )
    issue_text = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('Masalan: Vol. 5, No. 2, 2025')}),
        label=_('Jurnal soni (ixtiyoriy)'),
        help_text=_('Mavjud sondan tanlang yoki o\u02bbzingiz yozing. Format: Vol. X, No. Y, YYYY'),
    )
    co_authors = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': _('Har bir muallifni yangi qatorda yozing:\nAliyev Vali\nKarimova Saoda')}),
        label=_('Qo\u02bbshimcha mualliflar (ixtiyoriy)'),
        help_text=_('Har bir muallif F.I.O.sini yangi qatorda yozing. Siz avtomatik birinchi muallif bo\u02bblasiz.'),
    )

    class Meta:
        model = Article
        fields = [
            'title_uz', 'title_ru', 'title_en',
            'abstract_uz', 'abstract_ru', 'abstract_en',
            'full_text_uz', 'full_text_ru', 'full_text_en',
            'article_type', 'category',
            'funding_statement_uz', 'conflict_of_interest_uz', 'ethics_statement_uz',
            'doi', 'thumbnail_image', 'pdf_file',
        ]
        widgets = {
            'title_uz': forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('Sarlavha (uz)')}),
            'title_ru': forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('Sarlavha (ru)')}),
            'title_en': forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('Sarlavha (en)')}),
            'abstract_uz': forms.Textarea(attrs={'class': 'form-input', 'rows': 5, 'placeholder': _('Annotatsiya (uz)')}),
            'abstract_ru': forms.Textarea(attrs={'class': 'form-input', 'rows': 5, 'placeholder': _('Annotatsiya (ru)')}),
            'abstract_en': forms.Textarea(attrs={'class': 'form-input', 'rows': 5, 'placeholder': _('Annotatsiya (en)')}),
            'full_text_uz': TinyMCE(attrs={'class': 'form-input'}),
            'full_text_ru': TinyMCE(attrs={'class': 'form-input'}),
            'full_text_en': TinyMCE(attrs={'class': 'form-input'}),
            'article_type': forms.Select(attrs={'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'funding_statement_uz': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': _('Ushbu tadqiqot ... tomonidan moliyalashtirilgan.')}),
            'conflict_of_interest_uz': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': _('Mualliflar manfaatlar to\u02bbqnashuvi yo\u02bbqligini bildiradilar.')}),
            'ethics_statement_uz': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': _('Tadqiqot etika komissiyasi tomonidan tasdiqlangan.')}),
            'doi': forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('10.1234/oncoscience.2025.01.005')}),
            'thumbnail_image': forms.FileInput(attrs={'class': 'form-input', 'accept': 'image/*'}),
            'pdf_file': forms.FileInput(attrs={'class': 'form-input', 'accept': '.pdf,.doc,.docx'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title_uz'].label = str(_('Sarlavha (uz)')) + ' *'
        self.fields['title_ru'].label = str(_('Sarlavha (ru)'))
        self.fields['title_en'].label = str(_('Sarlavha (en)'))
        self.fields['abstract_uz'].label = str(_('Annotatsiya (uz)')) + ' *'
        self.fields['abstract_ru'].label = str(_('Annotatsiya (ru)'))
        self.fields['abstract_en'].label = str(_('Annotatsiya (en)'))
        self.fields['article_type'].label = str(_('Maqola turi')) + ' *'
        self.fields['category'].label = str(_('Yoʻnalish')) + ' *'
        self.fields['doi'].label = str(_('DOI (ixtiyoriy)'))
        self.fields['doi'].help_text = str(_('Masalan: 10.1234/oncoscience.2025.01.005 — tahririyat beradi, boʻlmasa boʻsh qoldiring'))
        self.fields['thumbnail_image'].label = str(_('Kichik rasm (ixtiyoriy)'))
        self.fields['pdf_file'].label = str(_('PDF fayl')) + ' *'
        self.fields['doi'].required = False
        self.fields['thumbnail_image'].required = False
        self.fields['full_text_uz'].label = str(_('Toʻliq matn (uz)'))
        self.fields['full_text_ru'].label = str(_('Toʻliq matn (ru)'))
        self.fields['full_text_en'].label = str(_('Toʻliq matn (en)'))
        self.fields['full_text_uz'].required = False
        self.fields['full_text_ru'].required = False
        self.fields['full_text_en'].required = False
        self.fields['funding_statement_uz'].label = str(_('Moliyalashtirish (ixtiyoriy)'))
        self.fields['conflict_of_interest_uz'].label = str(_('Manfaatlar to\u02bbqnashuvi (ixtiyoriy)'))
        self.fields['ethics_statement_uz'].label = str(_('Etika bayonoti (ixtiyoriy)'))
        for name in ('funding_statement_uz', 'conflict_of_interest_uz', 'ethics_statement_uz'):
            self.fields[name].required = False

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('title_uz'):
            raise forms.ValidationError(_('Oʻzbek tilidagi sarlavha majburiy.'))
        if not cleaned.get('pdf_file'):
            raise forms.ValidationError(_('PDF fayl yuklash majburiy.'))

        allowed_tags = list(bleach.ALLOWED_TAGS) + [
            'p', 'br', 'span', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'a', 'img', 'div'
        ]
        allowed_attrs = {
            '*': ['class', 'style'],
            'a': ['href', 'title', 'target'],
            'img': ['src', 'alt', 'width', 'height']
        }
        for lang in ['uz', 'ru', 'en']:
            field_name = f'full_text_{lang}'
            val = cleaned.get(field_name)
            if val:
                cleaned[field_name] = bleach.clean(
                    val,
                    tags=allowed_tags,
                    attributes=allowed_attrs
                )

        return cleaned

    def save_m2m_custom(self, article, user, is_edit=False):
        issue_text = (self.cleaned_data.get('issue_text') or '').strip()
        if issue_text:
            m = re.match(r'Vol\.?\s*(\d+).*?No\.?\s*(\d+).*?(\d{4})', issue_text, re.IGNORECASE)
            if m:
                vol, num, yr = int(m.group(1)), int(m.group(2)), int(m.group(3))
                issue_obj, _created = Issue.objects.get_or_create(volume=vol, number=num, year=yr)
                article.issue = issue_obj
                article.save(update_fields=['issue'])

        if is_edit:
            author = Author.objects.filter(user=user).first()
            article.authors.set([author] if author else [])
        else:
            author = Author.objects.filter(user=user).first()
            if author:
                article.authors.add(author)

        co_authors_text = self.cleaned_data.get('co_authors', '')
        for line in co_authors_text.split('\n'):
            name = line.strip()
            if name:
                safe_slug = slugify(name)[:280] or f'author-{hash(name) % 100000}'
                co_author, _created = Author.objects.get_or_create(
                    full_name=name,
                    defaults={'slug': safe_slug},
                )
                article.authors.add(co_author)

        if is_edit:
            article.keywords.clear()
        keywords_text = self.cleaned_data.get('keywords_text', '')
        for kw in keywords_text.split(','):
            kw = kw.strip()
            if kw:
                keyword_obj, _created = Keyword.objects.get_or_create(name=kw)
                article.keywords.add(keyword_obj)


class AuthorProfileForm(forms.ModelForm):
    """Form for users to edit their author profile."""

    class Meta:
        model = Author
        fields = [
            'full_name', 'academic_degree',
            'affiliation_uz', 'affiliation_ru', 'affiliation_en',
            'orcid_id', 'email', 'photo',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('F.I.O.')}),
            'academic_degree': forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('Masalan: t.f.d.')}),
            'affiliation_uz': forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('Ish joyi (uz)')}),
            'affiliation_ru': forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('Ish joyi (ru)')}),
            'affiliation_en': forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('Affiliation (en)')}),
            'orcid_id': forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('0000-0000-0000-0000')}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': _('email@example.com')}),
            'photo': forms.FileInput(attrs={'class': 'form-input', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['full_name'].label = str(_('F.I.O.')) + ' *'
        self.fields['academic_degree'].label = str(_('Ilmiy daraja'))
        self.fields['affiliation_uz'].label = str(_('Ish joyi/lavozimi (uz)'))
        self.fields['affiliation_ru'].label = str(_('Ish joyi/lavozimi (ru)'))
        self.fields['affiliation_en'].label = str(_('Ish joyi/lavozimi (en)'))
        self.fields['orcid_id'].label = str(_('ORCID iD'))
        self.fields['email'].label = str(_('Email'))
        self.fields['photo'].label = str(_('Rasm (ixtiyoriy)'))
        self.fields['photo'].required = False


class ReviewForm(forms.ModelForm):
    """Form for reviewers to submit their review."""
    class Meta:
        model = Review
        fields = ['decision', 'comments_for_author', 'comments_for_editor']
        widgets = {
            'decision': forms.Select(attrs={'class': 'form-input'}),
            'comments_for_author': forms.Textarea(attrs={'class': 'form-input', 'rows': 5, 'placeholder': _('Muallifga yoziladigan izohlar (qanday kamchiliklar bor, nimalarni to\u02bbg\u02bbrilash kerak)...')}),
            'comments_for_editor': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': _('Faqat tahririyat uchun maxfiy izohlar...')}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['decision'].label = str(_('Xulosa')) + ' *'
        self.fields['comments_for_author'].label = str(_('Muallif uchun izohlar (Majburiy emas)'))
        self.fields['comments_for_author'].required = False
        self.fields['comments_for_editor'].label = str(_('Muharrir uchun xufyona izohlar (Majburiy emas)'))
        self.fields['comments_for_editor'].required = False


# ---------------------------------------------------------------------------
# Inline formsets — author-submitted references, figures, supplementary files
# ---------------------------------------------------------------------------

ReferenceFormSet = inlineformset_factory(
    Article,
    Reference,
    fields=('order', 'citation_text', 'doi_or_url'),
    widgets={
        'order': forms.NumberInput(attrs={'class': 'form-input form-input-sm', 'min': 0}),
        'citation_text': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': _('Muallif(lar), sarlavha, jurnal, yil, sahifalar.')}),
        'doi_or_url': forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('DOI yoki havola (ixtiyoriy)')}),
    },
    extra=1,
    can_delete=True,
)

ArticleFigureFormSet = inlineformset_factory(
    Article,
    ArticleFigure,
    fields=('order', 'image', 'caption_uz'),
    widgets={
        'order': forms.NumberInput(attrs={'class': 'form-input form-input-sm', 'min': 0}),
        'image': forms.FileInput(attrs={'class': 'form-input', 'accept': 'image/*'}),
        'caption_uz': forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('Tagyozuv (ixtiyoriy)')}),
    },
    extra=1,
    can_delete=True,
)

ArticleSupplementaryFileFormSet = inlineformset_factory(
    Article,
    ArticleSupplementaryFile,
    fields=('order', 'file', 'title_uz'),
    widgets={
        'order': forms.NumberInput(attrs={'class': 'form-input form-input-sm', 'min': 0}),
        'file': forms.FileInput(attrs={'class': 'form-input'}),
        'title_uz': forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('Fayl nomi')}),
    },
    extra=1,
    can_delete=True,
)
