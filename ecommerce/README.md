# ShopEase E-commerce Django Project

A basic full-stack e-commerce website built with Django, SQLite, HTML, CSS, and JavaScript.

## Features
- Product listing and product detail pages
- User registration, login, and logout
- Cart management: add, remove, update quantity
- Checkout and order processing
- Order history and order detail pages
- Wishlist support
- Responsive design with CSS styling

## Setup
1. Create a virtual environment:

```bash
python -m venv venv
```

2. Activate the virtual environment:

```bash
venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run migrations:

```bash
python manage.py migrate
```

5. Seed demo data (optional):

```bash
python seed_data.py
```

   This also creates a demo admin user with credentials:
   - username: `admin`
   - password: `admin123`

6. Start the development server:

```bash
python manage.py runserver
```

7. Open `http://127.0.0.1:8000/` in your browser.

## Notes
- Add products and categories from the Django admin at `/admin/`.
- Product images require Pillow and can be uploaded from the admin.
- In debug mode, static files and uploaded media are served automatically.
