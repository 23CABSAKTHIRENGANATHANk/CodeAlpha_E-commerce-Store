from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from store.models import Category, Product, Order, OrderItem, Wishlist
from decimal import Decimal

class StoreTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create Category
        self.category = Category.objects.create(
            name='Test Electronics',
            description='Test description'
        )
        
        # Create Product
        self.product = Product.objects.create(
            name='Test Phone',
            price=Decimal('599.99'),
            description='Sleek test phone',
            category=self.category,
            stock=5
        )
        
        # Create User
        self.user_password = 'password123'
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password=self.user_password
        )
        
        # Create Wishlist for user
        self.wishlist = Wishlist.objects.create(user=self.user)

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/home.html')
        self.assertIn('products', response.context)
        self.assertIn('categories', response.context)
        
        # Test Search query
        response_search = self.client.get(reverse('home'), {'search': 'Phone'})
        self.assertEqual(len(response_search.context['products']), 1)
        
        # Test Category query
        response_category = self.client.get(reverse('home'), {'category': 'Test Electronics'})
        self.assertEqual(len(response_category.context['products']), 1)

    def test_product_detail_view(self):
        response = self.client.get(reverse('product_detail', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/product_detail.html')
        self.assertEqual(response.context['product'], self.product)
        
        # Test non-existent product
        response_404 = self.client.get(reverse('product_detail', args=[9999]))
        self.assertEqual(response_404.status_code, 404)

    def test_register_view(self):
        # GET request
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        
        # POST request with valid details
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'newpassword123',
            'password2': 'newpassword123'
        }
        response_post = self.client.post(reverse('register'), data)
        self.assertRedirects(response_post, reverse('login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
        # Wishlist should be automatically created for registered user
        new_user = User.objects.get(username='newuser')
        self.assertTrue(Wishlist.objects.filter(user=new_user).exists())

    def test_login_logout_views(self):
        # Login view GET
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        
        # Login POST valid
        login_data = {
            'username': 'testuser',
            'password': self.user_password
        }
        response_login = self.client.post(reverse('login'), login_data)
        self.assertRedirects(response_login, reverse('home'))
        
        # Logout
        response_logout = self.client.get(reverse('logout'))
        self.assertRedirects(response_logout, reverse('home'))

    def test_cart_operations(self):
        # View cart empty
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cart_count'], 0)
        
        # Add to cart
        response_add = self.client.get(reverse('add_to_cart', args=[self.product.id]))
        self.assertRedirects(response_add, reverse('cart'))
        
        # Cart session updated
        session = self.client.session
        self.assertEqual(session['cart'][str(self.product.id)], 1)
        
        # AJAX Add to cart
        response_ajax = self.client.get(
            reverse('add_to_cart', args=[self.product.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response_ajax.status_code, 200)
        self.assertEqual(response_ajax.json()['status'], 'success')
        self.assertEqual(response_ajax.json()['cart_count'], 2)
        
        # Update cart quantity
        response_update = self.client.post(
            reverse('update_cart', args=[self.product.id]),
            {'quantity': 3}
        )
        self.assertRedirects(response_update, reverse('cart'))
        self.assertEqual(self.client.session['cart'][str(self.product.id)], 3)
        
        # Remove from cart
        response_remove = self.client.get(reverse('remove_from_cart', args=[self.product.id]))
        self.assertRedirects(response_remove, reverse('cart'))
        self.assertNotIn(str(self.product.id), self.client.session['cart'])

    def test_wishlist_operations(self):
        # Add to wishlist requires login
        response = self.client.get(reverse('add_to_wishlist', args=[self.product.id]))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('add_to_wishlist', args=[self.product.id])}")
        
        # Login first
        self.client.login(username='testuser', password=self.user_password)
        
        # Wishlist view
        response_wishlist = self.client.get(reverse('wishlist'))
        self.assertEqual(response_wishlist.status_code, 200)
        
        # Add to wishlist
        response_toggle1 = self.client.get(reverse('add_to_wishlist', args=[self.product.id]))
        self.assertRedirects(response_toggle1, reverse('home'))
        self.assertIn(self.product, self.wishlist.products.all())
        
        # Remove from wishlist (toggle again)
        response_toggle2 = self.client.get(reverse('add_to_wishlist', args=[self.product.id]))
        self.assertRedirects(response_toggle2, reverse('home'))
        self.assertNotIn(self.product, self.wishlist.products.all())
        
        # AJAX toggle
        response_ajax = self.client.get(
            reverse('add_to_wishlist', args=[self.product.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response_ajax.status_code, 200)
        self.assertEqual(response_ajax.json()['status'], 'success')
        self.assertIn(self.product, self.wishlist.products.all())

    def test_checkout_and_orders(self):
        # Checkout login required
        response = self.client.get(reverse('checkout'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('checkout')}")
        
        # Login
        self.client.login(username='testuser', password=self.user_password)
        
        # Add item to cart
        session = self.client.session
        session['cart'] = {str(self.product.id): 2}
        session.save()
        
        # Checkout GET
        response_checkout = self.client.get(reverse('checkout'))
        self.assertEqual(response_checkout.status_code, 200)
        self.assertTemplateUsed(response_checkout, 'store/checkout.html')
        
        # Checkout POST (Submit Order)
        checkout_data = {
            'shipping_address': '123 Main St',
            'shipping_city': 'Tech City',
            'shipping_zipcode': '12345',
            'shipping_country': 'United States'
        }
        response_post = self.client.post(reverse('checkout'), checkout_data)
        
        # Verify redirect to order confirmation
        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertRedirects(response_post, reverse('order_confirmation', args=[order.id]))
        
        # Verify Order fields and relationship models
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.shipping_address, '123 Main St')
        self.assertEqual(order.total_amount, self.product.price * 2)
        
        # Verify OrderItem creation
        order_item = OrderItem.objects.get(order=order)
        self.assertEqual(order_item.product, self.product)
        self.assertEqual(order_item.quantity, 2)
        
        # Verify stock decremented
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
        
        # Verify cart session cleared
        self.assertEqual(self.client.session['cart'], {})
        
        # Order detail view
        response_detail = self.client.get(reverse('order_detail', args=[order.id]))
        self.assertEqual(response_detail.status_code, 200)
        
        # Order history
        response_history = self.client.get(reverse('order_history'))
        self.assertEqual(response_history.status_code, 200)
        self.assertIn(order, response_history.context['orders'])

    def test_profile_view(self):
        # Login
        self.client.login(username='testuser', password=self.user_password)
        
        # Empty stats initially
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_orders'], 0)
        self.assertEqual(response.context['total_spent'], 0)
        
        # Create order to check non-zero stats
        order = Order.objects.create(
            user=self.user,
            total_amount=Decimal('100.50'),
            shipping_address='Addr',
            shipping_city='City',
            shipping_zipcode='Zip',
            shipping_country='Country',
            status='confirmed'
        )
        
        response_with_orders = self.client.get(reverse('profile'))
        self.assertEqual(response_with_orders.status_code, 200)
        self.assertEqual(response_with_orders.context['total_orders'], 1)
        self.assertEqual(response_with_orders.context['total_spent'], Decimal('100.50'))

    def test_admin_login_redirect(self):
        # Accessing admin login should redirect to storefront login
        response = self.client.get('/admin/login/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/?next=', response.url)
