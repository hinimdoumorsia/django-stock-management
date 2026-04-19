# <span style="color:#1565C0;">Backend — Architecture et logique métier</span>

---

## <span style="color:#1565C0;"> Vue d'ensemble du backend</span>

Le backend de ce projet repose sur l'architecture **MVT** de Django. Il orchestre toute la logique métier : authentification, contrôle d'accès par rôle, opérations CRUD, recherche, tri, filtrage et pagination.

![Architecture Backend Django](images/django.png)

---

## <span style="color:#1565C0;">Structure des fichiers backend</span>

```
inventory/
├── models.py       ← Tables de la base de données
├── forms.py        ← Validation des données saisies
├── views.py        ← Logique métier et traitement des requêtes
├── urls.py         ← Routage des adresses URL
└── admin.py        ← Interface d'administration

gestion_stock/
├── settings.py     ← Configuration globale
└── urls.py         ← Point d'entrée des URLs du projet
```

---

## <span style="color:#1565C0;"> Logique des rôles et permissions</span>

### Scénario global d'accès

![Architecture des rôles](images/selectRole.png)

### Fonctions utilitaires de contrôle d'accès

```python
# inventory/views.py

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

def can_manage_products(user):
    return user.is_authenticated and (
        user.is_superuser or
        user.groups.filter(name='superadmin').exists() or
        user.groups.filter(name='admin').exists()
    )
```

**Explication ligne par ligne :**

| Ligne | Ce qu'elle fait |
|---|---|
| `user.is_authenticated` | Vérifie que l'utilisateur est bien connecté. Sans ça, un visiteur anonyme passerait le test. |
| `user.is_superuser` | Donne accès total au compte Django créé avec `createsuperuser`. |
| `user.groups.filter(name='superadmin').exists()` | Cherche si l'utilisateur appartient au groupe nommé `superadmin`. Retourne `True` ou `False`. |
| `or` entre conditions | Un seul critère vrai suffit pour autoriser l'accès. |

!!! tip "Pourquoi des fonctions séparées ?"
    Chaque fonction est ensuite passée à `@user_passes_test(...)`. Avoir des fonctions nommées rend le code lisible : on comprend immédiatement quelle règle s'applique à chaque vue.

---

## <span style="color:#1565C0;">Les formulaires — `forms.py`</span>

### Rôle des formulaires dans le backend

### Cycle de traitement d'un formulaire

Le diagramme ci-dessous illustre le cycle complet de traitement d'un formulaire dans l'application :

![Cycle de formulaire - Backend](./images/cycleFormulaireBackend.png)

*Figure 1 : Cycle de vie d'un formulaire Django (création/modification)*

### Formulaire de catégorie

```python
# inventory/forms.py

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

**Explication détaillée :**

- `forms.ModelForm` — Django génère automatiquement les champs HTML à partir du modèle. Pas besoin de redéclarer chaque champ manuellement.
- `class Meta` — Classe interne obligatoire qui dit à Django quel modèle utiliser et quels champs inclure.
- `model = Category` — Lie ce formulaire au modèle `Category`. La validation utilisera les contraintes définies dans le modèle (`max_length`, `unique`, etc.).
- `fields = ['name', 'description']` — Seuls ces deux champs apparaîtront dans le formulaire. `created_at` est exclu car il est rempli automatiquement.
- `widgets` — Permet de personnaliser le rendu HTML de chaque champ. Ici, on ajoute la classe Bootstrap `form-control` pour le style.

### Formulaire de produit

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

**Explication des widgets :**

| Champ | Widget utilisé | Pourquoi |
|---|---|---|
| `name` | `TextInput` | Champ texte simple, une seule ligne |
| `description` | `Textarea` | Zone de texte multi-lignes, `rows=4` fixe la hauteur |
| `price` | `NumberInput` | Clavier numérique, `step=0.01` autorise les centimes |
| `stock` | `NumberInput` | Entier positif uniquement |
| `category` | `Select` | Liste déroulante des catégories existantes |

!!! tip "À retenir"
    `ModelForm` gère automatiquement la validation (`required`, `max_length`, types), la liaison aux instances existantes pour la modification, et la sauvegarde en base avec `form.save()`.

---

## <span style="color:#1565C0;">Les vues — `views.py`</span>

### Vue liste — recherche, filtre, tri, pagination

#### Scénario complet

![Scénario : Utilisateur consulte la liste](images/utilisateurConsultantliste.png)


#### Code annoté

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from .models import Product, Category
from .forms import ProductForm, CategoryForm

@login_required                          # (1) Accès réservé aux utilisateurs connectés
def product_list(request):
    query       = request.GET.get('q', '')          # (2) Terme de recherche saisi
    category_id = request.GET.get('category', '')   # (3) Filtre par catégorie
    sort        = request.GET.get('sort', 'name')   # (4) Critère de tri, défaut = nom

    products = Product.objects.select_related('category').all()  # (5) QuerySet optimisé

    if query:                            # (6) Applique la recherche textuelle si renseignée
        products = products.filter(
            Q(name__icontains=query) |          # Cherche dans le nom
            Q(description__icontains=query)     # OU dans la description
        )

    if category_id:                      # (7) Filtre par catégorie si sélectionnée
        products = products.filter(category_id=category_id)

    if sort in ['name', '-name', 'price', '-price']:  # (8) Tri sécurisé (whitelist)
        products = products.order_by(sort)

    paginator = Paginator(products, 6)                # (9) 6 produits par page
    page_obj  = paginator.get_page(request.GET.get('page'))

    categories = Category.objects.all()  # (10) Pour remplir la liste déroulante

    return render(request, 'inventory/product_list.html', {
        'page_obj':    page_obj,
        'categories':  categories,
        'query':       query,
        'category_id': category_id,
        'sort':        sort,
    })
```

**Explication de chaque annotation :**

=== "(1) @login_required"
    Décorateur Django qui redirige automatiquement vers la page de connexion si l'utilisateur n'est pas authentifié. Aucune ligne de code supplémentaire n'est nécessaire.

=== "(2) request.GET.get('q', '')"
    Lit le paramètre `q` dans l'URL (`?q=clavier`). Le deuxième argument `''` est la valeur par défaut si le paramètre est absent. Utiliser `.get()` évite une `KeyError`.

=== "(3) category_id"
    Fonctionne de la même façon : lit `?category=2` depuis l'URL. La valeur est une chaîne, Django la convertit en entier lors du filtre `filter(category_id=...)`.

=== "(4) sort"
    Valeur par défaut `'name'` : si aucun tri n'est demandé, les produits sont affichés par ordre alphabétique.

=== "(5) select_related('category')"
    Sans `select_related`, Django exécuterait une requête SQL séparée pour chaque produit afin de récupérer sa catégorie. Avec `select_related`, tout est chargé en **une seule requête SQL** (jointure).

=== "(6) Q(name__icontains=query)"
    `Q` permet de combiner des conditions avec `|` (OU) ou `&` (ET). `icontains` est une recherche insensible à la casse. Sans `Q`, on ne pourrait filtrer que sur un seul champ à la fois.

=== "(7) filter(category_id=category_id)"
    Filtre les produits appartenant à la catégorie sélectionnée. Si `category_id` est vide (aucun filtre), cette ligne est ignorée grâce au `if`.

=== "(8) whitelist de tri"
    La liste `['name', '-name', 'price', '-price']` est une **liste blanche** : elle interdit toute valeur arbitraire envoyée via l'URL. Cela protège contre les injections dans `order_by()`. Le `-` devant un champ signifie tri décroissant.

=== "(9) Paginator(products, 6)"
    Découpe le QuerySet en pages de 6 éléments. `get_page()` gère les cas limites (page inexistante, page hors limite) sans lever d'exception.

=== "(10) Category.objects.all()"
    Récupère toutes les catégories pour alimenter la liste déroulante de filtrage dans le template.

---

### Vue détail d'un produit

```python
@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)   # (1)
    return render(request, 'inventory/product_detail.html', {
        'product': product
    })
```

- **(1) `get_object_or_404`** — Cherche le produit avec l'identifiant `pk`. Si aucun produit ne correspond, Django retourne automatiquement une page d'erreur HTTP 404 au lieu de planter avec une exception `DoesNotExist`.

---

### CRUD produit — admin et superadmin

#### Scénario : Ajout d'un produit

![Scénario : Ajout d'un produit](images/ajoutproduit.png)

#### Code — Créer un produit

```python
@login_required
@user_passes_test(can_manage_products)       # (1) Restreint aux admin et superadmin
def product_create(request):
    form = ProductForm(
        request.POST or None,                # (2) Données du formulaire si POST, sinon None
        request.FILES or None                # (3) Fichiers uploadés (photo)
    )
    if form.is_valid():                      # (4) Validation complète par Django
        form.save()                          # (5) INSERT en base de données
        messages.success(request, "Produit ajouté avec succès.")
        return redirect('product_list')      # (6) Redirection après succès
    return render(request, 'inventory/product_form.html', {'form': form})
```

**Explication :**

- **(1) `@user_passes_test(can_manage_products)`** — Si la fonction retourne `False`, Django redirige vers la page de login (ou renvoie HTTP 403). La vue n'est jamais exécutée pour un profil non autorisé.
- **(2) `request.POST or None`** — Pattern Django idiomatique. En GET, `request.POST` est vide (falsy), donc `None` est passé, créant un formulaire vide. En POST, les données sont passées directement.
- **(3) `request.FILES or None`** — Même logique pour les fichiers. Sans cela, le champ `photo` ne serait jamais sauvegardé. Le template doit avoir `enctype="multipart/form-data"` pour que les fichiers arrivent.
- **(4) `form.is_valid()`** — Déclenche toutes les validations : types de champs, contraintes du modèle (`unique`, `max_length`), validateurs personnalisés.
- **(5) `form.save()`** — Crée un objet Python et exécute un `INSERT INTO` SQL. Retourne l'instance créée.
- **(6) `redirect('product_list')`** — Suit le pattern **Post/Redirect/Get** : empêche la double soumission si l'utilisateur rafraîchit la page.

#### Scénario : Modification d'un produit

![Scénario : Modification d'un produit](images/modificationproduit.png)

```python
@login_required
@user_passes_test(can_manage_products)
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(
        request.POST or None,
        request.FILES or None,
        instance=product                     # (1) Lie le formulaire au produit existant
    )
    if form.is_valid():
        form.save()                          # (2) UPDATE en base (pas INSERT)
        messages.success(request, "Produit modifié avec succès.")
        return redirect('product_list')
    return render(request, 'inventory/product_form.html', {'form': form})
```

- **(1) `instance=product`** — Clé de la modification : en passant l'instance existante, `ModelForm` pré-remplit les champs et sait qu'il faut faire un `UPDATE` et non un `INSERT`.
- **(2) `form.save()`** — Exécute un `UPDATE SET ... WHERE id=pk` en SQL.

#### Scénario : Suppression d'un produit


Le diagramme ci-dessous illustre le flux complet de suppression d'un produit dans l'application :

![Scénario de suppression d'un produit](./images/supressionecycle.png)

*Figure : Cycle de suppression d'un produit (GET → Confirmation → DELETE → Redirection)*

```python
@login_required
@user_passes_test(can_manage_products)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':             # (1) Confirme que c'est bien une action intentionnelle
        product.delete()                     # (2) DELETE en base
        messages.warning(request, "Produit supprimé.")
        return redirect('product_list')
    return render(request, 'inventory/product_confirm_delete.html', {
        'product': product
    })
```

- **(1) `if request.method == 'POST'`** — La suppression ne s'exécute qu'après confirmation via un formulaire POST. Un simple lien GET ne peut pas supprimer un enregistrement, ce qui évite les suppressions accidentelles.
- **(2) `product.delete()`** — Exécute `DELETE FROM inventory_product WHERE id=pk` et supprime également le fichier photo associé si `ImageField` est configuré pour ça.

---

### CRUD catégorie — superadmin uniquement

```python
@login_required
@user_passes_test(is_superadmin)             # (1) Réservé exclusivement au superadmin
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

- **(1) `@user_passes_test(is_superadmin)`** — Seul le superadmin peut gérer les catégories. Un admin qui tente d'accéder à ces URLs est automatiquement bloqué.

!!! danger "Règle métier importante"
    Si un admin tente d'accéder à `/categories/add/`, Django le redirige vers la page de login (comportement par défaut de `user_passes_test`). Pour personnaliser ce comportement, il faut utiliser `user_passes_test(..., login_url='/acces-interdit/')`.

---

## <span style="color:#1565C0;">Routage — `urls.py`</span>

### Scénario de routage

![Cycle d'une requête URL](images/cycleRequete.png)

### `inventory/urls.py`

```python
from django.urls import path
from . import views

urlpatterns = [
    # ── Produits ────────────────────────────────────────────
    path('',
         views.product_list,
         name='product_list'),                   # Liste + recherche + tri

    path('products/<int:pk>/',
         views.product_detail,
         name='product_detail'),                 # Détail d'un produit

    path('products/add/',
         views.product_create,
         name='product_create'),                 # Créer un produit

    path('products/<int:pk>/edit/',
         views.product_update,
         name='product_update'),                 # Modifier un produit

    path('products/<int:pk>/delete/',
         views.product_delete,
         name='product_delete'),                 # Supprimer un produit

    # ── Catégories (superadmin uniquement) ──────────────────
    path('categories/',
         views.category_list,
         name='category_list'),

    path('categories/add/',
         views.category_create,
         name='category_create'),

    path('categories/<int:pk>/edit/',
         views.category_update,
         name='category_update'),

    path('categories/<int:pk>/delete/',
         views.category_delete,
         name='category_delete'),
]
```

**Points clés :**

| Élément | Explication |
|---|---|
| `<int:pk>` | Capture un entier dans l'URL et le passe comme argument `pk` à la vue. `int:` valide que c'est bien un entier. |
| `name='...'` | Permet d'utiliser `{% url 'product_list' %}` dans les templates sans hardcoder les URLs. |
| `include('inventory.urls')` | Délègue le routage à l'application. Le projet principal n'a pas à connaître les détails. |

### `gestion_stock/urls.py`

```python
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',       include('inventory.urls')),   # (1)
]

if settings.DEBUG:                               # (2)
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
```

- **(1) `include('inventory.urls')`** — Toutes les URLs de l'application `inventory` sont montées à la racine `/`. On pourrait les monter sous `/stock/` en écrivant `path('stock/', include('inventory.urls'))`.
- **(2) `if settings.DEBUG`** — En développement uniquement, Django sert lui-même les fichiers médias (photos des produits). En production, c'est le serveur web (Nginx) qui s'en charge.

---

## <span style="color:#1565C0;">Flux complet d'une requête backend</span>

---
![Flux complet — Ajout produit](images/ajoutproduit.png)

---

## <span style="color:#1565C0;">Tableau récapitulatif des vues</span>

| Vue | URL | Méthode | Rôle autorisé | Action SQL |
|---|---|---|---|---|
| `product_list` | `/` | GET | Tous | `SELECT` |
| `product_detail` | `/products/<pk>/` | GET | Tous | `SELECT` |
| `product_create` | `/products/add/` | GET / POST | Admin, Superadmin | `INSERT` |
| `product_update` | `/products/<pk>/edit/` | GET / POST | Admin, Superadmin | `UPDATE` |
| `product_delete` | `/products/<pk>/delete/` | GET / POST | Admin, Superadmin | `DELETE` |
| `category_list` | `/categories/` | GET | Superadmin | `SELECT` |
| `category_create` | `/categories/add/` | GET / POST | Superadmin | `INSERT` |
| `category_update` | `/categories/<pk>/edit/` | GET / POST | Superadmin | `UPDATE` |
| `category_delete` | `/categories/<pk>/delete/` | GET / POST | Superadmin | `DELETE` |

---

!!! abstract "Bonnes pratiques backend appliquées dans ce projet"
    - **Post/Redirect/Get** — Après tout POST réussi, on redirige. Évite la double soumission.
    - **Whitelist de tri** — Les valeurs de `sort` sont vérifiées contre une liste autorisée avant `order_by()`.
    - **`get_object_or_404`** — Jamais de `Product.objects.get(pk=pk)` nu, qui planterait avec une exception non gérée.
    - **`select_related`** — Toujours utilisé sur les QuerySets qui accèdent aux relations, pour éviter le problème N+1.
    - **Décorateurs de permission** — La sécurité est appliquée au niveau de la vue, pas dans le template.


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