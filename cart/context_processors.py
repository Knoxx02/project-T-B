from .models import Cart


def cart_count(request):
    count = 0
    
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            count = cart.items.count()
        except Cart.DoesNotExist:
            pass
    else:
        session_key = request.session.session_key
        if session_key:
            try:
                cart = Cart.objects.get(session_id=session_key)
                count = cart.items.count()
            except Cart.DoesNotExist:
                pass
    
    return {'cart_count': count}