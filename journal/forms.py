from django import forms
from django.contrib.auth.models import User

from .models import Article, Author


class RegistrationForm(forms.Form):
    """Extended registration with author info collected upfront."""

    # Auth fields
    username = forms.CharField(
        max_length=150, widget=forms.TextInput(attrs={'class': 'form-input'}),
        label='Foydalanuvchi nomi *',
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        label='Parol *',
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        label='Parol (qayta) *',
    )

    # Author fields
    full_name = forms.CharField(
        max_length=255, widget=forms.TextInput(attrs={'class': 'form-input'}),
        label='F.I.O. *',
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-input'}),
        label='Email *',
    )
    academic_degree = forms.CharField(
        max_length=100, required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 't.f.n., t.f.d., dotsent...'}),
        label='Ilmiy daraja',
    )
    affiliation = forms.CharField(
        max_length=300, widget=forms.TextInput(attrs={'class': 'form-input'}),
        label='Ish joyi / Afiliatsiya *',
    )
    orcid_id = forms.CharField(
        max_length=25, required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '0000-0000-0000-0000'}),
        label='ORCID iD',
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Bu foydalanuvchi nomi band.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Bu email allaqachon roʻyxatdan oʻtgan.')
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Parollar mos kelmadi.')
        if p1 and len(p1) < 8:
            raise forms.ValidationError('Parol kamida 8 ta belgidan iborat boʻlishi kerak.')
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
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'saraton, immunoterapiya, kimyoterapiya...'}),
        label='Kalit so\u02bblar (vergul bilan ajrating)',
    )
    issue_text = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Masalan: Vol. 5, No. 2, 2025'}),
        label='Jurnal soni (ixtiyoriy)',
        help_text='Mavjud sondan tanlang yoki o\u02bbzingiz yozing. Format: Vol. X, No. Y, YYYY',
    )

    class Meta:
        model = Article
        fields = [
            'title_uz', 'title_ru', 'title_en',
            'abstract_uz', 'abstract_ru', 'abstract_en',
            'article_type', 'category',
            'doi', 'thumbnail_image', 'pdf_file',
        ]
        widgets = {
            'title_uz': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Sarlavha (uz)'}),
            'title_ru': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Sarlavha (ru)'}),
            'title_en': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Sarlavha (en)'}),
            'abstract_uz': forms.Textarea(attrs={'class': 'form-input', 'rows': 5, 'placeholder': 'Annotatsiya (uz)'}),
            'abstract_ru': forms.Textarea(attrs={'class': 'form-input', 'rows': 5, 'placeholder': 'Annotatsiya (ru)'}),
            'abstract_en': forms.Textarea(attrs={'class': 'form-input', 'rows': 5, 'placeholder': 'Annotatsiya (en)'}),
            'article_type': forms.Select(attrs={'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'doi': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '10.1234/oncoscience.2025.01.005'}),
            'thumbnail_image': forms.FileInput(attrs={'class': 'form-input', 'accept': 'image/*'}),
            'pdf_file': forms.FileInput(attrs={'class': 'form-input', 'accept': '.pdf,.doc,.docx'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title_uz'].label = 'Sarlavha (uz) *'
        self.fields['title_ru'].label = 'Sarlavha (ru)'
        self.fields['title_en'].label = 'Sarlavha (en)'
        self.fields['abstract_uz'].label = 'Annotatsiya (uz) *'
        self.fields['abstract_ru'].label = 'Annotatsiya (ru)'
        self.fields['abstract_en'].label = 'Annotatsiya (en)'
        self.fields['article_type'].label = 'Maqola turi *'
        self.fields['category'].label = 'Yoʻnalish *'
        self.fields['doi'].label = 'DOI (ixtiyoriy)'
        self.fields['doi'].help_text = 'Masalan: 10.1234/oncoscience.2025.01.005 — tahririyat beradi, boʻlmasa boʻsh qoldiring'
        self.fields['thumbnail_image'].label = 'Kichik rasm (ixtiyoriy)'
        self.fields['pdf_file'].label = 'PDF fayl *'
        self.fields['doi'].required = False
        self.fields['thumbnail_image'].required = False

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('title_uz'):
            raise forms.ValidationError('Oʻzbek tilidagi sarlavha majburiy.')
        if not cleaned.get('pdf_file'):
            raise forms.ValidationError('PDF fayl yuklash majburiy.')
        return cleaned
