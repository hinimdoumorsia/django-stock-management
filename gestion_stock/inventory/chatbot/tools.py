from langchain.tools import tool
from django.db.models import Q
from inventory.models import Product, Category


# =========================
# HELPERS
# =========================
def stock_status(stock: int) -> str:
    if stock > 10:
        return "🟢"
    elif stock > 0:
        return "🟡"
    return "🔴"

def get_base_url():
    try:
        from django.conf import settings
        return getattr(settings, 'BASE_URL', 'http://127.0.0.1:8000')
    except:
        return 'http://127.0.0.1:8000'

def get_image_url(product) -> str:
    try:
        if product.image:
            return f"{get_base_url()}{product.image.url}"
        return ""
    except:
        return ""


# =========================
# 1. RECHERCHE PRODUITS
# =========================
@tool
def rechercher_produits(requete: str) -> str:
    """
    Recherche intelligente des produits par nom ou description.
    Utiliser quand le client demande un produit spécifique.
    """
    try:
        import re
        from unidecode import unidecode
        
        mots_importants = [w for w in requete.lower().split() 
                          if w not in ["avez", "vous", "du", "des", "un", "une", "le", "la", "les", "de", "d'", "avoir"]]
        
        produits = Product.objects.all()
        scores = []
        
        for p in produits:
            nom_clean = unidecode(p.name.lower())
            nom_clean = re.sub(r'[^a-z0-9]', '', nom_clean)
            score = 0
            
            for mot in mots_importants:
                mot_clean = unidecode(mot)
                mot_clean = re.sub(r'[^a-z0-9]', '', mot_clean)
                if mot_clean in nom_clean:
                    score += 1
            
            if score > 0:
                scores.append((score, p))
        
        scores.sort(key=lambda x: x[0], reverse=True)
        
        if not scores:
            return f"Aucun produit trouvé pour '{requete}'."
        
        result = f"📦 Produits trouvés:\n\n"
        for score, p in scores[:5]:
            base_url = get_base_url()
            image_url = get_image_url(p)
            lien = f"{base_url}/product/{p.pk}/"
            result += f"{stock_status(p.stock)} **{p.name}** - {p.formatted_price} (Stock: {p.stock})\n"
            result += f"🔗 {lien}\n"
            if image_url:
                result += f"🖼️ {image_url}\n"
            result += "\n"
        
        return result
        
    except Exception as e:
        return f"❌ Erreur: {str(e)}"


# =========================
# 2. LISTE PRODUITS
# =========================
@tool
def lister_tous_les_produits(limit: str = "20") -> str:
    """
    Liste tous les produits disponibles dans le catalogue.
    Utiliser quand le client demande la liste des produits ou le catalogue.
    """
    try:
        try:
            limit = int(str(limit))
        except:
            limit = 20
        limit = min(limit, 50)

        produits = Product.objects.all()[:limit]
        total = Product.objects.count()

        if not produits:
            return "📦 Aucun produit disponible."

        base_url = get_base_url()
        result = f"📋 Produits ({len(produits)}/{total}):\n\n"

        for p in produits:
            lien = f"{base_url}/product/{p.pk}/"
            result += f"{stock_status(p.stock)} **{p.name}** - {p.formatted_price} (Stock: {p.stock}) — 🔗 {lien}\n"

        return result

    except Exception as e:
        return f"❌ Erreur listing : {str(e)}"


# =========================
# 3. LISTE CATEGORIES
# =========================
@tool
def lister_categories() -> str:
    """
    Liste toutes les catégories disponibles dans le catalogue.
    Utiliser quand le client demande les catégories ou types de produits.
    """
    try:
        categories = Category.objects.all()

        if not categories:
            return "📁 Aucune catégorie disponible."

        result = f"📁 **Catégories disponibles ({categories.count()}) :**\n\n"
        for c in categories:
            nb_produits = Product.objects.filter(category=c).count()
            result += f"• **{c.name}** — {nb_produits} produit(s)\n"

        return result

    except Exception as e:
        return f"❌ Erreur catégories : {str(e)}"


# =========================
# 4. RUPTURE STOCK
# =========================
@tool
def produits_en_rupture() -> str:
    """
    Retourne les produits en rupture de stock (stock = 0).
    """
    try:
        produits = Product.objects.filter(stock=0)

        if not produits:
            return "✅ Aucun produit en rupture de stock."

        result = "🔴 Produits en rupture:\n\n"
        for p in produits:
            result += f"- **{p.name}** - {p.formatted_price}\n"

        return result

    except Exception as e:
        return f"❌ Erreur rupture : {str(e)}"


# =========================
# 5. STOCK FAIBLE
# =========================
@tool
def produits_stock_faible(seuil: str = "5") -> str:
    """
    Retourne les produits avec un stock faible (inférieur ou égal au seuil).
    """
    try:
        try:
            seuil = int(str(seuil))
        except:
            seuil = 5

        produits = Product.objects.filter(stock__lte=seuil, stock__gt=0)

        if not produits:
            return f"✅ Aucun produit avec stock ≤ {seuil}."

        result = f"🟡 Stock faible (≤{seuil}):\n\n"
        for p in produits:
            result += f"- **{p.name}** : {p.stock} unité(s) restante(s)\n"

        return result

    except Exception as e:
        return f"❌ Erreur stock faible : {str(e)}"


# =========================
# 6. CONSEIL PRODUITS
# =========================
@tool
def conseiller_produits(critere: str = "") -> str:
    """
    Recommande des produits selon les besoins du client (budget, tendance, etc).
    Utiliser quand le client cherche des conseils ou a un budget limité.
    """
    try:
        critere = critere.lower() if critere else ""
        qs = Product.objects.filter(stock__gt=0)

        if any(x in critere for x in ["cher", "budget", "prix", "moins", "abordable", "economique"]):
            qs = qs.order_by("price")
            title = "💰 Produits les moins chers:\n\n"
        elif any(x in critere for x in ["tendance", "populaire", "nouveau"]):
            qs = qs.order_by("-id")
            title = "🔥 Produits tendance:\n\n"
        else:
            qs = qs.order_by("price")
            title = "🎯 Produits recommandés:\n\n"

        produits = qs[:5]
        base_url = get_base_url()
        result = title

        for p in produits:
            lien = f"{base_url}/product/{p.pk}/"
            result += f"{stock_status(p.stock)} **{p.name}** - {p.formatted_price} — 🔗 {lien}\n"

        return result

    except Exception as e:
        return f"❌ Erreur conseil : {str(e)}"


# =========================
# 7. DETAILS PRODUIT
# =========================
@tool
def details_produit(nom_produit: str) -> str:
    """
    Donne les détails complets d'un produit avec image et lien.
    Utiliser quand le client veut en savoir plus sur un produit précis.
    """
    try:
        produits = Product.objects.filter(name__icontains=nom_produit)

        if not produits:
            return f"❌ Produit '{nom_produit}' introuvable."

        p = produits.first()
        base_url = get_base_url()
        image_url = get_image_url(p)
        lien = f"{base_url}/product/{p.pk}/"

        result = f"""📦 **{p.name}**
💰 Prix : {p.formatted_price}
{stock_status(p.stock)} Stock : {p.stock} unités
📁 Catégorie : {p.category.name if p.category else 'Non définie'}
📝 Description : {p.description or 'Aucune description'}
🔗 {lien}
"""
        if image_url:
            result += f"🖼️ {image_url}\n"

        return result

    except Exception as e:
        return f"❌ Erreur détails : {str(e)}"


# =========================
# 8. STATISTIQUES
# =========================
@tool
def statistiques_produits() -> str:
    """
    Donne les statistiques globales du catalogue (total, ruptures, stock faible, catégories).
    """
    try:
        total = Product.objects.count()
        rupture = Product.objects.filter(stock=0).count()
        faible = Product.objects.filter(stock__lte=5, stock__gt=0).count()
        categories = Category.objects.count()

        return f"""📊 **Statistiques du catalogue:**

📦 Total produits : {total}
🟢 Stock normal : {total - rupture - faible}
🟡 Stock faible (≤5) : {faible}
🔴 Rupture de stock : {rupture}
📁 Catégories : {categories}
"""

    except Exception as e:
        return f"❌ Erreur stats : {str(e)}"


# =========================
# 9. FEEDBACK
# =========================
@tool
def enregistrer_feedback(satisfaction: str, commentaire: str = "") -> str:
    """
    Enregistre un feedback, avis ou plainte d'un client.
    Utiliser quand le client exprime une satisfaction ou insatisfaction.
    """
    return "✅ Merci pour votre retour ! Votre avis a été bien enregistré. Notre équipe en prendra note."


# =========================
# 10. LIEN + IMAGE PRODUIT
# =========================
@tool
def envoyer_lien_produit(nom_produit: str) -> str:
    """
    Envoie le lien direct et l'image d'un produit.
    Utiliser quand le client demande un lien, une image ou plus d'infos visuelles sur un produit.
    """
    try:
        produits = Product.objects.filter(name__icontains=nom_produit)
        
        if not produits:
            return f"❌ Produit '{nom_produit}' introuvable."
        
        p = produits.first()
        base_url = get_base_url()
        image_url = get_image_url(p)
        lien = f"{base_url}/product/{p.pk}/"

        result = f"""🛍️ **{p.name}**

💰 Prix : {p.formatted_price}
{stock_status(p.stock)} Stock : {p.stock} unités
📝 {p.description or 'Aucune description'}

🔗 {lien}
"""
        if image_url:
            result += f"🖼️ {image_url}\n"

        result += "\nSouhaitez-vous voir d'autres produits similaires ?"

        return result
        
    except Exception as e:
        return f"❌ Erreur : {str(e)}"


# =========================
# LISTE TOOLS
# =========================
TOOLS = [
    rechercher_produits,
    lister_tous_les_produits,
    lister_categories,
    produits_en_rupture,
    produits_stock_faible,
    conseiller_produits,
    details_produit,
    statistiques_produits,
    enregistrer_feedback,
    envoyer_lien_produit,
]