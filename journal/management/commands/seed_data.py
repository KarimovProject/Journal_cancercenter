import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from journal.models import (
    Article,
    Author,
    Category,
    Collection,
    Conference,
    EditorialBoardMember,
    Grant,
    Issue,
    JournalInfo,
    JournalMetric,
    JournalUpdate,
    Keyword,
    PostgraduateProgram,
    ScientificDepartment,
    StaticPage,
)


class Command(BaseCommand):
    help = "Namuna (demo) ma'lumotlarni yaratadi."

    def handle(self, *args, **options):
        self.stdout.write('Seeding demo data...')

        categories = {
            'onkojarrohlik': ('Onkojarrohlik', 'Онкохирургия', 'Oncosurgery'),
            'radioterapiya': ('Radioterapiya', 'Радиотерапия', 'Radiotherapy'),
            'onkoginekologiya': ('Onkoginekologiya', 'Онкогинекология', 'Oncogynecology'),
            'kimyoterapiya': ('Kimyoterapiya', 'Химиотерапия', 'Chemotherapy'),
        }
        cat_objs = {}
        for i, (slug, (uz, ru, en)) in enumerate(categories.items()):
            obj, _ = Category.objects.get_or_create(
                slug=slug,
                defaults={'name_uz': uz, 'name_ru': ru, 'name_en': en, 'order': i},
            )
            cat_objs[slug] = obj

        authors_data = [
            ('Alisher Karimov', 'Onkojarrohlik bo\'limi mudiri, t.f.d.'),
            ('Dilnoza Rahimova', 'Radioterapiya bo\'limi shifokori, t.f.n.'),
            ('Sardor Yusupov', 'Onkoginekologiya bo\'limi, professor'),
            ('Malika Toshpulatova', 'Kimyoterapiya bo\'limi, t.f.n.'),
        ]
        author_objs = []
        for name, aff in authors_data:
            obj, _ = Author.objects.get_or_create(
                full_name=name, defaults={'affiliation_uz': aff},
            )
            author_objs.append(obj)

        kw_objs = []
        for kw in ['onkologiya', 'radioterapiya', 'immunoterapiya', 'diagnostika', 'MRT']:
            obj, _ = Keyword.objects.get_or_create(name=kw)
            kw_objs.append(obj)

        issue, _ = Issue.objects.get_or_create(
            volume=1, number=1, year=2025,
            defaults={'title_uz': 'Birinchi son', 'published_date': datetime.date(2025, 3, 1)},
        )

        articles = [
            ('onkojarrohlik', 'Lokal tarqalgan oshqozon saratonida jarrohlik yondashuvlar',
             'Locally advanced gastric cancer: surgical approaches',
             'Ushbu maqolada lokal tarqalgan oshqozon saratonini davolashda zamonaviy jarrohlik usullari tahlil qilinadi. 120 bemor ustida olib borilgan tadqiqot natijalari keltirilgan.'),
            ('radioterapiya', 'Ko\'krak bezi saratonida stereotaktik radioterapiya samaradorligi',
             'Efficacy of stereotactic radiotherapy in breast cancer',
             'Stereotaktik radioterapiyaning ko\'krak bezi saratoni bemorlarida uzoq muddatli natijalari o\'rganildi.'),
            ('onkoginekologiya', 'Bachadon bo\'yni saratonini erta aniqlash usullari',
             'Early detection methods for cervical cancer',
             'Skrining dasturlari va HPV testlari yordamida bachadon bo\'yni saratonini erta aniqlash imkoniyatlari muhokama qilinadi.'),
            ('kimyoterapiya', 'Zamonaviy immunoterapiya: kelajak istiqbollari',
             'Modern immunotherapy: future prospects',
             'Onkologiyada immunoterapiyaning rivojlanishi va checkpoint inhibitorlarining klinik qo\'llanilishi.'),
            ('onkojarrohlik', 'Minimal invaziv jarrohlik onkologiyada',
             'Minimally invasive surgery in oncology',
             'Laparoskopik va robotik jarrohlik usullarining an\'anaviy usullar bilan qiyosiy tahlili.'),
        ]
        art_types = [
            Article.ArticleType.RESEARCH, Article.ArticleType.REVIEW,
            Article.ArticleType.CASE_REPORT, Article.ArticleType.EDITORIAL,
            Article.ArticleType.CLINICAL_TRIAL,
        ]
        for i, (cat, title_uz, title_en, abstract) in enumerate(articles):
            art, created = Article.objects.get_or_create(
                title_uz=title_uz,
                defaults={
                    'title_en': title_en,
                    'abstract_uz': abstract,
                    'category': cat_objs[cat],
                    'issue': issue,
                    'status': Article.Status.PUBLISHED,
                    'article_type': art_types[i % len(art_types)],
                    'is_open_access': True,
                    'publication_date': datetime.date(2025, 1 + i, 10),
                    'doi': f'10.1234/onco.2025.{i+1:03d}',
                    'pages': f'{i*10+1}-{i*10+9}',
                    'views_count': (i + 1) * 37,
                    'citation_count': i * 2,
                },
            )
            if created:
                art.authors.add(author_objs[i % len(author_objs)], author_objs[(i + 1) % len(author_objs)])
                art.keywords.add(*kw_objs[: (i % 3) + 1])

        for i, (name, pos, deg) in enumerate([
            ('Alisher Karimov', 'Bosh muharrir', 't.f.d., professor'),
            ('Sardor Yusupov', 'Bosh muharrir o\'rinbosari', 'professor'),
            ('Dilnoza Rahimova', 'A\'zo', 't.f.n.'),
            ('Malika Toshpulatova', 'Ilmiy kotib', 't.f.n.'),
        ]):
            EditorialBoardMember.objects.get_or_create(
                full_name=name,
                defaults={'position_uz': pos, 'academic_degree': deg, 'order': i,
                          'is_editor_in_chief': i == 0},
            )

        for i, slug in enumerate(['onkojarrohlik', 'radioterapiya']):
            ScientificDepartment.objects.get_or_create(
                slug=f'kafedra-{slug}',
                defaults={
                    'name_uz': f'{cat_objs[slug].name_uz} kafedrasi',
                    'head_of_department': author_objs[i],
                    'description_uz': 'Kafedra ilmiy-tadqiqot va ta\'lim faoliyati bilan shug\'ullanadi.',
                    'order': i,
                },
            )

        today = timezone.now().date()
        Conference.objects.get_or_create(
            title_uz='Onkologiyada zamonaviy yondashuvlar — 2025',
            defaults={
                'title_en': 'Modern Approaches in Oncology — 2025',
                'description_uz': 'Xalqaro ilmiy-amaliy konferensiya. Onkologiya, radiologiya va immunoterapiya bo\'yicha ma\'ruzalar.',
                'date_start': today + datetime.timedelta(days=45),
                'date_end': today + datetime.timedelta(days=47),
                'location_uz': 'Toshkent, O\'zbekiston',
            },
        )
        Conference.objects.get_or_create(
            title_uz='Radioterapiya kongressi — 2024',
            defaults={
                'title_en': 'Radiotherapy Congress — 2024',
                'description_uz': 'Bo\'lib o\'tgan milliy kongress.',
                'date_start': today - datetime.timedelta(days=180),
                'date_end': today - datetime.timedelta(days=178),
                'location_uz': 'Samarqand, O\'zbekiston',
            },
        )

        PostgraduateProgram.objects.get_or_create(
            program_type=PostgraduateProgram.ProgramType.ASPIRANTURA,
            title_uz='Onkologiya yo\'nalishida aspirantura (PhD)',
            defaults={'description_uz': 'PhD dasturi bo\'yicha ilmiy tadqiqotlar olib borish imkoniyati.',
                      'deadline': today + datetime.timedelta(days=90)},
        )
        PostgraduateProgram.objects.get_or_create(
            program_type=PostgraduateProgram.ProgramType.ORDINATURA,
            title_uz='Klinik ordinatura — Onkologiya',
            defaults={'description_uz': '2 yillik klinik ordinatura dasturi.',
                      'deadline': today + datetime.timedelta(days=60)},
        )

        g, created = Grant.objects.get_or_create(
            title_uz='Onkologik kasalliklarni erta diagnostika qilish tizimi',
            defaults={
                'funding_source': 'Innovatsion rivojlanish vazirligi',
                'year': 2025, 'status': Grant.Status.ACTIVE,
                'description_uz': 'Sun\'iy intellekt yordamida onkologik kasalliklarni erta aniqlash.',
            },
        )
        if created:
            g.principal_investigators.add(author_objs[0])

        StaticPage.objects.get_or_create(
            key='for-authors',
            defaults={
                'title_uz': 'Mualliflar uchun qoidalar',
                'body_uz': 'Maqolalar onkologiya va radiologiya bo\'yicha original tadqiqotlarni qamrab olishi kerak. '
                           'Har bir maqola uch tilda sarlavha va annotatsiya bilan taqdim etilishi tavsiya etiladi.',
            },
        )

        # Journal metrics (real ko'rsatkichlar — Impact Factor emas)
        for i, (name, value, year) in enumerate([
            ('Yiliga nashr etilgan maqolalar', '48', 2024),
            ("O'rtacha ko'rib chiqish muddati (kun)", '32', 2024),
            ('Yillik yuklab olishlar', '12 400', 2024),
            ('Tahririyat a\'zolari', '18', 2024),
        ]):
            JournalMetric.objects.get_or_create(
                name_uz=name, defaults={'value': value, 'year': year, 'order': i},
            )

        # Call for papers
        Collection.objects.get_or_create(
            title_uz='Onkoimmunologiya: yangi ufqlar',
            defaults={
                'title_en': 'Oncoimmunology: New Horizons',
                'description_uz': 'Immunoterapiya va onkoimmunologiya sohasidagi original tadqiqotlar uchun maxsus to\'plam.',
                'status': Collection.Status.OPEN,
                'submission_deadline': today + datetime.timedelta(days=120),
                'order': 0,
            },
        )
        Collection.objects.get_or_create(
            title_uz='Radioterapiyada zamonaviy texnologiyalar',
            defaults={
                'title_en': 'Modern Technologies in Radiotherapy',
                'description_uz': 'Stereotaktik va adaptiv radioterapiya bo\'yicha maqolalar qabul qilinadi.',
                'status': Collection.Status.OPEN,
                'submission_deadline': today + datetime.timedelta(days=60),
                'order': 1,
            },
        )

        # Journal updates
        JournalUpdate.objects.get_or_create(
            title_uz='Jurnal Google Scholar bazasiga qo\'shildi',
            defaults={
                'title_en': 'Journal indexed in Google Scholar',
                'content_uz': 'Oncoscience jurnali endi Google Scholar bazasida indekslanadi, bu maqolalarning ko\'rinishini oshiradi.',
                'published_date': today - datetime.timedelta(days=10),
            },
        )
        JournalUpdate.objects.get_or_create(
            title_uz='2025-yil uchun maqolalar qabuli boshlandi',
            defaults={
                'title_en': 'Submissions open for 2025',
                'content_uz': 'Yangi son uchun maqolalar qabul qilinmoqda. Muallif qoidalari bilan tanishing.',
                'published_date': today - datetime.timedelta(days=3),
            },
        )

        # Journal info (singleton)
        info = JournalInfo.load()
        if not info.issn_online:
            info.overview_uz = (
                'Oncoscience — Respublika Ixtisoslashtirilgan Onkologiya va Radiologiya '
                'Ilmiy-Amaliy Tibbiyot Markazining ochiq kirishli, retsenzlanadigan ilmiy jurnali. '
                'Jurnal onkologiya, radiologiya va tegishli sohalar bo\'yicha original tadqiqotlarni chop etadi.'
            )
            info.issn_print = '3060-0000'
            info.issn_online = '3060-0001'
            info.indexed_in = 'Google Scholar\nCrossRef\nUzbek Scientific Citation Index'
            info.is_open_access_journal = True
            info.save()

        self.stdout.write(self.style.SUCCESS('Demo ma\'lumotlar muvaffaqiyatli yaratildi.'))
