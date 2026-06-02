import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')

import django

django.setup()

from django.contrib.auth import get_user_model
from store.models import Category, Product

User = get_user_model()
user, created = User.objects.get_or_create(
    username='admin',
    defaults={'email': 'admin@example.com'}
)

if created:
    user.set_password('admin123')
    user.is_superuser = True
    user.is_staff = True
    user.save()

categories = [
    ('Electronics', 'Gadgets and devices'),
    ('Clothing', 'Casual and formal wear'),
    ('Home', 'Home goods and accessories'),
    ('Accessories', 'Stylish add-ons for everyday use'),
    ('Wellness', 'Comfort and self-care essentials'),
]

for name, desc in categories:
    Category.objects.get_or_create(name=name, defaults={'description': desc})

products = [
    ('Smartphone', 699.99, 'Powerful smartphone with latest features and sleek glass design.', 'Electronics', 25, 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?q=80&w=1200&auto=format&fit=crop'),
    ('Running Shoes', 89.99, 'Comfortable running shoes designed for style and support.', 'Clothing', 40, 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=1200&auto=format&fit=crop'),
    ('Coffee Maker', 59.99, 'Automatic coffee maker for fresh brew every morning.', 'Home', 15, 'https://images.unsplash.com/photo-1544787219-7f47ccb76574?q=80&w=1200&auto=format&fit=crop'),
    ('Bluetooth Speaker', 129.99, 'Rich audio with ambient lighting for your living room.', 'Electronics', 18, 'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?q=80&w=1200&auto=format&fit=crop'),
    ('Leather Wallet', 49.99, 'Slim handcrafted wallet made from premium leather.', 'Accessories', 30, 'https://images.unsplash.com/photo-1588850561407-ed78c282e89b?q=80&w=1200&auto=format&fit=crop'),
    ('Desk Lamp', 79.99, 'Modern LED desk lamp with adaptive brightness settings.', 'Home', 22, 'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?q=80&w=1200&auto=format&fit=crop'),
    ('Yoga Mat', 39.99, 'Non-slip yoga mat with high-density cushioning.', 'Wellness', 35, 'https://images.unsplash.com/photo-1592432678016-e910b452f9a2?q=80&w=1200&auto=format&fit=crop'),
    ('Sunglasses', 69.99, 'Minimalist sunglasses with UV protection.', 'Accessories', 28, 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?q=80&w=1200&auto=format&fit=crop'),
    ('Travel Backpack', 99.99, 'Lightweight travel backpack with smart organization pockets.', 'Accessories', 14, 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?q=80&w=1200&auto=format&fit=crop'),
    ('Aroma Candle Set', 39.99, 'Luxury scented candles for calm evenings at home.', 'Wellness', 45, 'https://images.unsplash.com/photo-1603006905003-be475563bc59?q=80&w=1200&auto=format&fit=crop'),
]

for name, price, desc, category_name, stock, image_url in products:
    category = Category.objects.get(name=category_name)
    product, created = Product.objects.get_or_create(
        name=name,
        defaults={
            'price': price,
            'description': desc,
            'category': category,
            'stock': stock,
            'image_url': image_url,
        }
    )
    if not created:
        updated = False
        if product.image_url != image_url:
            product.image_url = image_url
            updated = True
        if product.description != desc:
            product.description = desc
            updated = True
        if product.price != price:
            product.price = price
            updated = True
        if product.stock != stock:
            product.stock = stock
            updated = True
        if product.category != category:
            product.category = category
            updated = True
        if updated:
            product.save()

print('seeded demo data successfully')
