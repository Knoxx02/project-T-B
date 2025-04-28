from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem, Order, OrderItem
from shop.models import Product
from .forms import OrderCreateForm


def _get_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.save()
            session_key = request.session.session_key
        
        cart, created = Cart.objects.get_or_create(session_id=session_key)
    
    return cart


def cart_detail(request):
    cart = _get_cart(request)
    cart_items = cart.items.all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'cart/cart_detail.html', context)


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = _get_cart(request)
    
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        CartItem.objects.create(cart=cart, product=product, quantity=1)
    
    messages.success(request, f"{product.name} added to your cart.")
    return redirect('cart_detail')


def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    product_name = cart_item.product.name
    cart_item.delete()
    
    messages.success(request, f"{product_name} removed from your cart.")
    return redirect('cart_detail')


def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
    
    return redirect('cart_detail')


@login_required
def checkout(request):
    cart = _get_cart(request)
    cart_items = cart.items.all()
    
    if not cart_items:
        messages.warning(request, "Your cart is empty. Add some products first.")
        return redirect('product_list')
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            
            for item in cart_items:
                if item.product.sale_price:
                    price = item.product.sale_price
                else:
                    price = item.product.price
                
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=price,
                    quantity=item.quantity
                )
            
            # Clear the user's cart
            cart_items.delete()
            
            messages.success(request, "Your order has been placed successfully.")
            return redirect('order_complete', order_id=order.id)
    else:
        # Pre-fill the form with user's information
        initial_data = {}
        if hasattr(request.user, 'profile'):
            initial_data = {
                'full_name': f"{request.user.first_name} {request.user.last_name}",
                'email': request.user.email,
                'phone': request.user.profile.phone,
                'address': request.user.profile.address,
            }
        form = OrderCreateForm(initial=initial_data)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'form': form,
    }
    return render(request, 'cart/checkout.html', context)


@login_required
def order_complete(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'cart/order_complete.html', context)


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'cart/order_history.html', context)