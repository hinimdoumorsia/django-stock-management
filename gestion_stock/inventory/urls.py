from django.urls import path
from . import views

urlpatterns = [
    # Authentification
    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    
    # Profil utilisateur
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/edit/', views.user_profile_edit, name='user_profile_edit'),
    path('profile/change-password/', views.user_change_password, name='user_change_password'),
    path('profile/history/', views.user_history, name='user_history'),
    
    # Produits
    path('', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/add/', views.product_create, name='product_create'),
    path('product/<int:pk>/edit/', views.product_update, name='product_update'),
    path('product/<int:pk>/delete/', views.product_delete, name='product_delete'),

    # Catégories (superadmin uniquement)
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
]