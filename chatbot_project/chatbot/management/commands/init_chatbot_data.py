from django.core.management.base import BaseCommand
from chatbot.models import Category, ActionType
from django.db import transaction

class Command(BaseCommand):
    help = 'Initialize chatbot categories and action types'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write('Initializing chatbot data...')

        # Catégories
        categories = [
            {'name': 'Général', 'parent': None},
            {'name': 'Compte utilisateur', 'parent': None},
            {'name': 'Produits et services', 'parent': None},
            {'name': 'Paiement', 'parent': None},
            {'name': 'Support technique', 'parent': None},
            {'name': 'Politique de confidentialité', 'parent': None},
        ]

        for category_data in categories:
            category, created = Category.objects.get_or_create(
                name=category_data['name'],
                parent=category_data['parent']
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))
            else:
                self.stdout.write(f'Category already exists: {category.name}')

        # Types d'action
        action_types = [
            'OPEN_LINK',
            'DOWNLOAD_DOCUMENT',
            'SHOW_FORM',
            'TRANSFER_TO_AGENT',
            'SHOW_VIDEO',
            'OPEN_CHAT',
        ]

        for action_type in action_types:
            action, created = ActionType.objects.get_or_create(name=action_type)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created action type: {action.name}'))
            else:
                self.stdout.write(f'Action type already exists: {action.name}')

        self.stdout.write(self.style.SUCCESS('Chatbot data initialization completed successfully.'))