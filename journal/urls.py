from django.urls import path

from . import views

app_name = 'journal'

urlpatterns = [
    path('', views.home, name='home'),
    path('maqolalar/', views.article_list, name='article_list'),
    path('maqolalar/<slug:slug>/', views.article_detail, name='article_detail'),
    path('mualliflar/<slug:slug>/', views.author_detail, name='author_detail'),
    path('sonlar/', views.issue_list, name='issue_list'),
    path('sonlar/<int:pk>/', views.issue_detail, name='issue_detail'),
    path('ilmiy-kengash/', views.editorial_board, name='editorial_board'),
    path('kafedralar/', views.department_list, name='department_list'),
    path('konferensiyalar/', views.conference_list, name='conference_list'),
    path('konferensiyalar/<slug:slug>/', views.conference_detail, name='conference_detail'),
    path('aspirantura/', views.postgraduate, {'program_type': 'aspirantura'}, name='aspirantura'),
    path('ordinatura/', views.postgraduate, {'program_type': 'ordinatura'}, name='ordinatura'),
    path('grantlar/', views.grant_list, name='grant_list'),
    path('mualliflar-uchun/', views.for_authors, name='for_authors'),
    path('yangiliklar/', views.update_list, name='update_list'),
    path('yangiliklar/<slug:slug>/', views.update_detail, name='update_detail'),
    path('toplamlar/', views.collection_list, name='collection_list'),
    path('toplamlar/<slug:slug>/', views.collection_detail, name='collection_detail'),
    path('obuna/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('obuna/tasdiqlash/<str:token>/', views.newsletter_confirm, name='newsletter_confirm'),
    path('sahifa/<slug:key>/', views.static_page, name='static_page'),
    # Auth
    path('royxatdan-otish/', views.register_view, name='register'),
    path('kirish/', views.login_view, name='login'),
    path('chiqish/', views.logout_view, name='logout'),
    # Article submission
    path('maqola-yuborish/', views.submit_article, name='submit_article'),
    path('maqola-tahrirlash/<int:pk>/', views.edit_article, name='edit_article'),
    path('mening-maqolalarim/', views.my_articles, name='my_articles'),
    path('profil/', views.edit_profile, name='edit_profile'),
]
