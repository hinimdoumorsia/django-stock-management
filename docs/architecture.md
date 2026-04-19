# <span style="color:blue;"> Architecture du projet</span>


## Schéma de l’architecture

Voici la structure globale du projet Django :

<img src="/images/architectureproject.png" alt="Architecture du projet" style="width:100%; max-width:900px; border-radius:10px;"/>


<p style="margin-top:10px;">
⚠️ <b>Remarque importante :</b> Cette architecture représente la structure initiale du projet.  
Au fil du développement, de nouveaux fichiers et modules ont été ajoutés afin de répondre à des besoins non prévus dans le cahier des charges initial.  
Cependant, l’essentiel du système reste basé sur cette organisation, qui reflète la logique principale de l’application.
</p>


## <b>Modélisation du système</b>

### <span style="color:blue;">Pourquoi modéliser avant de coder ?</span>

La modélisation permet de transformer un besoin fonctionnel en une structure claire et organisée avant le développement.

Elle aide à identifier :

- les acteurs du système  
- les objets métiers  
- les relations entre les entités  
- les flux d’information  
- les responsabilités techniques  

Elle permet de réduire les erreurs de conception avant l’écriture du code et facilite la communication entre enseignants, apprenants et développeurs.

---

### <span style="color:red;">À retenir</span>

Dans ce projet, la modélisation est comprise à trois niveaux :

- <span style="color:red;">Fonctionnel : qui fait quoi ?</span>  
- <span style="color:red;">Structurel : quelles données sont manipulées ?</span>  
- <span style="color:red;">Technique : comment Django organise l’application ?</span>  


---


## <span style="color:blue;"> Vue d’ensemble du système</span>

| Élément | Description |
|----------|-------------|
| **Superadmin** | gère les catégories, les produits et le paramétrage global |
| **Admin** | gère uniquement les produits |
| **Utilisateur simple** | consulte, recherche, filtre et trie les produits |
| **Category** | organise les produits par famille ou type |
| **Product** | contient les informations métier de l’article |
| **Application Django** | traite les requêtes, applique les règles et affiche les résultats |

---

##  Bonnes pratiques

Le noyau du projet repose sur deux entités principales (**Category** et **Product**) avec des droits différents selon le profil utilisateur.


## <span style="color:purple;">Diagramme de cas d’utilisation</span>

### Principe

Le diagramme de cas d’utilisation décrit les services rendus par le système du point de vue des utilisateurs.  
Il permet de répondre à la question suivante :

**Quelles actions chaque acteur peut-il réaliser dans le système ?**

---

## Objectif

Ce diagramme est particulièrement utile pour distinguer les différents niveaux d’accès et de permissions :

- Super Admin  
- Admin  
- Utilisateur simple  

---

## Comparaison

Contrairement au diagramme de classes qui se concentre sur la structure des données et les relations entre objets,  
le diagramme de cas d’utilisation met l’accent sur les fonctionnalités offertes par le système et les interactions avec les utilisateurs.

---

## Diagramme de cas d’utilisation

Voici la représentation graphique du fonctionnement global du système :

<img src="/images/usecase.PNG" alt="Diagramme de cas d’utilisation" style="width:100%; max-width:900px; border-radius:10px;"/>

---

### Resumé

Ce diagramme permet de mieux comprendre les rôles des utilisateurs ainsi que les services accessibles à chacun,  
ce qui facilite la conception des droits d’accès et la sécurité du système.


## <span style="color:blue;">Diagramme de flux</span>

### Principe

Le diagramme de flux décrit l’enchaînement des étapes dans le système.  
Il permet de visualiser le fonctionnement global de l’application de manière séquentielle.

Il montre principalement :

- les entrées  
- les décisions  
- les traitements  
- les sorties  

---

## Utilité

Ce diagramme est utile pour comprendre le comportement global du système et la logique de traitement des données à travers les différentes étapes de l’application.

---

## Diagramme de flux

Voici la représentation graphique du flux de fonctionnement du système :

<img src="/images/fluxDiag.PNG" alt="Diagramme de flux" style="width:100%; max-width:900px; border-radius:10px;"/>

---

### Resumé

Le diagramme de flux permet de mieux comprendre l’enchaînement des opérations dans le système et la logique globale de traitement des données.


## <span style="color:blue;">Lecture pédagogique du diagramme de flux</span>

### Lecture du diagramme

Toute interaction commence par l’identification de l’utilisateur.  
Le système applique ensuite une décision basée sur le rôle de l’utilisateur.

Les traitements autorisés conduisent à des opérations de lecture ou d’écriture en base de données.  
Le résultat final est ensuite affiché sous forme de pages HTML.

---

## Bonnes pratiques

Le diagramme de flux permet de préparer la compréhension de l’architecture logique de l’application.  
Il facilite notamment la transition vers l’implémentation des vues Django et du routage des requêtes.

---

## Resumé

Cette modélisation aide à comprendre le comportement dynamique du système et constitue une base importante pour la conception de l’application web.

## <span style="color:blue;">Diagramme de classes UML</span>

### Principe

Le diagramme de classes décrit la structure statique du système.  
Il permet de représenter l’organisation des données et des objets du projet.

Il présente principalement :

- les classes  
- leurs attributs  
- les relations entre les classes  

---

## Classes principales du projet

Dans ce projet, les classes principales sont :

- User  
- Category  
- Product  

---

## Diagramme de classes UML

Voici la représentation graphique du diagramme de classes :

<img src="/images/umlDiag.PNG" alt="Diagramme de classes UML" style="width:100%; max-width:900px; border-radius:10px;"/>

---

### Resumé

Ce diagramme permet de comprendre la structure interne du système ainsi que les relations entre les principales entités du projet.


## <span style="color:blue;">Interprétation du diagramme de classes</span>

### Analyse des relations

Le diagramme de classes met en évidence les relations suivantes :

- Une catégorie peut contenir plusieurs produits.  
- Chaque produit appartient à une seule catégorie.  
- Les utilisateurs interagissent avec les produits selon leur rôle dans le système.  
- Les catégories sont gérées uniquement par le superadmin.  

---

## Mise en pratique (Django)

Dans l’implémentation Django, la relation entre les produits et les catégories est modélisée à l’aide d’une clé étrangère :

```python
category = models.ForeignKey(Category, on_delete=models.CASCADE)



## <span style="color:blue;">Passage UML vers Django</span>

### Correspondance entre UML et Django

| Concept UML        | Traduction dans Django                          |
|-------------------|------------------------------------------------|
| Classe            | Modèle dans `models.py`                        |
| Attribut          | Champ Django (`CharField`, `DecimalField`, etc.) |
| Association 1..N  | `ForeignKey`                                   |
| Acteur            | Utilisateur authentifié                        |
| Rôle / Action     | Groupes Django ou permissions                  |
| Action utilisateur| Vue associée à une URL                         |

---

### Exemple concret

En UML, une relation entre **Category** et **Product** (1..N) devient en Django :

```python
category = models.ForeignKey(Category, on_delete=models.CASCADE)


## <span style="color:blue;">Diagramme de séquence</span>

### Principe

Le diagramme de séquence décrit le déroulement temporel d’une opération dans le système.  
Il met en évidence l’ordre dans lequel les objets interagissent au cours d’un scénario précis.

Il permet de répondre à la question suivante :

**Dans quel ordre les objets interagissent-ils ?**

---

## Cas d’utilisation typiques

Ce diagramme est particulièrement utile pour illustrer des opérations concrètes telles que :

- ajouter un produit  
- modifier un produit  
- consulter la liste des produits  

---

## Diagramme de séquence

Voici la représentation graphique du déroulement des interactions :

<img src="/images/seqDiag.PNG" alt="Diagramme de séquence" style="width:100%; max-width:900px; border-radius:10px;"/>

---

## Resumé

Le diagramme de séquence permet de comprendre le comportement dynamique du système en illustrant clairement l’ordre des échanges entre les différents composants.


## <span style="color:blue;">Lecture du diagramme de séquence</span>

### Déroulement des interactions

Le diagramme de séquence décrit les étapes suivantes :

- L’utilisateur remplit le formulaire.  
- Le template envoie les données à la vue.  
- La vue valide les données et appelle le modèle.  
- Le modèle enregistre le produit dans la base de données.  
- La vue renvoie un message et effectue une redirection.  
- L’utilisateur obtient la nouvelle page affichant le résultat.

---

## Comparaison

Le diagramme de séquence complète le diagramme de classes :

- Le diagramme de classes décrit la structure statique du système.  
- Le diagramme de séquence décrit le comportement dynamique et le déroulement des opérations dans le temps.

---

### Resumé

Ainsi, le diagramme de séquence permet de comprendre comment les différentes couches du système interagissent lors de l’exécution d’une fonctionnalité dans l’application.


## <span style="color:blue;">Architecture MVT dans Django</span>

### Principe

Django repose sur l’architecture MVT (Model – View – Template) :

- **Model** : représente la structure des données et les règles métier.  
- **View** : contient la logique de traitement et la gestion des requêtes.  
- **Template** : représente l’interface utilisateur en HTML.  

---

## Avantages de l’architecture MVT

Cette séparation permet d’améliorer plusieurs aspects du projet :

- la lisibilité du code  
- la maintenance de l’application  
- la réutilisabilité des composants  
- l’évolution future du système  

## Schéma de l’architecture MVT

<img src="/images/mvt.png" alt="Architecture MVT Django" style="width:100%; max-width:900px; border-radius:10px;"/>

---

## À retenir

L’architecture MVT est très proche du modèle MVC, mais adaptée au fonctionnement interne de Django.  
Elle permet une organisation claire et structurée du développement web.

---

## Schéma de l’architecture MVT

Voici la représentation graphique de l’architecture MVT Dans notre cas pour ce present projet :

<img src="/images/MVTarch.PNG" alt="Architecture MVT Django" style="width:100%; max-width:900px; border-radius:10px;"/>


## Exemple MVT – Suppression d’un produit

| Composant MVT | Rôle dans la suppression |
|--------------|--------------------------|
| Model | Représente le produit à supprimer (Product) |
| View | Récupère l’objet et exécute la suppression |
| Template | Affiche une page de confirmation |
| URL | Relie `/products/delete/<id>/` à la vue |

### Bonnes pratiques
- <span style="color:blue">Vérifier que l’utilisateur a les droits nécessaires</span>  
- <span style="color:blue">Demander confirmation avant suppression</span>  
- Rediriger vers la liste après suppression  

---

## Exemple MVT – Mise à jour d’un produit

| Composant MVT | Rôle dans la mise à jour |
|--------------|--------------------------|
| Model | Produit existant à modifier |
| View | Charge les données, valide et sauvegarde |
| Template | Formulaire pré-rempli |
| URL | `/products/edit/<id>/` |

### Étapes du processus
1. L’utilisateur ouvre la page d’édition  
2. La vue charge les données du produit  
3. <span style="color:blue">Le formulaire est affiché avec les anciennes valeurs</span>  
4. L’utilisateur modifie et soumet  
5. <span style="color:blue">La vue valide et met à jour la base de données</span>  

---

## Synthèse du cycle CRUD dans MVT

| Opération | Vue principale | Résultat |
|-----------|---------------|----------|
| Create | add_product | Ajout d’un produit |
| Read | product_list | Affichage des produits |
| Update | edit_product | Modification |
| Delete | delete_product | Suppression |

---

## Avantage de l’architecture MVT

L’architecture MVT de Django permet :

- Une séparation claire des responsabilités  
- Une meilleure organisation du code
- Une maintenance simplifiée  
- Une évolution facile du projet  
- Une réutilisation des composants  

---

## Conclusion générale de la partie MVT

À retenir :

- <span style="color:blue">Le Model gère les données</span>  
- <span style="color:blue">La View gère la logique</span>  
- <span style="color:blue">Le Template gère l’affichage</span>  
- <span style="color:blue">L’URL connecte l’utilisateur au système</span> 

L’ensemble forme une architecture cohérente qui rend le développement web structuré, lisible et scalable.



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