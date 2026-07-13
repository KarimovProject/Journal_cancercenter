from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _


def translated(instance, base):
    """Return the value of ``base`` for the active language.

    Fields are stored as ``<base>_uz``, ``<base>_ru``, ``<base>_en``.
    Falls back to Uzbek, then to any non-empty value.
    """
    lang = (get_language() or 'uz')[:2]
    order = [lang, 'uz', 'ru', 'en']
    for code in order:
        value = getattr(instance, f'{base}_{code}', None)
        if value:
            return value
    return ''


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(_('Yaratilgan'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Yangilangan'), auto_now=True)

    class Meta:
        abstract = True


class Category(models.Model):
    """Ilmiy yo'nalish (masalan: Onkojarrohlik, Radioterapiya)."""

    name_uz = models.CharField(_('Nomi (uz)'), max_length=200)
    name_ru = models.CharField(_('Nomi (ru)'), max_length=200, blank=True)
    name_en = models.CharField(_('Nomi (en)'), max_length=200, blank=True)
    slug = models.SlugField(_('Slug'), max_length=220, unique=True, blank=True)
    description_uz = models.TextField(_('Tavsif (uz)'), blank=True)
    description_ru = models.TextField(_('Tavsif (ru)'), blank=True)
    description_en = models.TextField(_('Tavsif (en)'), blank=True)
    order = models.PositiveIntegerField(_('Tartib'), default=0)

    class Meta:
        verbose_name = _('Ilmiy yo\'nalish')
        verbose_name_plural = _('Ilmiy yo\'nalishlar')
        ordering = ['order', 'name_uz']

    def __str__(self):
        return self.name_uz

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en or self.name_uz)
        super().save(*args, **kwargs)

    @property
    def name(self):
        return translated(self, 'name')

    @property
    def description(self):
        return translated(self, 'description')

    def get_absolute_url(self):
        return f"{reverse('journal:article_list')}?category={self.slug}"


class Author(models.Model):
    """Muallif. Asosiy sayt bazasiga bog'lanmaydi — mustaqil saqlanadi."""

    user = models.OneToOneField(
        'auth.User', related_name='author_profile',
        on_delete=models.CASCADE, null=True, blank=True,
        verbose_name=_('Foydalanuvchi'),
    )
    full_name = models.CharField(_('F.I.O.'), max_length=255)
    slug = models.SlugField(_('Slug'), max_length=280, unique=True, blank=True)
    academic_degree = models.CharField(_('Ilmiy daraja'), max_length=100, blank=True)
    affiliation_uz = models.CharField(_('Ish joyi/lavozimi (uz)'), max_length=300, blank=True)
    affiliation_ru = models.CharField(_('Ish joyi/lavozimi (ru)'), max_length=300, blank=True)
    affiliation_en = models.CharField(_('Ish joyi/lavozimi (en)'), max_length=300, blank=True)
    photo = models.ImageField(_('Rasm'), upload_to='authors/', blank=True, null=True)
    bio_uz = models.TextField(_('Biografiya (uz)'), blank=True)
    bio_ru = models.TextField(_('Biografiya (ru)'), blank=True)
    bio_en = models.TextField(_('Biografiya (en)'), blank=True)
    orcid_id = models.CharField(_('ORCID iD'), max_length=25, blank=True)
    email = models.EmailField(_('Email'), blank=True)
    # Kelajakda asosiy cancercenter.uz shifokorlar bazasi bilan sinxronlash uchun.
    external_doctor_id = models.CharField(
        _('Asosiy sayt Doctor ID (ixtiyoriy)'), max_length=64, blank=True,
        help_text=_('Kelajakda REST API orqali sinxronlash uchun tashqi ID.'),
    )

    class Meta:
        verbose_name = _('Muallif')
        verbose_name_plural = _('Mualliflar')
        ordering = ['full_name']

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.full_name) or 'author'
            slug = base
            i = 2
            while Author.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{i}'
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def affiliation(self):
        return translated(self, 'affiliation')

    @property
    def bio(self):
        return translated(self, 'bio')

    def get_absolute_url(self):
        return reverse('journal:author_detail', args=[self.slug])


class Keyword(models.Model):
    name = models.CharField(_('Kalit so\'z'), max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)

    class Meta:
        verbose_name = _('Kalit so\'z')
        verbose_name_plural = _('Kalit so\'zlar')
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Issue(models.Model):
    """Jurnal soni (Volume/Number/Year)."""

    volume = models.PositiveIntegerField(_('Volume (tom)'))
    number = models.PositiveIntegerField(_('Number (son)'))
    year = models.PositiveIntegerField(_('Yil'))
    title_uz = models.CharField(_('Sarlavha (uz)'), max_length=255, blank=True)
    title_ru = models.CharField(_('Sarlavha (ru)'), max_length=255, blank=True)
    title_en = models.CharField(_('Sarlavha (en)'), max_length=255, blank=True)
    cover_image = models.ImageField(_('Muqova'), upload_to='issues/', blank=True, null=True)
    published_date = models.DateField(_('Nashr sanasi'), blank=True, null=True)

    class Meta:
        verbose_name = _('Jurnal soni')
        verbose_name_plural = _('Jurnal sonlari')
        ordering = ['-year', '-volume', '-number']
        unique_together = ('volume', 'number', 'year')

    def __str__(self):
        return f'Vol. {self.volume}, No. {self.number} ({self.year})'

    @property
    def title(self):
        return translated(self, 'title') or str(self)


class Article(TimeStampedModel):
    """Ilmiy maqola."""

    class Status(models.TextChoices):
        DRAFT = 'draft', _('Qoralama')
        REVIEW = 'review', _('Ko\'rib chiqilmoqda')
        PUBLISHED = 'published', _('Chop etilgan')
        REJECTED = 'rejected', _('Rad etilgan')
        ARCHIVED = 'archived', _('Arxivlangan')

    class ArticleType(models.TextChoices):
        RESEARCH = 'research', _('Original tadqiqot')
        REVIEW = 'review', _('Sharh maqola')
        CASE_REPORT = 'case_report', _('Klinik kuzatuv')
        EDITORIAL = 'editorial', _('Muharrir maqolasi')
        CLINICAL_TRIAL = 'clinical_trial', _('Klinik sinov')
        OTHER = 'other', _('Boshqa')

    title_uz = models.CharField(_('Sarlavha (uz)'), max_length=500)
    title_ru = models.CharField(_('Sarlavha (ru)'), max_length=500, blank=True)
    title_en = models.CharField(_('Sarlavha (en)'), max_length=500, blank=True)
    slug = models.SlugField(_('Slug'), max_length=520, unique=True, blank=True)

    authors = models.ManyToManyField(Author, related_name='articles', verbose_name=_('Mualliflar'))

    abstract_uz = models.TextField(_('Annotatsiya (uz)'), blank=True)
    abstract_ru = models.TextField(_('Annotatsiya (ru)'), blank=True)
    abstract_en = models.TextField(_('Annotatsiya (en)'), blank=True)

    keywords = models.ManyToManyField(Keyword, related_name='articles', blank=True, verbose_name=_('Kalit so\'zlar'))

    category = models.ForeignKey(
        Category, related_name='articles', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name=_('Yo\'nalish'),
    )
    issue = models.ForeignKey(
        Issue, related_name='articles', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name=_('Jurnal soni'),
    )

    article_type = models.CharField(
        _('Maqola turi'), max_length=20, choices=ArticleType.choices, default=ArticleType.RESEARCH,
    )
    thumbnail_image = models.ImageField(_('Kichik rasm'), upload_to='articles/thumbs/', blank=True, null=True)
    is_open_access = models.BooleanField(_('Ochiq kirish'), default=True)

    pdf_file = models.FileField(_('PDF fayl'), upload_to='articles/%Y/%m/', blank=True, null=True)
    doi = models.CharField(_('DOI'), max_length=120, blank=True)
    pages = models.CharField(_('Sahifalar'), max_length=40, blank=True)

    publication_date = models.DateField(_('Nashr sanasi'), default=timezone.now)
    citation_count = models.PositiveIntegerField(_('Iqtiboslar soni'), default=0)
    views_count = models.PositiveIntegerField(_('Ko\'rishlar soni'), default=0)

    status = models.CharField(_('Holat'), max_length=12, choices=Status.choices, default=Status.DRAFT)

    submitted_by = models.ForeignKey(
        'auth.User', related_name='submitted_articles',
        on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name=_('Topshirgan foydalanuvchi'),
    )
    rejection_reason = models.TextField(_('Rad etish sababi'), blank=True, help_text=_('Admin tomonidan rad etilganda yoziladi.'))

    class Meta:
        verbose_name = _('Maqola')
        verbose_name_plural = _('Maqolalar')
        ordering = ['-publication_date', '-created_at']
        indexes = [
            models.Index(fields=['status', '-publication_date']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.title_uz

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title_en or self.title_uz)[:480] or 'article'
            slug = base
            i = 2
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{i}'
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def title(self):
        return translated(self, 'title')

    @property
    def abstract(self):
        return translated(self, 'abstract')

    @property
    def is_published(self):
        return self.status == self.Status.PUBLISHED

    @property
    def year(self):
        return self.publication_date.year if self.publication_date else None

    def get_absolute_url(self):
        return reverse('journal:article_detail', args=[self.slug])

    def citation_apa(self):
        """Simple APA-style citation string."""
        names = [a.full_name for a in self.authors.all()]
        if len(names) > 1:
            author_str = ', '.join(names[:-1]) + ' & ' + names[-1]
        else:
            author_str = names[0] if names else ''
        year = self.year or ''
        parts = [p for p in [f'{author_str} ({year}).' if author_str else '', f'{self.title}.'] if p]
        cite = ' '.join(parts)
        if self.issue:
            cite += f' Vol. {self.issue.volume}({self.issue.number}).'
        if self.doi:
            cite += f' https://doi.org/{self.doi}'
        return cite.strip()


class EditorialBoardMember(models.Model):
    """Ilmiy kengash a'zosi."""

    full_name = models.CharField(_('F.I.O.'), max_length=255)
    position_uz = models.CharField(_('Lavozim (uz)'), max_length=200, blank=True)
    position_ru = models.CharField(_('Lavozim (ru)'), max_length=200, blank=True)
    position_en = models.CharField(_('Lavozim (en)'), max_length=200, blank=True)
    academic_degree = models.CharField(_('Ilmiy daraja'), max_length=200, blank=True)
    photo = models.ImageField(_('Rasm'), upload_to='board/', blank=True, null=True)
    email = models.EmailField(_('Email'), blank=True)
    orcid_id = models.CharField(_('ORCID iD'), max_length=25, blank=True)
    is_editor_in_chief = models.BooleanField(_('Bosh muharrir'), default=False)
    order = models.PositiveIntegerField(_('Tartib'), default=0)

    class Meta:
        verbose_name = _('Ilmiy kengash a\'zosi')
        verbose_name_plural = _('Ilmiy kengash')
        ordering = ['order', 'full_name']

    def __str__(self):
        return self.full_name

    @property
    def position(self):
        return translated(self, 'position')


class Conference(TimeStampedModel):
    """Konferensiya."""

    title_uz = models.CharField(_('Sarlavha (uz)'), max_length=400)
    title_ru = models.CharField(_('Sarlavha (ru)'), max_length=400, blank=True)
    title_en = models.CharField(_('Sarlavha (en)'), max_length=400, blank=True)
    slug = models.SlugField(_('Slug'), max_length=420, unique=True, blank=True)
    description_uz = models.TextField(_('Tavsif (uz)'), blank=True)
    description_ru = models.TextField(_('Tavsif (ru)'), blank=True)
    description_en = models.TextField(_('Tavsif (en)'), blank=True)
    date_start = models.DateField(_('Boshlanish sanasi'))
    date_end = models.DateField(_('Tugash sanasi'), blank=True, null=True)
    location_uz = models.CharField(_('Manzil (uz)'), max_length=300, blank=True)
    location_ru = models.CharField(_('Manzil (ru)'), max_length=300, blank=True)
    location_en = models.CharField(_('Manzil (en)'), max_length=300, blank=True)
    poster_image = models.ImageField(_('Afisha'), upload_to='conferences/', blank=True, null=True)
    program_pdf = models.FileField(_('Dastur (PDF)'), upload_to='conferences/programs/', blank=True, null=True)
    registration_url = models.URLField(_('Ro\'yxatdan o\'tish havolasi'), blank=True)

    class Meta:
        verbose_name = _('Konferensiya')
        verbose_name_plural = _('Konferensiyalar')
        ordering = ['-date_start']

    def __str__(self):
        return self.title_uz

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title_en or self.title_uz)[:400] or 'conference'
            slug = base
            i = 2
            while Conference.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{i}'
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def title(self):
        return translated(self, 'title')

    @property
    def description(self):
        return translated(self, 'description')

    @property
    def location(self):
        return translated(self, 'location')

    @property
    def is_upcoming(self):
        end = self.date_end or self.date_start
        return end >= timezone.now().date()

    def get_absolute_url(self):
        return reverse('journal:conference_detail', args=[self.slug])


class ScientificDepartment(models.Model):
    """Ilmiy kafedra (asosiy sayt Department modelidan mustaqil)."""

    name_uz = models.CharField(_('Nomi (uz)'), max_length=300)
    name_ru = models.CharField(_('Nomi (ru)'), max_length=300, blank=True)
    name_en = models.CharField(_('Nomi (en)'), max_length=300, blank=True)
    slug = models.SlugField(_('Slug'), max_length=320, unique=True, blank=True)
    head_of_department = models.ForeignKey(
        Author, related_name='headed_departments', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name=_('Kafedra mudiri'),
    )
    description_uz = models.TextField(_('Tavsif (uz)'), blank=True)
    description_ru = models.TextField(_('Tavsif (ru)'), blank=True)
    description_en = models.TextField(_('Tavsif (en)'), blank=True)
    order = models.PositiveIntegerField(_('Tartib'), default=0)

    class Meta:
        verbose_name = _('Kafedra')
        verbose_name_plural = _('Kafedralar')
        ordering = ['order', 'name_uz']

    def __str__(self):
        return self.name_uz

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en or self.name_uz)
        super().save(*args, **kwargs)

    @property
    def name(self):
        return translated(self, 'name')

    @property
    def description(self):
        return translated(self, 'description')


class PostgraduateProgram(TimeStampedModel):
    """Aspirantura / Ordinatura."""

    class ProgramType(models.TextChoices):
        ASPIRANTURA = 'aspirantura', _('Aspirantura')
        ORDINATURA = 'ordinatura', _('Ordinatura')

    program_type = models.CharField(_('Turi'), max_length=20, choices=ProgramType.choices)
    title_uz = models.CharField(_('Nomi (uz)'), max_length=400)
    title_ru = models.CharField(_('Nomi (ru)'), max_length=400, blank=True)
    title_en = models.CharField(_('Nomi (en)'), max_length=400, blank=True)
    description_uz = models.TextField(_('Tavsif (uz)'), blank=True)
    description_ru = models.TextField(_('Tavsif (ru)'), blank=True)
    description_en = models.TextField(_('Tavsif (en)'), blank=True)
    requirements_pdf = models.FileField(_('Talablar (PDF)'), upload_to='programs/', blank=True, null=True)
    deadline = models.DateField(_('Muddat'), blank=True, null=True)
    is_active = models.BooleanField(_('Faol'), default=True)

    class Meta:
        verbose_name = _('Aspirantura/Ordinatura dasturi')
        verbose_name_plural = _('Aspirantura/Ordinatura')
        ordering = ['program_type', '-created_at']

    def __str__(self):
        return f'{self.get_program_type_display()}: {self.title_uz}'

    @property
    def title(self):
        return translated(self, 'title')

    @property
    def description(self):
        return translated(self, 'description')


class Grant(TimeStampedModel):
    """Grant / Ilmiy loyiha."""

    class Status(models.TextChoices):
        ACTIVE = 'active', _('Faol')
        COMPLETED = 'completed', _('Yakunlangan')

    title_uz = models.CharField(_('Nomi (uz)'), max_length=400)
    title_ru = models.CharField(_('Nomi (ru)'), max_length=400, blank=True)
    title_en = models.CharField(_('Nomi (en)'), max_length=400, blank=True)
    description_uz = models.TextField(_('Tavsif (uz)'), blank=True)
    description_ru = models.TextField(_('Tavsif (ru)'), blank=True)
    description_en = models.TextField(_('Tavsif (en)'), blank=True)
    funding_source = models.CharField(_('Moliyalashtiruvchi'), max_length=300, blank=True)
    year = models.PositiveIntegerField(_('Yil'), blank=True, null=True)
    status = models.CharField(_('Holat'), max_length=12, choices=Status.choices, default=Status.ACTIVE)
    principal_investigators = models.ManyToManyField(
        Author, related_name='grants', blank=True, verbose_name=_('Loyiha rahbarlari'),
    )

    class Meta:
        verbose_name = _('Grant')
        verbose_name_plural = _('Grantlar')
        ordering = ['-year', '-created_at']

    def __str__(self):
        return self.title_uz

    @property
    def title(self):
        return translated(self, 'title')

    @property
    def description(self):
        return translated(self, 'description')


class StaticPage(models.Model):
    """Statik sahifalar, masalan 'Mualliflar uchun' qoidalari."""

    key = models.SlugField(_('Kalit'), max_length=80, unique=True,
                           help_text=_("Masalan: 'for-authors', 'about'."))
    title_uz = models.CharField(_('Sarlavha (uz)'), max_length=300)
    title_ru = models.CharField(_('Sarlavha (ru)'), max_length=300, blank=True)
    title_en = models.CharField(_('Sarlavha (en)'), max_length=300, blank=True)
    body_uz = models.TextField(_('Matn (uz)'), blank=True)
    body_ru = models.TextField(_('Matn (ru)'), blank=True)
    body_en = models.TextField(_('Matn (en)'), blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Statik sahifa')
        verbose_name_plural = _('Statik sahifalar')
        ordering = ['key']

    def __str__(self):
        return self.title_uz

    @property
    def title(self):
        return translated(self, 'title')

    @property
    def body(self):
        return translated(self, 'body')


class Collection(models.Model):
    """Call for papers / mavzuli to'plam (Springer 'Call for papers')."""

    class Status(models.TextChoices):
        OPEN = 'open', _('Qabul ochiq')
        CLOSED = 'closed', _('Yopiq')

    title_uz = models.CharField(_('Sarlavha (uz)'), max_length=400)
    title_ru = models.CharField(_('Sarlavha (ru)'), max_length=400, blank=True)
    title_en = models.CharField(_('Sarlavha (en)'), max_length=400, blank=True)
    slug = models.SlugField(_('Slug'), max_length=420, unique=True, blank=True)
    description_uz = models.TextField(_('Tavsif (uz)'), blank=True)
    description_ru = models.TextField(_('Tavsif (ru)'), blank=True)
    description_en = models.TextField(_('Tavsif (en)'), blank=True)
    cover_image = models.ImageField(_('Rasm'), upload_to='collections/', blank=True, null=True)
    status = models.CharField(_('Holat'), max_length=10, choices=Status.choices, default=Status.OPEN)
    submission_deadline = models.DateField(_('Topshirish muddati'), blank=True, null=True)
    related_articles = models.ManyToManyField(
        'Article', related_name='collections', blank=True, verbose_name=_('Bog\'liq maqolalar'),
    )
    order = models.PositiveIntegerField(_('Tartib'), default=0)

    class Meta:
        verbose_name = _('To\'plam / Call for papers')
        verbose_name_plural = _('To\'plamlar / Call for papers')
        ordering = ['order', '-submission_deadline']

    def __str__(self):
        return self.title_uz

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title_en or self.title_uz)[:400] or 'collection'
            slug = base
            i = 2
            while Collection.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{i}'
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def title(self):
        return translated(self, 'title')

    @property
    def description(self):
        return translated(self, 'description')

    @property
    def is_open(self):
        return self.status == self.Status.OPEN

    def get_absolute_url(self):
        return reverse('journal:collection_detail', args=[self.slug])


class JournalMetric(models.Model):
    """Bosh sahifadagi 'Journal metrics' raqamlari (real ko'rsatkichlar)."""

    name_uz = models.CharField(_('Ko\'rsatkich nomi (uz)'), max_length=200)
    name_ru = models.CharField(_('Ko\'rsatkich nomi (ru)'), max_length=200, blank=True)
    name_en = models.CharField(_('Ko\'rsatkich nomi (en)'), max_length=200, blank=True)
    value = models.CharField(_('Qiymat'), max_length=50)
    year = models.PositiveIntegerField(_('Yil'), blank=True, null=True)
    order = models.PositiveIntegerField(_('Tartib'), default=0)

    class Meta:
        verbose_name = _('Jurnal ko\'rsatkichi')
        verbose_name_plural = _('Jurnal ko\'rsatkichlari')
        ordering = ['order']

    def __str__(self):
        return f'{self.name_uz}: {self.value}'

    @property
    def name(self):
        return translated(self, 'name')


class JournalUpdate(models.Model):
    """Journal updates — e'lonlar/yangiliklar bloki."""

    title_uz = models.CharField(_('Sarlavha (uz)'), max_length=400)
    title_ru = models.CharField(_('Sarlavha (ru)'), max_length=400, blank=True)
    title_en = models.CharField(_('Sarlavha (en)'), max_length=400, blank=True)
    slug = models.SlugField(_('Slug'), max_length=420, unique=True, blank=True)
    content_uz = models.TextField(_('Matn (uz)'), blank=True)
    content_ru = models.TextField(_('Matn (ru)'), blank=True)
    content_en = models.TextField(_('Matn (en)'), blank=True)
    banner_image = models.ImageField(_('Banner rasm'), upload_to='updates/', blank=True, null=True)
    published_date = models.DateField(_('Nashr sanasi'), default=timezone.now)
    is_published = models.BooleanField(_('Chop etilgan'), default=True)

    class Meta:
        verbose_name = _('Jurnal yangiligi')
        verbose_name_plural = _('Jurnal yangiliklari')
        ordering = ['-published_date']

    def __str__(self):
        return self.title_uz

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title_en or self.title_uz)[:400] or 'update'
            slug = base
            i = 2
            while JournalUpdate.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{i}'
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def title(self):
        return translated(self, 'title')

    @property
    def content(self):
        return translated(self, 'content')

    def get_absolute_url(self):
        return reverse('journal:update_detail', args=[self.slug])


class NewsletterSubscription(models.Model):
    """'Sign up for alerts' — yangi maqolalar haqida xabar olish uchun email."""

    email = models.EmailField(_('Email'), unique=True)
    is_active = models.BooleanField(_('Faol'), default=True)
    created_at = models.DateTimeField(_('Obuna sanasi'), auto_now_add=True)

    class Meta:
        verbose_name = _('Obunachi')
        verbose_name_plural = _('Obunachilar (alerts)')
        ordering = ['-created_at']

    def __str__(self):
        return self.email


class JournalInfo(models.Model):
    """Jurnal haqida umumiy ma'lumot (overview, ISSN, indekslash). Singleton."""

    overview_uz = models.TextField(_('Umumiy ma\'lumot (uz)'), blank=True)
    overview_ru = models.TextField(_('Umumiy ma\'lumot (ru)'), blank=True)
    overview_en = models.TextField(_('Umumiy ma\'lumot (en)'), blank=True)
    issn_print = models.CharField(_('ISSN (Print)'), max_length=20, blank=True)
    issn_online = models.CharField(_('ISSN (Online)'), max_length=20, blank=True)
    indexed_in = models.TextField(
        _('Indekslangan bazalar'), blank=True,
        help_text=_('Har bir bazani yangi qatorga yozing (Google Scholar, Scopus, ...).'),
    )
    submit_url = models.URLField(_('Maqola yuborish havolasi'), blank=True)
    is_open_access_journal = models.BooleanField(_('Ochiq kirishli jurnal'), default=True)

    class Meta:
        verbose_name = _('Jurnal ma\'lumoti')
        verbose_name_plural = _('Jurnal ma\'lumoti')

    def __str__(self):
        return 'Jurnal ma\'lumoti'

    def save(self, *args, **kwargs):
        self.pk = 1  # Singleton
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _created = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def overview(self):
        return translated(self, 'overview')

    @property
    def indexed_list(self):
        return [line.strip() for line in self.indexed_in.splitlines() if line.strip()]
