from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.forms import PasswordChangeForm
from django.db import models

from .models import Category, Product, UserHistory, Profile, ChatConversation
from .forms import CategoryForm, ProductForm, UserRegistrationForm, UserProfileForm, ProfileForm
from .tokens import account_activation_token
from .utils import add_history

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from django.http import JsonResponse

from .chatbot.agent import get_bot_response 

# ============ Fonctions utilitaires pour les rôles ============
def is_superadmin(user):
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name='superadmin').exists())

def is_admin(user):
    return user.is_authenticated and (user.groups.filter(name='admin').exists() or user.is_superuser)

def is_viewer(user):
    return user.is_authenticated

# ============ Vue d'inscription ============
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            
            Profile.objects.get_or_create(user=user)
            viewer_group, created = Group.objects.get_or_create(name='viewer')
            user.groups.add(viewer_group)
            
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            
            subject = 'Activez votre compte - Gestion de Stock'
            message = f"""
Bonjour {user.username},

Merci de vous être inscrit sur notre application de gestion de stock.

Pour activer votre compte, veuillez cliquer sur le lien ci-dessous :

http://127.0.0.1:8000/activate/{uid}/{token}/

Ce lien expirera automatiquement.

---
© 2024 - Application de Gestion de Stock | ENSAM-Meknès
"""
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
            
            messages.success(request, 'Un email de confirmation vous a été envoyé. Vérifiez votre boîte mail.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'inventory/registration/register.html', {'form': form})

# ============ Vue d'activation du compte ============
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        add_history(user, 'login', 'Compte activé avec succès', request)
        messages.success(request, 'Votre compte a été activé avec succès ! Vous pouvez maintenant vous connecter.')
        return redirect('login')
    else:
        messages.error(request, "Lien d'activation invalide ou expiré.")
        return redirect('register')

# ============ Profil utilisateur ============
@login_required
def user_profile(request):
    return render(request, 'inventory/user_profile.html', {
        'user': request.user,
        'is_superadmin': is_superadmin(request.user),
        'is_admin': is_admin(request.user),
    })

@login_required
def user_profile_edit(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            add_history(request.user, 'update', 'Profil utilisateur modifié', request)
            messages.success(request, 'Votre profil a été modifié avec succès!')
            return redirect('user_profile')
    else:
        user_form = UserProfileForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)
    
    return render(request, 'inventory/user_profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'is_superadmin': is_superadmin(request.user),
        'is_admin': is_admin(request.user),
    })

@login_required
def user_change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            add_history(request.user, 'update', 'Mot de passe modifié', request)
            messages.success(request, 'Votre mot de passe a été modifié avec succès!')
            return redirect('user_profile')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'inventory/user_change_password.html', {
        'form': form,
        'is_superadmin': is_superadmin(request.user),
        'is_admin': is_admin(request.user),
    })

@login_required
def user_history(request):
    history_list = UserHistory.objects.filter(user=request.user)
    
    action_filter = request.GET.get('action', '')
    if action_filter:
        history_list = history_list.filter(action=action_filter)
    
    paginator = Paginator(history_list, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'inventory/user_history.html', {
        'page_obj': page_obj,
        'action_filter': action_filter,
        'action_choices': UserHistory.ACTION_TYPES,
        'is_superadmin': is_superadmin(request.user),
        'is_admin': is_admin(request.user),
    })

# ============ Vues des produits ============
@login_required
def product_list(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    sort = request.GET.get('sort', 'name')

    products = Product.objects.select_related('category').all()

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
        add_history(request.user, 'search', f'Recherche: {query}', request)

    if category_id and category_id.isdigit():
        products = products.filter(category_id=int(category_id))
        add_history(request.user, 'filter', f'Filtre par catégorie ID: {category_id}', request)

    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'stock_asc':
        products = products.order_by('stock')
    elif sort == 'stock_desc':
        products = products.order_by('-stock')
    else:
        products = products.order_by('name')

    paginator = Paginator(products, 6)
    page_obj = paginator.get_page(request.GET.get('page'))
    categories = Category.objects.all()

    return render(request, 'inventory/product_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'category_id': category_id if category_id else '',
        'sort': sort,
        'is_superadmin': is_superadmin(request.user),
        'is_admin': is_admin(request.user),
    })

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    add_history(request.user, 'view', f'Consultation du produit: {product.name}', request)
    return render(request, 'inventory/product_detail.html', {
        'product': product,
        'is_superadmin': is_superadmin(request.user),
        'is_admin': is_admin(request.user),
    })

@login_required
@user_passes_test(is_admin)
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            add_history(request.user, 'create', f'Création du produit: {product.name}', request)
            messages.success(request, f'Produit "{product.name}" créé avec succès!')
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm()
    return render(request, 'inventory/product_form.html', {
        'form': form,
        'title': 'Ajouter un produit',
        'is_superadmin': is_superadmin(request.user),
        'is_admin': is_admin(request.user),
    })

@login_required
@user_passes_test(is_admin)
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            add_history(request.user, 'update', f'Modification du produit: {product.name}', request)
            messages.success(request, f'Produit "{product.name}" modifié avec succès!')
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    return render(request, 'inventory/product_form.html', {
        'form': form,
        'title': 'Modifier le produit',
        'is_superadmin': is_superadmin(request.user),
        'is_admin': is_admin(request.user),
    })

@login_required
@user_passes_test(is_admin)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        add_history(request.user, 'delete', f'Suppression du produit: {product_name}', request)
        messages.success(request, f'Produit "{product_name}" supprimé avec succès!')
        return redirect('product_list')
    return render(request, 'inventory/product_confirm_delete.html', {
        'product': product,
        'is_superadmin': is_superadmin(request.user),
        'is_admin': is_admin(request.user),
    })

# ============ Vues des catégories ============
@login_required
@user_passes_test(is_superadmin)
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'inventory/category_list.html', {
        'categories': categories,
        'is_superadmin': is_superadmin(request.user),
        'is_admin': is_admin(request.user),
    })

@login_required
@user_passes_test(is_superadmin)
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            add_history(request.user, 'create', f'Création de la catégorie: {category.name}', request)
            messages.success(request, f'Catégorie "{category.name}" créée avec succès!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'inventory/category_form.html', {
        'form': form,
        'title': 'Ajouter une catégorie',
        'is_superadmin': is_superadmin(request.user),
        'is_admin': is_admin(request.user),
    })

@login_required
@user_passes_test(is_superadmin)
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            add_history(request.user, 'update', f'Modification de la catégorie: {category.name}', request)
            messages.success(request, f'Catégorie "{category.name}" modifiée avec succès!')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'inventory/category_form.html', {
        'form': form,
        'title': 'Modifier la catégorie',
        'is_superadmin': is_superadmin(request.user),
        'is_admin': is_admin(request.user),
    })

@login_required
@user_passes_test(is_superadmin)
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if category.product_set.count() > 0:
        messages.error(request, f'Impossible de supprimer "{category.name}" car elle contient encore {category.product_set.count()} produit(s)!')
        return redirect('category_list')
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        add_history(request.user, 'delete', f'Suppression de la catégorie: {category_name}', request)
        messages.success(request, f'Catégorie "{category_name}" supprimée avec succès!')
        return redirect('category_list')
    return render(request, 'inventory/category_confirm_delete.html', {
        'category': category,
        'is_superadmin': is_superadmin(request.user),
        'is_admin': is_admin(request.user),
    })

# ============ Chatbot API ============
@csrf_exempt
@require_POST
def chatbot_api(request):
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()

        if not message:
            return JsonResponse({'response': 'Message vide.'}, status=400)

        # ✅ Session ID unique par utilisateur
        if not request.session.session_key:
            request.session.create()
        session_id = request.session.session_key

        # ✅ Envoyer UNIQUEMENT le message de l'utilisateur
        # L'historique est géré par LangGraph MemorySaver automatiquement
        response_text = get_bot_response(message, session_id)

        # ✅ Sauvegarder l'échange en base pour historique admin
        try:
            ChatConversation.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_id=session_id,
                message=message,
                response=response_text[:2000],
                is_feedback=False
            )
        except Exception:
            pass  # Ne pas bloquer si la sauvegarde échoue

        return JsonResponse({'response': response_text})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'response': f"❌ Erreur technique: {str(e)}"}, status=500)