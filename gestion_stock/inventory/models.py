from django.db import models
from django.urls import reverse
from django.conf import settings

class Category(models.Model):
    name = models.CharField("Nom", max_length=120, unique=True)
    description = models.TextField("Description", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_list')

    @property
    def product_count(self):
        return self.product_set.count()


class Product(models.Model):
    name = models.CharField("Nom du produit", max_length=200)
    description = models.TextField("Description", blank=True)
    price = models.DecimalField("Prix", max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField("Stock disponible", default=0)
    photo = models.ImageField("Photo", upload_to='products/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Catégorie")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Produit"
        verbose_name_plural = "Produits"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'pk': self.pk})

    @property
    def stock_status(self):
        if self.stock <= 0:
            return 'rupture'
        elif self.stock <= 5:
            return 'faible'
        else:
            return 'normal'

    @property
    def formatted_price(self):
        return f"{self.price:,.2f} DH"


# ============ MODÈLE POUR L'HISTORIQUE DES ACTIONS UTILISATEUR ============
class UserHistory(models.Model):
    ACTION_TYPES = [
        ('login', 'Connexion'),
        ('logout', 'Déconnexion'),
        ('view', 'Consultation'),
        ('create', 'Création'),
        ('update', 'Modification'),
        ('delete', 'Suppression'),
        ('search', 'Recherche'),
        ('filter', 'Filtrage'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Utilisateur")
    action = models.CharField("Action", max_length=20, choices=ACTION_TYPES)
    description = models.TextField("Description", blank=True)
    ip_address = models.GenericIPAddressField("Adresse IP", blank=True, null=True)
    created_at = models.DateTimeField("Date et heure", auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Historique utilisateur"
        verbose_name_plural = "Historiques utilisateurs"
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.created_at}"


# ============ MODÈLE POUR LA PHOTO DE PROFIL ============
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField("Photo de profil", upload_to='profiles/', blank=True, null=True)
    bio = models.TextField("Bio", blank=True, max_length=500)
    phone = models.CharField("Téléphone", max_length=20, blank=True)
    address = models.CharField("Adresse", max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profils"

    def __str__(self):
        return f"Profil de {self.user.username}"


# ============ MODÈLE POUR LES CONVERSATIONS DU CHATBOT ============
class ChatConversation(models.Model):
    FEEDBACK_TYPES = [
        ('complaint', 'Plainte'),
        ('suggestion', 'Suggestion'),
        ('question', 'Question'),
        ('other', 'Autre'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Utilisateur")
    session_id = models.CharField("Session ID", max_length=100)
    message = models.TextField("Message")
    response = models.TextField("Réponse")
    is_feedback = models.BooleanField("Est un feedback", default=False)
    feedback_type = models.CharField("Type de feedback", max_length=20, choices=FEEDBACK_TYPES, null=True, blank=True)
    created_at = models.DateTimeField("Date et heure", auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Conversation chatbot"
        verbose_name_plural = "Conversations chatbot"
    
    def __str__(self):
        return f"{self.created_at.strftime('%Y-%m-%d %H:%M')} - {self.message[:50]}"