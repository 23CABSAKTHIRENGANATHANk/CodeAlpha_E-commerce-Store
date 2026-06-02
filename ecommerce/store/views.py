from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
import json

from .models import Product, Order, OrderItem, Category, Wishlist
from .forms import RegisterForm, LoginForm, CheckoutForm, ProductSearchForm

User = get_user_model()


# Home page - Product Listings
def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    search_form = ProductSearchForm(request.GET)
    current_category = None
    
    # Search functionality
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search')
        category_query = search_form.cleaned_data.get('category')
        
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
        
        if category_query:
            current_category = category_query
            products = products.filter(category__name__icontains=category_query)
    
    # User's wishlist products mapping for heart highlights
    wishlist_products = []
    if request.user.is_authenticated:
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        wishlist_products = wishlist.products.values_list('id', flat=True)
    
    context = {
        'products': products,
        'categories': categories,
        'search_form': search_form,
        'current_category': current_category,
        'wishlist_products': wishlist_products,
    }
    return render(request, 'store/home.html', context)



# Product Details Page
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    related_products = Product.objects.filter(category=product.category).exclude(id=product_id)[:4]
    
    # Query wishlist items for active toggle rendering
    wishlist_products = []
    if request.user.is_authenticated:
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        wishlist_products = wishlist.products.values_list('id', flat=True)
        
    context = {
        'product': product,
        'related_products': related_products,
        'wishlist_products': wishlist_products,
    }
    return render(request, 'store/product_detail.html', context)



# Register Page
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create wishlist for new user
            Wishlist.objects.create(user=user)
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegisterForm()
    
    context = {'form': form}
    return render(request, 'store/register.html', context)


# Login Page
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is None:
                matching_users = User.objects.filter(
                    Q(username__iexact=username) | Q(email__iexact=username)
                )
                if matching_users.count() == 1:
                    user = authenticate(request, username=matching_users.first().username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect(request.GET.get('next', 'home'))
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    context = {'form': form}
    return render(request, 'store/login.html', context)


# Logout
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


# Cart Page
def cart(request):
    cart_items = request.session.get('cart', {})
    products = []
    total_price = 0
    
    for product_id, quantity in cart_items.items():
        product = get_object_or_404(Product, id=int(product_id))
        item_total = product.price * quantity
        products.append({
            'product': product,
            'quantity': quantity,
            'total': item_total
        })
        total_price += item_total
    
    context = {
        'cart_items': products,
        'total_price': total_price,
        'cart_count': sum(cart_items.values()),
    }
    return render(request, 'store/cart.html', context)


# Add to Cart (AJAX)
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if product.stock <= 0:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'This product is out of stock.'})
        messages.error(request, 'This product is out of stock.')
        return redirect('product_detail', product_id=product_id)

    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    current_quantity = cart.get(product_id_str, 0)

    if current_quantity >= product.stock:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'You have reached the maximum stock available.'})
        messages.error(request, 'You have reached the maximum stock available for this product.')
        return redirect('product_detail', product_id=product_id)

    cart[product_id_str] = current_quantity + 1
    request.session['cart'] = cart
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': f'{product.name} added to cart!',
            'cart_count': sum(cart.values())
        })
    
    messages.success(request, f'{product.name} added to cart!')
    return redirect('cart')


# Remove from Cart
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        del cart[product_id_str]
    
    request.session['cart'] = cart
    request.session.modified = True
    
    messages.success(request, 'Product removed from cart.')
    return redirect('cart')


# Update Cart Quantity
def update_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})
        product_id_str = str(product_id)
        product = get_object_or_404(Product, id=product_id)

        if quantity > product.stock:
            quantity = product.stock
            messages.warning(request, f'Quantity reduced to available stock ({product.stock}).')

        if quantity > 0:
            cart[product_id_str] = quantity
        elif product_id_str in cart:
            del cart[product_id_str]

        request.session['cart'] = cart
        request.session.modified = True

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})

        messages.success(request, 'Cart updated.')
    
    return redirect('cart')


# Checkout Page
@login_required(login_url='login')
def checkout(request):
    cart_items = request.session.get('cart', {})
    
    if not cart_items:
        messages.warning(request, 'Your cart is empty.')
        return redirect('home')
    
    products = []
    total_price = 0
    
    for product_id, quantity in cart_items.items():
        product = get_object_or_404(Product, id=int(product_id))
        item_total = product.price * quantity
        products.append({
            'product': product,
            'quantity': quantity,
            'total': item_total
        })
        total_price += item_total
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create order
            order = Order.objects.create(
                user=request.user,
                total_amount=total_price,
                shipping_address=form.cleaned_data['shipping_address'],
                shipping_city=form.cleaned_data['shipping_city'],
                shipping_zipcode=form.cleaned_data['shipping_zipcode'],
                shipping_country=form.cleaned_data['shipping_country'],
                status='confirmed'
            )
            
            # Create order items
            for product_id, quantity in cart_items.items():
                product = get_object_or_404(Product, id=int(product_id))
                if quantity > product.stock:
                    order.delete()
                    messages.error(request, f'Not enough stock for {product.name}.')
                    return redirect('cart')
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )
                product.stock -= quantity
                product.save()
            
            # Clear cart
            request.session['cart'] = {}
            request.session.modified = True
            
            messages.success(request, 'Order placed successfully!')
            return redirect('order_confirmation', order_id=order.id)
    else:
        form = CheckoutForm()
    
    context = {
        'cart_items': products,
        'total_price': total_price,
        'form': form,
    }
    return render(request, 'store/checkout.html', context)


# Order Confirmation
@login_required(login_url='login')
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
        'order_items': order.items.all(),
    }
    return render(request, 'store/order_confirmation.html', context)


# Order History
@login_required(login_url='login')
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    
    context = {
        'orders': orders,
    }
    return render(request, 'store/order_history.html', context)


# Order Details
@login_required(login_url='login')
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
        'order_items': order.items.all(),
    }
    return render(request, 'store/order_detail.html', context)


# Wishlist
@login_required(login_url='login')
def wishlist(request):
    try:
        wishlist = Wishlist.objects.get(user=request.user)
        products = wishlist.products.all()
    except Wishlist.DoesNotExist:
        wishlist = Wishlist.objects.create(user=request.user)
        products = []
    
    context = {
        'wishlist': wishlist,
        'products': products,
    }
    return render(request, 'store/wishlist.html', context)


# Add to Wishlist
@login_required(login_url='login')
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    if product in wishlist.products.all():
        wishlist.products.remove(product)
        message = f'{product.name} removed from wishlist.'
    else:
        wishlist.products.add(product)
        message = f'{product.name} added to wishlist!'
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': message,
        })
    
    messages.success(request, message)
    return redirect(request.GET.get('next', 'home'))


# Profile
@login_required(login_url='login')
def profile(request):
    orders = Order.objects.filter(user=request.user).count()
    total_spent = sum(order.total_amount for order in Order.objects.filter(user=request.user))
    
    context = {
        'total_orders': orders,
        'total_spent': total_spent,
    }
    return render(request, 'store/profile.html', context)
