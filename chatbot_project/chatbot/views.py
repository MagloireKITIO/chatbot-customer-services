import logging
import os
import string
from django.http import FileResponse
from django.conf import settings
from rest_framework import viewsets, status 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import ActionType, Category, FAQ, Conversation, Message
from .serializers import ActionTypeSerializer, CategorySerializer, FAQSerializer, ConversationSerializer, MessageSerializer
from .npl_utils import NLPProcessor
from rest_framework.permissions import AllowAny
import datetime
from .serializers import FAQSerializer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
import nltk


nlp_processor = NLPProcessor()

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

logger = logging.getLogger(__name__)

class ActionTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActionType.objects.all()
    serializer_class = ActionTypeSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class FAQViewSet(viewsets.ModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]  # Ceci permettra l'accès à tous sans authentification

    def create(self, request, *args, **kwargs):
        logger.info(f"Données reçues: {request.data}")
        try:
            serializer = self.get_serializer(data=request.data)
            logger.info(f"Serializer créé: {serializer}")
            if serializer.is_valid():
                logger.info("Serializer valide")
                self.perform_create(serializer)
                logger.info("FAQ créée avec succès")
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            else:
                logger.error(f"Erreurs de validation: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("Une erreur s'est produite lors de la création de la FAQ")
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_queryset(self):
        queryset = FAQ.objects.all()
        category = self.request.query_params.get('category', None)
        if category is not None:
            queryset = queryset.filter(category__name=category)
        return queryset
    

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

class ChatbotView(APIView):
    permission_classes = [AllowAny]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vectorizer = TfidfVectorizer(tokenizer=self.simple_tokenize, stop_words='english')
        self.faq_vectors = None
        self.faqs = None
        self.update_faq_vectors()

    def simple_tokenize(self, text):
        text = re.sub(r'[^\w\s]', '', text.lower())
        return text.split()

    def update_faq_vectors(self):
        self.faqs = list(FAQ.objects.all())  # Convertir en liste
        faq_texts = [faq.question for faq in self.faqs]
        self.faq_vectors = self.vectorizer.fit_transform(faq_texts)

    def preprocess_text(self, text):
        # Convertir en minuscules et supprimer la ponctuation
        text = text.lower().translate(str.maketrans("", "", string.punctuation))
        # Tokenization
        tokens = word_tokenize(text)
        # Suppression des stop words
        stop_words = set(stopwords.words('french'))
        tokens = [token for token in tokens if token not in stop_words]
        return tokens

    # def find_best_match(self, user_message):
    #     if not user_message:
    #         return None
    #     message_vector = self.vectorizer.transform([user_message])
    #     similarities = cosine_similarity(message_vector, self.faq_vectors)
    #     best_match_index = np.argmax(similarities[0])  # Utilisez np.argmax
    #     if similarities[0][best_match_index] > 0.5:  # Seuil de similarité
    #         return self.faqs[int(best_match_index)]  # Convertir en int
    #     return None

    def find_best_match(self, user_message):
        preprocessed_message = self.preprocess_text(user_message)
        
        faqs = FAQ.objects.all()
        best_match = None
        highest_score = 0

        for faq in faqs:
            preprocessed_question = self.preprocess_text(faq.question)
            
            # Calcul du score de correspondance
            score = len(set(preprocessed_message) & set(preprocessed_question)) / len(set(preprocessed_message) | set(preprocessed_question))
            
            if score > highest_score:
                highest_score = score
                best_match = faq

        # Augmenter le seuil si nécessaire
        if highest_score > 0.3:  # Vous pouvez ajuster ce seuil
            return best_match
        return None

    def post(self, request):
        user_message = request.data.get('message')
        if not user_message:
            return Response({"error": "Message is required"}, status=400)

        best_match = self.find_best_match(user_message)

        if best_match:
            # Vérifiez si la réponse est structurée (avec des étapes)
            if isinstance(best_match.answer, dict) and 'steps' in best_match.answer:
                response_data = {
                    'answer': {
                        'text': best_match.answer.get('text', ''),
                        'steps': best_match.answer.get('steps', [])
                    },
                    'action_type': 'DISPLAY_STEPS',
                    'action_data': None
                }
            else:
                response_data = {
                    'answer': best_match.answer,
                    'action_type': best_match.action_type,
                    'action_data': best_match.action_data
                }
        else:
            response_data = {
                'answer': {
                    'text': "Désolé, je n'ai pas trouvé de réponse à votre question. Puis-je vous mettre en relation avec un agent du service client ?",
                    'steps': []
                },
                'action_type': 'TRANSFER_TO_AGENT',
                'action_data': None
            }

        return Response(response_data)
    
class DownloadView(APIView):
    def get(self, request, document_id):
        # Logique pour récupérer le chemin du fichier basé sur document_id
        file_path = os.path.join(settings.MEDIA_ROOT, f'documents/{document_id}.pdf')
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
        else:
            return Response({"error": "File not found"}, status=404)
        
class TransferToAgentView(APIView):
    def post(self, request):
        conversation_id = request.data.get('conversation_id')
        
        if not conversation_id:
            return Response({"error": "Conversation ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        conversation = Conversation.objects.get(id=conversation_id)
        conversation.end_time = datetime.timezone.now()
        conversation.save()

        # Here you would implement the logic to transfer the conversation to a human agent
        # For now, we'll just send a message indicating the transfer

        transfer_message = "Vous allez être mis en relation avec un agent du service client." if conversation.language == 'fr' else "You will be connected to a customer service agent shortly."
        Message.objects.create(conversation=conversation, content=transfer_message, is_bot=True)

        return Response({"message": "Conversation transferred to agent"})
    

class WelcomeMessageView(APIView):
    def get(self, request):
        language = request.query_params.get('language', 'fr')
        welcome_message = FAQ.objects.filter(category__name='Welcome', language=language).first()
        
        if welcome_message:
            return Response({
                'message': welcome_message.answer,
                'action_type': welcome_message.action_type,
                'action_data': welcome_message.action_data
            })
        else:
            return Response({
                'message': "Bonjour, 😊 Merci d'avoir contacté ACTIVA ASSURANCE. Je suis Ruby, votre conseillère,  Dites nous comment nous pouvons vous aider s'il vous plaît?",
                'action_type': None,
                'action_data': None
            })