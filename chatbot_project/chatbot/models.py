import json
from django.db import models
from django.contrib.auth.models import User
from mptt.models import MPTTModel, TreeForeignKey

class ActionType(models.Model):
    name = models.CharField(max_length=50, unique=True)

class Category(MPTTModel):
    name = models.CharField(max_length=200)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    
    # Ajoutez ces champs explicitement
    level = models.PositiveIntegerField(default=0, editable=False)
    lft = models.PositiveIntegerField(default=0, editable=False)
    rght = models.PositiveIntegerField(default=0, editable=False)
    tree_id = models.PositiveIntegerField(default=0, editable=False)

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name

class FAQ(models.Model):
    question = models.TextField()
    answer = models.JSONField(default=dict)  # Changé ici
  # Utilisation de JSONField pour des réponses complexes
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='faqs')
    language = models.CharField(max_length=2, choices=[('fr', 'Français'), ('en', 'English')], default='fr')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Nouveaux champs pour les liens et actions
    action_type = models.ForeignKey(ActionType, on_delete=models.SET_NULL, null=True, blank=True)
    action_data = models.JSONField(default=dict, blank=True, null=True)

    def save(self, *args, **kwargs):
        if isinstance(self.answer, str):
            try:
                self.answer = json.loads(self.answer)
            except json.JSONDecodeError:
                self.answer = {"text": self.answer}
        super().save(*args, **kwargs)

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    language = models.CharField(max_length=2, choices=[('fr', 'Français'), ('en', 'English')])

    def __str__(self):
        return f"Conversation {self.id} - {self.start_time}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    is_bot = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    related_faq = models.ForeignKey(FAQ, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{'Bot' if self.is_bot else 'User'}: {self.content[:50]}"