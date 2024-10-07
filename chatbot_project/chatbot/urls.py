from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ActionTypeViewSet, CategoryViewSet, FAQViewSet, ConversationViewSet, ChatbotView, TransferToAgentView, DownloadView, WelcomeMessageView

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'faqs', FAQViewSet)
router.register(r'conversations', ConversationViewSet)
router.register(r'action-types', ActionTypeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('chat/', ChatbotView.as_view(), name='chat'),
    path('transfer/', TransferToAgentView.as_view(), name='transfer'),
    path('download/<str:document_id>/', DownloadView.as_view(), name='download_document'),
     path('welcome/', WelcomeMessageView.as_view(), name='welcome'),

]