# Authentification et gestion des utilisateurs

L’authentification constitue une partie essentielle de l’application de gestion de stock, car elle permet de sécuriser l’accès aux différentes fonctionnalités selon le rôle de chaque utilisateur.

Le système mis en place repose sur le mécanisme d’authentification natif de Django, enrichi par une gestion personnalisée de l’inscription, de l’activation de compte par email, de la connexion et de la déconnexion.

L’objectif principal est de garantir que seuls les utilisateurs autorisés puissent accéder aux ressources sensibles comme l’ajout, la modification ou la suppression des produits.

---

## Fonctionnalités principales de l’authentification

Le module d’authentification comprend plusieurs fonctionnalités importantes :

- création de compte utilisateur (inscription)
- activation du compte par email
- connexion sécurisée
- déconnexion
- restriction d’accès aux pages sensibles
- gestion des rôles et permissions
- protection des vues avec `@login_required`
- contrôle d’accès avec `@user_passes_test`

Cette organisation permet de séparer les simples utilisateurs des administrateurs ayant les droits de gestion.

---

## Processus général d’authentification

Le fonctionnement global suit le cycle suivant :

1. L’utilisateur crée un compte via la page d’inscription  
2. Un email d’activation est envoyé automatiquement  
3. L’utilisateur clique sur le lien reçu  
4. Le compte est activé dans la base de données  
5. L’utilisateur peut ensuite se connecter  
6. Django vérifie les identifiants  
7. Selon son rôle, il accède aux fonctionnalités autorisées

Ce processus garantit une meilleure sécurité et évite la création de faux comptes ou d’utilisateurs non vérifiés.

---

## Interfaces utilisateur concernées

Le système d’authentification repose principalement sur trois interfaces :

### Page d’inscription

Cette page permet à un nouvel utilisateur de créer son compte en renseignant ses informations personnelles nécessaires.

### Page de connexion

Elle permet à l’utilisateur authentifié d’accéder à son espace sécurisé après vérification de son nom d’utilisateur et de son mot de passe.

### Page de déconnexion

Elle informe l’utilisateur que sa session a bien été fermée et lui propose de se reconnecter si nécessaire.

---

## Activation par email

Après l’inscription, un email automatique est envoyé à l’utilisateur contenant un lien unique d’activation.

Cette étape permet :

- de vérifier l’existence réelle de l’adresse email
- de renforcer la sécurité du système
- d’éviter les inscriptions frauduleuses
- de garantir une meilleure gestion des utilisateurs

Le compte reste inactif tant que cette étape n’est pas validée.

---

## Sécurisation des accès

Certaines fonctionnalités comme :

- l’ajout de produits
- la modification
- la suppression
- l’administration générale

ne sont accessibles qu’aux utilisateurs autorisés.

Pour cela, Django utilise :

- `@login_required` pour vérifier que l’utilisateur est connecté
- `@user_passes_test()` pour vérifier son rôle (administrateur ou non)

Cela permet d’assurer une gestion stricte des permissions dans l’application.

---


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
    <img src="docs/images/datacamp.jpg" width="22"/>
    DataCamp
  </a>

  <a href="https://www.kaggle.com/morsiahinimdou" target="_blank" style="display:flex; align-items:center; gap:8px; text-decoration:none;">
    <img src="docs/images/kaggleImg.png" width="22"/>
    Kaggle
  </a>

</div>