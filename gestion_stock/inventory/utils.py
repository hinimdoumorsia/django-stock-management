from .models import UserHistory

def add_history(user, action, description='', request=None):
    """Ajoute une entrée dans l'historique utilisateur"""
    ip_address = None
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
    
    UserHistory.objects.create(
        user=user,
        action=action,
        description=description,
        ip_address=ip_address
    )