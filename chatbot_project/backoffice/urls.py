from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BackofficeCategoryViewSet, BackofficeFAQViewSet, BackofficeConversationViewSet, BackofficeMessageViewSet

router = DefaultRouter()
router.register(r'categories', BackofficeCategoryViewSet)
router.register(r'faqs', BackofficeFAQViewSet)
router.register(r'conversations', BackofficeConversationViewSet)
router.register(r'messages', BackofficeMessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]