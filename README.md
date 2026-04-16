# Gestion de Stock - Application Web Django


#  Django Stock Management

![Version](https://img.shields.io/badge/version-1.0.0-7c6af7?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.x-092E20?style=for-the-badge&logo=django&logoColor=white)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-Frontend-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-Styling-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-UI-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)
![License](https://img.shields.io/badge/Licence-MIT-green?style=for-the-badge)

## 1. Presentation de l'application

Gestion de Stock est une application web complete developpee avec le framework Django. Elle permet aux entreprises et organisations de gerer efficacement leur inventaire de produits a travers une interface intuitive et securisee.

L'application couvre les besoins essentiels suivants :

- Gestion complete des produits : creation, modification, consultation et suppression
- Organisation des produits par categories
- Suivi des niveaux de stock en temps reel
- Recherche, filtrage et tri des produits
- Gestion des utilisateurs avec differents niveaux d'acces
- Historique des actions des utilisateurs
- Gestion des profils utilisateurs avec photos

---

## 2. Objectif et contexte du developpement

Cette application a été développée dans le cadre d’un travaux pratiques à l’ENSAM-Meknès, sous la supervision du Pr Brahim BAKKAS.

Elle repond a plusieurs besoins concrets :

- Moderniser la gestion d'inventaire traditionnelle basee sur des fichiers Excel
- Automatiser le suivi des produits et des stocks
- Securiser l'acces aux donnees grace a un systeme de roles
- Offrir une experience utilisateur fluide et intuitive
- Demonstrer la puissance de Django pour les applications metier

---

## 3. Architecture du projet

### 3.1 Architecture MVT (Model - View - Template)

Django repose sur le patron architectural MVT, une variante du MVC classique :

- **Model** : definit la structure des donnees et les relations entre entites (base de donnees SQLite)
- **View** : contient la logique metier, traite les requetes HTTP et retourne les reponses
- **Template** : gere l'affichage HTML envoye au navigateur
- **URLs** : systeme de routage qui dirige chaque requete vers la bonne vue
- **Static** : fichiers CSS et JavaScript pour l'interface

### 3.2 Structure des fichiers du projet

```
gestion_stock/
    gestion_stock/         <- Configuration principale
        settings.py        <- Parametres du projet
        urls.py            <- URLs principales
        wsgi.py            <- Point d'entree WSGI
    inventory/             <- Application principale
        models.py          <- Modeles (Category, Product, UserHistory, Profile)
        views.py           <- Vues et logique metier
        forms.py           <- Formulaires Django
        admin.py           <- Interface d'administration
        urls.py            <- URLs de l'application
        tokens.py          <- Generation de tokens d'activation
        utils.py           <- Fonctions utilitaires
    templates/             <- Templates HTML
        inventory/
            base.html      <- Template de base
            product_list.html
            product_detail.html
            product_form.html
            category_list.html
            user_profile.html
            user_history.html
            registration/  <- Templates d'authentification
    static/                <- Fichiers CSS
    media/                 <- Images uploadees
    env/                   <- Environnement virtuel
```

### 3.3 Relations entre les modeles

Le projet definit quatre modeles principaux interconnectes :

- **User** (Django natif) : gere les comptes, identifiants et mots de passe
- **Category** : contient un nom, une description et une date de creation. Chaque produit appartient a une categorie
- **Product** : nom, description, prix, quantite en stock, photo, categorie liee et dates de creation et modification
- **Profile** : etend le modele User avec une photo, une bio, un numero de telephone et une adresse
- **UserHistory** : enregistre chaque action d'un utilisateur (action, description, adresse IP, date)

---

## 4. Systeme de roles et permissions

L'application definit trois niveaux d'acces distincts :

| Profil | Droits accordes |
|---|---|
| Superadmin | CRUD categories, CRUD produits, acces complet a toutes les fonctionnalites |
| Admin | CRUD produits uniquement, pas d'acces a la gestion des categories |
| Utilisateur simple | Consultation des produits, recherche, filtres et tri — aucune modification |

---

## 5. Technologies utilisees

### 5.1 Backend

| Technologie | Version | Role |
|---|---|---|
| Django | 5.2 | Framework web principal |
| Python | 3.11 | Langage de programmation |
| SQLite | 3 | Base de donnees (developpement) |
| SMTP Gmail | - | Envoi des emails d'activation de compte |

### 5.2 Frontend

| Technologie | Version | Role |
|---|---|---|
| Bootstrap | 5.3 | Framework CSS responsive |
| HTML5 | - | Structure des pages web |
| Font Awesome | 6.4 | Icones vectorielles |
| JavaScript | ES6 | Interactions dynamiques cote client |

### 5.3 Fonctionnalites techniques notables

- Authentification Django avec confirmation par email (token unique)
- Systeme de groupes et permissions natif de Django
- Validation cote serveur via les formulaires Django
- Upload et redimensionnement d'images produits et profils
- Pagination des resultats (6 produits par page)
- Recherche multi-criteres avec les objets Q de Django
- Historique complet des actions de chaque utilisateur

---

## 6. Fonctionnalites detaillees

### 6.1 Module Produits

- Creer un produit : nom, description, prix, quantite en stock, photo, categorie
- Modifier un produit existant
- Supprimer un produit
- Consulter la fiche complete d'un produit
- Rechercher par nom ou description
- Filtrer par categorie
- Trier par nom, prix ou stock
- Pagination : 6 produits affiches par page

### 6.2 Module Categories (Superadmin uniquement)

- Creer une categorie
- Modifier une categorie existante
- Supprimer une categorie (uniquement si elle ne contient aucun produit)
- Visualiser le nombre de produits par categorie

### 6.3 Module Utilisateurs

- Inscription avec confirmation par email
- Connexion et deconnexion securisees
- Profil utilisateur avec photo de profil
- Modification des informations personnelles
- Changement de mot de passe
- Historique des actions : recherches, consultations, modifications

---

## 7. Installation et lancement

### 7.1 Prerequis

- Python 3.11 ou superieur installe sur la machine
- pip (gestionnaire de paquets Python)
- Git

### 7.2 Etapes d'installation

**Etape 1 : Cloner le projet**

```bash
git clone https://github.com/votre-repo/gestion_stock.git
cd gestion_stock
```

**Etape 2 : Creer l'environnement virtuel**

```bash
# Windows
python -m venv env
env\Scripts\activate

# Linux / Mac
python3 -m venv env
source env/bin/activate
```

**Etape 3 : Installer les dependances**

```bash
pip install -r requirements.txt
```

**Etape 4 : Configurer la base de donnees**

```bash
python manage.py makemigrations
python manage.py migrate
```

**Etape 5 : Creer un superutilisateur**

```bash
python manage.py createsuperuser
```

**Etape 6 : Creer les groupes d'utilisateurs**

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import Group
Group.objects.get_or_create(name='superadmin')
Group.objects.get_or_create(name='admin')
Group.objects.get_or_create(name='viewer')
exit()
```

**Etape 7 : Configurer l'envoi d'emails (optionnel)**

Dans le fichier `settings.py`, ajouter les parametres SMTP suivants :

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'votre_email@gmail.com'
EMAIL_HOST_PASSWORD = 'votre_mot_de_passe_applicatif'
```

**Etape 8 : Lancer le serveur de developpement**

```bash
python manage.py runserver
```

**Etape 9 : Acceder a l'application**

```
Application principale  : http://127.0.0.1:8000/
Interface d'administration : http://127.0.0.1:8000/admin/
```

---

## 8. Impact et potentiel du projet

### 8.1 Pour l'entreprise

- Reduction estimee de 70 % du temps de gestion d'inventaire
- Elimination des erreurs humaines liees aux fichiers Excel
- Tracabilite complete des actions de chaque utilisateur
- Controle d'acces granulaire par niveaux de roles

### 8.2 Pour l'apprenant

- Maitrise de l'architecture MVT de Django
- Comprehension des relations entre modeles de base de donnees
- Gestion des sessions et de l'authentification
- Integration d'emails transactionnels
- Developpement d'interfaces responsives avec Bootstrap

### 8.3 Pistes d'evolution

- Tableaux de bord statistiques et graphiques d'evolution des ventes
- Gestion des fournisseurs et generation de factures
- API REST pour application mobile
- Alertes automatiques en cas de stock faible (email ou SMS)

---

## 9. Contributeur

**Morsia Guitdam Hinimdou**  
Étudiant en génie de l’intelligence artificielle, des technologies des données et de leurs applications industrielles. | ENSAM-Meknes

| Contact | Information |
|---|---|
| Email | hinimdoumorsia@gmail.com |
| LinkedIn | [LinkedIn](https://www.linkedin.com/in/morsia-guitdam-hinimdou-266bb0269/) |
| WhatsApp | +237 690 124 864 |
| Portfolio | https://site-web-nodemailer.vercel.app |

---

## 10. Remerciements

- Pr Brahim BAKKAS — Encadrement et supervision pedagogique
- ENSAM-Meknes — Pour la formation et les ressources mises a disposition
- Communaute Django — Pour la documentation et le support technique

---

*Ce projet est developpe a des fins pedagogiques dans le cadre de la formation a l'ENSAM-Meknes.*  
*2024 - Application de Gestion de Stock | ENSAM-Meknes | Tous droits reserves*
