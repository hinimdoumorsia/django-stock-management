from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Category, Product
from .models import Category, Product, Profile

# ============ Formulaire pour les catégories ============
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de la catégorie'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description de la catégorie (optionnelle)'
            }),
        }

# ============ Formulaire pour les produits ============
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'photo', 'category']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du produit'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description détaillée du produit'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Prix en DH'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Quantité en stock'
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

# ============ Formulaire d'inscription utilisateur (NOUVEAU) ============
# Ce formulaire permet aux nouveaux utilisateurs de créer un compte
# Il hérite de UserCreationForm qui gère déjà les mots de passe
class UserRegistrationForm(UserCreationForm):
    # Champ email obligatoire pour la confirmation
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'exemple@email.com'
    }))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Nom d'utilisateur"
            }),
        }
    
    # Validation personnalisée pour vérifier que l'email n'est pas déjà utilisé
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email
    

    # ============ NOUVEAU : Formulaire de modification du profil ============
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Nom d'utilisateur"
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': "Email"
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Prénom"
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Nom"
            }),
        }

        # ============ NOUVEAU : Formulaire pour la photo de profil et infos supplémentaires ============
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo', 'bio', 'phone', 'address']
        widgets = {
            'photo': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Parlez-nous de vous...'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre numéro de téléphone'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre adresse'
            }),
        }