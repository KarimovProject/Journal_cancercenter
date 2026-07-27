from django.urls import path

from django.contrib.auth import views as auth_views
from . import views

app_name = 'journal'

urlpatterns = [
    path('api/admin-stats/', views.admin_stats_api, name='admin_stats_api'),
    path('', views.home, name='home'),
    path('maqolalar/', views.article_list, name='article_list'),
    path('maqolalar/<str:slug>/', views.article_detail, name='article_detail'),
    path('maqolalar/<str:slug>/iqtibos/<str:format>/', views.download_citation, name='download_citation'),
    path('mualliflar/<str:slug>/', views.author_detail, name='author_detail'),
    path('sonlar/', views.issue_list, name='issue_list'),
    path('sonlar/<int:pk>/', views.issue_detail, name='issue_detail'),
    path('ilmiy-kengash/', views.editorial_board, name='editorial_board'),
    path('kafedralar/', views.department_list, name='department_list'),
    path('konferensiyalar/', views.conference_list, name='conference_list'),
    path('konferensiyalar/<str:slug>/', views.conference_detail, name='conference_detail'),
    path('aspirantura/', views.postgraduate, {'program_type': 'aspirantura'}, name='aspirantura'),
    path('ordinatura/', views.postgraduate, {'program_type': 'ordinatura'}, name='ordinatura'),
    path('grantlar/', views.grant_list, name='grant_list'),
    path('mualliflar-uchun/', views.for_authors, name='for_authors'),
    path('yangiliklar/', views.update_list, name='update_list'),
    path('yangiliklar/<str:slug>/', views.update_detail, name='update_detail'),
    path('toplamlar/', views.collection_list, name='collection_list'),
    path('toplamlar/<str:slug>/', views.collection_detail, name='collection_detail'),
    path('obuna/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('obuna/tasdiqlash/<str:token>/', views.newsletter_confirm, name='newsletter_confirm'),
    path('sahifa/<str:key>/', views.static_page, name='static_page'),
    path('bildirishnoma/<int:notif_id>/', views.read_notification, name='read_notification'),
    # Auth
    path('royxatdan-otish/', views.register_view, name='register'),
    path('kirish/', views.login_view, name='login'),
    path('chiqish/', views.logout_view, name='logout'),
    
    # Password Reset
    path('parolni-tiklash/', auth_views.PasswordResetView.as_view(
        template_name='journal/auth/password_reset.html',
        email_template_name='journal/auth/password_reset_email.html',
        success_url='/ilm-fan/parolni-tiklash/yuborildi/'
    ), name='password_reset'),
    path('parolni-tiklash/yuborildi/', auth_views.PasswordResetDoneView.as_view(
        template_name='journal/auth/password_reset_done.html'
    ), name='password_reset_done'),
    path('parolni-tiklash/tasdiqlash/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='journal/auth/password_reset_confirm.html',
        success_url='/ilm-fan/parolni-tiklash/muvaffaqiyatli/'
    ), name='password_reset_confirm'),
    path('parolni-tiklash/muvaffaqiyatli/', auth_views.PasswordResetCompleteView.as_view(
        template_name='journal/auth/password_reset_complete.html'
    ), name='password_reset_complete'),
    # Article submission
    path('maqola-yuborish/', views.submit_article, name='submit_article'),
    path('maqola-tahrirlash/<int:pk>/', views.edit_article, name='edit_article'),
    path('mening-maqolalarim/', views.my_articles, name='my_articles'),
    path('profil/', views.edit_profile, name='edit_profile'),
    # Reviewer dashboard
    path('taqriz-paneli/', views.reviewer_dashboard, name='reviewer_dashboard'),
    path('taqriz-qilish/<int:pk>/', views.review_article, name='review_article'),
]
