Dans cette partie, nous allons explorer l'installation des différents éléments du projet ainsi que la mise en place d'un environnement de développement fonctionnel afin de démarrer le projet dans de bonnes conditions.

---

## Étape 0 — Préparer l'environnement

### Qu'est-ce qu'un environnement virtuel ?

Un environnement virtuel est un espace isolé dans lequel Python installe uniquement les dépendances d'un projet spécifique.
Cela permet d'éviter les conflits entre différentes versions de bibliothèques utilisées dans plusieurs projets.

### Pourquoi l'utiliser ?

- Isoler les dépendances du projet
- Éviter les conflits entre versions de packages
- Faciliter le déploiement et la reproduction du projet sur une autre machine
- Garder un projet propre et organisé

### Création et activation de l'environnement

```bash
python -m venv .venv
```

=== "Windows"

    ```bash
    .venv\Scripts\activate
    ```

=== "Linux / macOS"

    ```bash
    source .venv/bin/activate
    ```

### Installation des dépendances

```bash
pip install django Pillow
pip freeze > requirements.txt
```

### Vérification des dépendances

Une fois toutes les installations effectuées, vous pouvez ouvrir le fichier `requirements.txt` afin de vérifier les bibliothèques installées dans le projet.

=== "Linux / macOS"

    ```bash
    cat requirements.txt
    ```

=== "Windows"

    ```bash
    type requirements.txt
    ```

Vous devriez voir une liste similaire à :

```
Django==5.x.x
Pillow==10.x.x
```

---

## Étape 1 — Créer le projet et l'application

### Commandes

```bash
django-admin startproject gestion_stock .
python manage.py startapp inventory
```

### Arborescence minimale

```
gestion_stock/
├── manage.py
├── gestion_stock/
│   └── settings.py
├── inventory/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   └── urls.py
├── templates/
│   └── inventory/
└── media/
```

### Description rapide

| Fichier | Rôle |
|---|---|
| `manage.py` | Point d'entrée des commandes Django |
| `settings.py` | Configuration globale du projet |
| `models.py` | Définition des tables de la base de données |
| `forms.py` | Formulaires liés aux modèles |
| `views.py` | Logique de traitement des requêtes |
| `urls.py` | Routage des URLs de l'application |
| `templates/inventory/` | Fichiers HTML de l'interface |
| `media/` | Fichiers uploadés par les utilisateurs |


## Étape 2 — Configurer `settings.py`

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'inventory',  # (1)
]

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Casablanca'

STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

1. Ajouter le nom de l'application ici.

!!! danger "Erreurs fréquentes"
    - Oublier `inventory` dans `INSTALLED_APPS`
    - Oublier `MEDIA_ROOT`
    - Confondre `static` et `media`

---

## Étape 3 — Modèle `Category`

```python
from django.db import models

class Category(models.Model):
    name        = models.CharField("Nom", max_length=120, unique=True)
    description = models.TextField("Description", blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering         = ['name']
        verbose_name     = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.name
```

!!! tip "À retenir"
    Une catégorie permet d'organiser les produits : informatique, bureautique, alimentation, etc.

---

## Étape 4 — Modèle `Product`

```python
class Product(models.Model):
    STATUS_CHOICES = [
        ('available', 'Disponible'),
        ('low',       'Stock faible'),
        ('out',       'Rupture'),
    ]

    name        = models.CharField("Nom du produit", max_length=150)
    description = models.TextField("Description", blank=True)
    price       = models.DecimalField("Prix", max_digits=10, decimal_places=2)
    stock       = models.PositiveIntegerField("Quantité en stock", default=0)
    photo       = models.ImageField(upload_to='products/', blank=True, null=True)
    category    = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='products'
    )
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering         = ['name']
        verbose_name     = "Produit"
        verbose_name_plural = "Produits"

    def __str__(self):
        return self.name

    @property
    def stock_status(self):
        if self.stock == 0:
            return 'out'
        elif self.stock <= 5:
            return 'low'
        return 'available'
```

### Analyse métier du modèle

| Champ        | Rôle                        |
|--------------|-----------------------------|
| `name`       | Nom de l'article            |
| `description`| Détail ou fiche descriptive |
| `price`      | Prix unitaire               |
| `stock`      | Quantité disponible         |
| `photo`      | Image du produit            |
| `category`   | Catégorie associée          |
| `created_at` | Date de création            |
| `updated_at` | Dernière modification       |

!!! tip "Bonne pratique"
    La propriété `stock_status` évite de stocker un état redondant dans la base.

### Migrations et superutilisateur

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

!!! info "Mise en pratique"
    Tester ensuite l'interface admin de Django pour vérifier que les modèles ont bien été créés.

---

## Étape 5 — Enregistrer les modèles dans l'admin

```python
from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ('name', 'category', 'price', 'stock', 'created_at')
    search_fields = ('name', 'description')
    list_filter   = ('category', 'created_at')
```

!!! tip "À retenir"
    L'admin Django sert ici de laboratoire de test avant de créer l'interface utilisateur finale.

---

## Gestion des rôles et permissions

### Choix pédagogique pour les profils

On garde le modèle `User` par défaut de Django et on crée trois groupes :

- `superadmin`
- `admin`
- `viewer`

Les droits sont définis par les groupes, par des décorateurs, et par des vérifications dans les vues.

!!! note "Comparaison"
    Pour un TP initial, cette approche est plus simple qu'un modèle utilisateur personnalisé.

### Fonctions utilitaires de contrôle

```python
def is_superadmin(user):
    return user.is_authenticated and (
        user.is_superuser or
        user.groups.filter(name='superadmin').exists()
    )

def is_admin(user):
    return user.is_authenticated and (
        user.groups.filter(name='admin').exists()
    )

def is_viewer(user):
    return user.is_authenticated and (
        user.groups.filter(name='viewer').exists()
    )
```

!!! tip "Bonne pratique"
    Ces fonctions seront utilisées avec `user_passes_test` pour limiter l'accès à certaines vues.

---

## Étape 6 — Formulaire de catégorie

```python
from django import forms
from .models import Category, Product

class CategoryForm(forms.ModelForm):
    class Meta:
        model  = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3
            }),
        }
```

---

## Étape 7 — Formulaire de produit

```python
class ProductForm(forms.ModelForm):
    class Meta:
        model  = Product
        fields = ['name', 'description', 'price', 'stock', 'photo', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01'
            }),
            'stock':    forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }
```

!!! tip "À retenir"
    `ModelForm` simplifie la validation, la saisie et la maintenance.

---

## Étape 8 — Vues métiers

### Vue liste avec recherche, filtre et tri

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, Category

@login_required
def product_list(request):
    query       = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    sort        = request.GET.get('sort', 'name')

    products = Product.objects.select_related('category').all()

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
    if category_id:
        products = products.filter(category_id=category_id)
    if sort in ['name', '-name', 'price', '-price']:
        products = products.order_by(sort)

    paginator = Paginator(products, 6)
    page_obj  = paginator.get_page(request.GET.get('page'))
    categories = Category.objects.all()

    return render(request, 'inventory/product_list.html', {
        'page_obj':    page_obj,
        'categories':  categories,
        'query':       query,
        'category_id': category_id,
        'sort':        sort,
    })
```

| Point clé | Explication |
|---|---|
| `Q(...)` | Filtrage textuel sur plusieurs champs |
| `select_related` | Réduit le nombre de requêtes SQL |
| `Paginator` | Découpage des résultats en pages de 6 |
| `sort` | Gestion dynamique via les paramètres URL |

### Vue de détail d'un produit

```python
@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'inventory/product_detail.html', {
        'product': product
    })
```

!!! info "Mise en pratique"
    L'utilisateur simple doit au minimum pouvoir : consulter la liste, filtrer, trier, voir le détail d'un produit.

### CRUD produit — admin et superadmin

```python
def can_manage_products(user):
    return user.is_authenticated and (
        user.is_superuser or
        user.groups.filter(name='superadmin').exists() or
        user.groups.filter(name='admin').exists()
    )

@login_required
@user_passes_test(can_manage_products)
def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Produit ajouté avec succès.")
        return redirect('product_list')
    return render(request, 'inventory/product_form.html', {'form': form})

@login_required
@user_passes_test(can_manage_products)
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if form.is_valid():
        form.save()
        messages.success(request, "Produit modifié avec succès.")
        return redirect('product_list')
    return render(request, 'inventory/product_form.html', {'form': form})

@login_required
@user_passes_test(can_manage_products)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.warning(request, "Produit supprimé.")
        return redirect('product_list')
    return render(request, 'inventory/product_confirm_delete.html', {
        'product': product
    })
```

### CRUD catégorie — superadmin uniquement

```python
@login_required
@user_passes_test(is_superadmin)
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'inventory/category_list.html', {
        'categories': categories
    })

@login_required
@user_passes_test(is_superadmin)
def category_create(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Catégorie ajoutée avec succès.")
        return redirect('category_list')
    return render(request, 'inventory/category_form.html', {'form': form})

@login_required
@user_passes_test(is_superadmin)
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        messages.success(request, "Catégorie modifiée avec succès.")
        return redirect('category_list')
    return render(request, 'inventory/category_form.html', {'form': form})

@login_required
@user_passes_test(is_superadmin)
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.warning(request, "Catégorie supprimée.")
        return redirect('category_list')
    return render(request, 'inventory/category_confirm_delete.html', {
        'category': category
    })
```

---

## Étape 9 — `inventory/urls.py`

```python
from django.urls import path
from . import views

urlpatterns = [
    path('',                              views.product_list,    name='product_list'),
    path('products/<int:pk>/',            views.product_detail,  name='product_detail'),
    path('products/add/',                 views.product_create,  name='product_create'),
    path('products/<int:pk>/edit/',       views.product_update,  name='product_update'),
    path('products/<int:pk>/delete/',     views.product_delete,  name='product_delete'),
    path('categories/',                   views.category_list,   name='category_list'),
    path('categories/add/',              views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/',    views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/',  views.category_delete, name='category_delete'),
]
```

---

## Étape 10 — `gestion_stock/urls.py`

```python
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',       include('inventory.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
```

---

## Étape 11 — Gabarit de base

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Gestion de stock</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
          rel="stylesheet">
</head>
<body class="bg-light">

<nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container">
        <a class="navbar-brand" href="{% url 'product_list' %}">
            Stock Produits
        </a>
    </div>
</nav>

<div class="container py-4">
    {% if messages %}
        {% for message in messages %}
            <div class="alert alert-{{ message.tags }}">{{ message }}</div>
        {% endfor %}
    {% endif %}

    {% block content %}{% endblock %}
</div>

</body>
</html>
```

---

## Étape 12 — Liste des produits

```html
{% extends 'inventory/base.html' %}
{% block content %}

<h1 class="mb-4">Liste des produits</h1>

<form method="get" class="row g-3 mb-4">
    <div class="col-md-4">
        <input type="text" name="q" value="{{ query }}"
               class="form-control" placeholder="Recherche...">
    </div>
    <div class="col-md-3">
        <select name="category" class="form-select">
            <option value="">Toutes les catégories</option>
            {% for cat in categories %}
                <option value="{{ cat.id }}">{{ cat.name }}</option>
            {% endfor %}
        </select>
    </div>
    <div class="col-md-3">
        <select name="sort" class="form-select">
            <option value="name">Nom A-Z</option>
            <option value="price">Prix croissant</option>
        </select>
    </div>
    <div class="col-md-2">
        <button class="btn btn-primary">Filtrer</button>
    </div>
</form>

<div class="row">
    {% for product in page_obj %}
    <div class="col-md-4 mb-4">
        <div class="card h-100 shadow-sm">
            {% if product.photo %}
                <img src="{{ product.photo.url }}"
                     class="card-img-top" style="height: 220px;">
            {% endif %}
            <div class="card-body">
                <h5>{{ product.name }}</h5>
                <p>{{ product.category.name }}</p>
                <p><strong>Prix :</strong> {{ product.price }} DH</p>
                <p><strong>Stock :</strong> {{ product.stock }}</p>
                <a href="{% url 'product_detail' product.id %}"
                   class="btn btn-outline-primary btn-sm">Détail</a>
            </div>
        </div>
    </div>
    {% endfor %}
</div>

{% endblock %}
```

### Formulaire produit

```html
{% extends 'inventory/base.html' %}
{% block content %}

<h2 class="mb-4">Formulaire produit</h2>

<form method="post" enctype="multipart/form-data" class="card card-body shadow-sm">
    {% csrf_token %}
    {{ form.as_p }}
    <button class="btn btn-success">Enregistrer</button>
</form>

{% endblock %}
```

### Page détail produit

```html
{% extends 'inventory/base.html' %}
{% block content %}

<div class="card shadow-sm">
    <div class="row g-0">
        <div class="col-md-4">
            {% if product.photo %}
                <img src="{{ product.photo.url }}" class="img-fluid rounded-start">
            {% endif %}
        </div>
        <div class="col-md-8">
            <div class="card-body">
                <h3>{{ product.name }}</h3>
                <p><strong>Catégorie :</strong> {{ product.category.name }}</p>
                <p><strong>Description :</strong> {{ product.description }}</p>
                <p><strong>Prix :</strong> {{ product.price }} DH</p>
                <p><strong>Stock :</strong> {{ product.stock }}</p>
            </div>
        </div>
    </div>
</div>

{% endblock %}
```

---

## Tests et mise en pratique

### Créer les groupes dans l'admin

1. Se connecter à `/admin`
2. Créer les groupes : `superadmin`, `admin`, `viewer`
3. Créer des utilisateurs de test et les affecter à leur groupe

| Utilisateur | Groupe       |
|-------------|--------------|
| `super1`    | superadmin   |
| `admin1`    | admin        |
| `user1`     | viewer       |

### Scénarios de test attendus

1. Le superadmin crée des catégories
2. Le superadmin ajoute plusieurs produits avec photos
3. L'admin modifie le stock et le prix d'un produit
4. L'admin ne doit pas accéder au CRUD catégorie
5. L'utilisateur simple consulte les produits
6. L'utilisateur simple recherche par nom
7. L'utilisateur simple trie par prix ou stock
8. Vérifier qu'un accès interdit est bien bloqué

---

## Bonnes pratiques

| Bonne pratique         | Pourquoi                              |
|------------------------|---------------------------------------|
| Utiliser `ModelForm`   | Validation plus propre                |
| Séparer les rôles      | Sécurité et clarté métier             |
| Utiliser `select_related` | Optimisation des requêtes SQL      |
| Prévoir une page détail | Meilleure expérience utilisateur     |
| Ajouter `messages` Django | Retour visuel après action         |
| Paginer la liste       | Meilleure lisibilité                  |

---

## Extensions possibles

- Alerte automatique de stock faible
- Tableau de bord statistique
- Export CSV ou Excel
- Gestion des fournisseurs
- Historique des mouvements de stock
- Recherche avancée multi-critères
- Authentification personnalisée

!!! tip "Bonne pratique"
    Le TP peut évoluer progressivement vers une application de gestion commerciale complète.

---

## Exercices d'entraînement

1. Ajouter un champ `reference` au produit
2. Ajouter un badge visuel pour stock faible ou rupture
3. Interdire la suppression d'une catégorie contenant encore des produits
4. Ajouter une recherche par intervalle de prix
5. Ajouter une page d'accueil avec indicateurs : nombre total de produits, nombre de catégories, produits en rupture

---

## Mini-projet de consolidation

!!! abstract "Mini-projet"
    Réaliser une version personnelle du système avec :

    - Logo de l'établissement
    - Authentification
    - Gestion des catégories
    - Gestion des produits avec photo
    - Rôles utilisateurs
    - Recherche, tri, filtrage
    - Pagination
    - Interface Bootstrap propre


    ## 🌐 <b>Retrouvez-moi sur mes plateformes</b>

<div style="display:flex; gap:25px; flex-wrap:wrap; align-items:center;">

  <a href="https://www.linkedin.com/in/morsia-guitdam-hinimdou-266bb0269/" target="_blank" style="display:flex; align-items:center; gap:8px; text-decoration:none;">
    <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="22"/>
    LinkedIn
  </a>

  <a href="https://github.com/hinimdoumorsia" target="_blank" style="display:flex; align-items:center; gap:8px; text-decoration:none;">
    <img src="https://cdn-icons-png.flaticon.com/512/25/25231.png" width="22"/>
    GitHub
  </a>

  <a href="https://www.datacamp.com/portfolio/mhinimdou" target="_blank" style="display:flex; align-items:center; gap:8px; text-decoration:none;">
    <img src="/images/datacamp.jpg" width="22"/>
    DataCamp
  </a>

  <a href="https://www.kaggle.com/morsiahinimdou" target="_blank" style="display:flex; align-items:center; gap:8px; text-decoration:none;">
    <img src="/images/kaggleImg.png" width="22"/>
    Kaggle
  </a>

</div>