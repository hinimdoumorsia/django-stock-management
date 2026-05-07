from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import Category, Product
from .models import Category, Product, Profile

# ============ Formulaire pour les catégories ============
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        labels = {
            'name': _('Nom'),
            'description': _('Description'),
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Nom de la catégorie')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Description de la catégorie (optionnelle)')
            }),
        }

# ============ Formulaire pour les produits ============
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'photo', 'category']
        labels = {
            'name': _('Nom du produit'),
            'description': _('Description'),
            'price': _('Prix'),
            'stock': _('Stock disponible'),
            'photo': _('Photo'),
            'category': _('Catégorie'),
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Nom du produit')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Description détaillée du produit')
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': _('Prix en DH')
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('Quantité en stock')
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

# ============ Formulaire d'inscription utilisateur ============
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': _('exemple@email.com')
    }))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': _("Nom d'utilisateur"),
            'email': _('Email'),
            'password1': _('Mot de passe'),
            'password2': _('Confirmation du mot de passe'),
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _("Nom d'utilisateur")
            }),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Cet email est déjà utilisé."))
        return email

# ============ Formulaire de modification du profil ============
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        labels = {
            'username': _("Nom d'utilisateur"),
            'email': _('Email'),
            'first_name': _('Prénom'),
            'last_name': _('Nom'),
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _("Nom d'utilisateur")
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _("Email")
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _("Prénom")
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _("Nom")
            }),
        }

# ============ Formulaire pour la photo de profil et infos supplémentaires ============
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['photo', 'bio', 'phone', 'address']
        labels = {
            'photo': _('Photo de profil'),
            'bio': _('Bio'),
            'phone': _('Téléphone'),
            'address': _('Adresse'),
        }
        widgets = {
            'photo': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Parlez-nous de vous...')
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Votre numéro de téléphone')
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Votre adresse')
            }),
        }