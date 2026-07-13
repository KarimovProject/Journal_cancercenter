from rest_framework.routers import DefaultRouter

from .api import ArticleViewSet, AuthorViewSet, CategoryViewSet, ConferenceViewSet

router = DefaultRouter()
router.register('articles', ArticleViewSet, basename='article')
router.register('categories', CategoryViewSet, basename='category')
router.register('authors', AuthorViewSet, basename='author')
router.register('conferences', ConferenceViewSet, basename='conference')

urlpatterns = router.urls
