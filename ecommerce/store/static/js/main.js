document.addEventListener('DOMContentLoaded', function () {
    /* ==========================================================================
       1. THEME SWITCHER SYSTEM (Light / Dark mode)
       ========================================================================== */
    const currentTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);

    // Dynamic insertion of theme toggle if a designated toggle btn exists or we place one
    const themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) {
        updateThemeIcon(themeBtn, currentTheme);
        themeBtn.addEventListener('click', function () {
            const activeTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = activeTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(themeBtn, newTheme);
            showToast(`Switched to ${newTheme} mode!`, 'success');
        });
    }

    function updateThemeIcon(btn, theme) {
        const icon = btn.querySelector('i');
        if (icon) {
            if (theme === 'dark') {
                icon.className = 'fa-solid fa-sun';
            } else {
                icon.className = 'fa-solid fa-moon';
            }
        }
    }

    /* ==========================================================================
       2. DYNAMIC TOAST NOTIFICATION CONTAINER
       ========================================================================== */
    function showToast(message, type = 'success') {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        let iconClass = 'fa-circle-check';
        if (type === 'warning') iconClass = 'fa-triangle-exclamation';
        if (type === 'error') iconClass = 'fa-circle-exclamation';

        toast.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <i class="fa-solid ${iconClass}"></i>
                <span>${message}</span>
            </div>
            <button class="toast-close"><i class="fa-solid fa-xmark"></i></button>
        `;

        container.appendChild(toast);

        // Click to close
        toast.querySelector('.toast-close').addEventListener('click', () => {
            closeToast(toast);
        });

        // Auto close after 4 seconds
        setTimeout(() => {
            closeToast(toast);
        }, 4000);
    }

    function closeToast(toast) {
        toast.style.animation = 'toastOut 0.3s cubic-bezier(0.4, 0, 0.2, 1) forwards';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }

    // Expose toast system globally
    window.showToast = showToast;

    /* ==========================================================================
       3. AJAX ADD-TO-CART OPERATIONS
       ========================================================================== */
    document.body.addEventListener('click', function (event) {
        const cartBtn = event.target.closest('[data-action="add-to-cart"]');
        if (cartBtn) {
            event.preventDefault();
            const href = cartBtn.getAttribute('href') || cartBtn.dataset.url;
            if (!href) return;

            fetch(href, {
                method: 'GET',
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showToast(data.message, 'success');
                    
                    // Bounce animation on button
                    cartBtn.classList.add('btn-secondary');
                    const originalText = cartBtn.innerHTML;
                    cartBtn.innerHTML = '<i class="fa-solid fa-check"></i> Added';
                    
                    setTimeout(() => {
                        cartBtn.classList.remove('btn-secondary');
                        cartBtn.innerHTML = originalText;
                    }, 2000);

                    // Update all badge counts
                    if (data.cart_count !== undefined) {
                        document.querySelectorAll('.badge').forEach(badge => {
                            badge.textContent = data.cart_count;
                            // Add micro animation bounce to badges
                            badge.style.transform = 'scale(1.25)';
                            setTimeout(() => badge.style.transform = 'none', 300);
                        });
                    }
                } else {
                    showToast(data.message || 'Could not add product.', 'error');
                }
            })
            .catch(error => {
                console.error('Error adding to cart:', error);
                showToast('Failed to add product to cart.', 'error');
            });
        }
    });

    /* ==========================================================================
       4. AJAX WISHLIST TOGGLE (INSTANT HEART BOUNCE)
       ========================================================================== */
    document.body.addEventListener('click', function (event) {
        const heartBtn = event.target.closest('.wishlist-heart-btn, [data-action="toggle-wishlist"]');
        if (heartBtn) {
            event.preventDefault();
            const href = heartBtn.getAttribute('href') || heartBtn.dataset.url;
            if (!href) return;

            fetch(href, {
                method: 'GET',
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showToast(data.message, 'success');
                    
                    // Toggle active classes
                    heartBtn.classList.toggle('active');
                    const icon = heartBtn.querySelector('i');
                    if (icon) {
                        if (heartBtn.classList.contains('active') || data.message.includes('added')) {
                            heartBtn.classList.add('active');
                            icon.className = 'fa-solid fa-heart';
                        } else {
                            heartBtn.classList.remove('active');
                            icon.className = 'fa-regular fa-heart';
                        }
                    }
                } else {
                    showToast('Failed to update wishlist.', 'warning');
                }
            })
            .catch(error => {
                console.error('Error toggling wishlist:', error);
                showToast('Please log in to manage your wishlist!', 'error');
            });
        }
    });

    /* ==========================================================================
       5. AJAX INLINE QUANTITY CONTROLS (IN CART)
       ========================================================================== */
    const cartTable = document.querySelector('.cart-table');
    if (cartTable) {
        // CSRF Token fetcher
        function getCSRFToken() {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, 10) === 'csrftoken=') {
                        cookieValue = decodeURIComponent(cookie.substring(10));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        // Trigger updates to Django backend
        function updateQuantityOnServer(productId, quantity, rowElement) {
            const formData = new FormData();
            formData.append('quantity', quantity);
            formData.append('csrfmiddlewaretoken', getCSRFToken());

            fetch(`/cart/update/${productId}/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Update totals instantly
                    recalculateCartTotals();
                } else {
                    showToast(data.message || 'Error updating quantity.', 'error');
                }
            })
            .catch(error => {
                console.error('Error updating quantity:', error);
                showToast('Failed to update cart quantity.', 'error');
            });
        }

        function recalculateCartTotals() {
            let grandTotal = 0;
            let cartCount = 0;

            document.querySelectorAll('.cart-row:not(.cart-header)').forEach(row => {
                const price = parseFloat(row.querySelector('.col-price').textContent.replace('$', ''));
                const input = row.querySelector('.quantity-form input');
                const qty = parseInt(input.value);

                const rowTotal = price * qty;
                row.querySelector('.col-total').textContent = `$${rowTotal.toFixed(2)}`;

                grandTotal += rowTotal;
                cartCount += qty;
            });

            // Update DOM grand totals
            const totalDisplays = document.querySelectorAll('.summary-row.total span:last-child, .checkout-total span:last-child');
            totalDisplays.forEach(display => {
                display.textContent = `$${grandTotal.toFixed(2)}`;
            });

            // Update badge counts
            document.querySelectorAll('.badge').forEach(badge => {
                badge.textContent = cartCount;
            });
        }

        // Increment and Decrement click listeners
        cartTable.addEventListener('click', function (event) {
            const decBtn = event.target.closest('.qty-dec');
            const incBtn = event.target.closest('.qty-inc');
            
            if (decBtn || incBtn) {
                event.preventDefault();
                const btn = decBtn || incBtn;
                const row = btn.closest('.cart-row');
                const input = row.querySelector('.quantity-form input');
                const productId = row.dataset.productId;
                
                let qty = parseInt(input.value);
                const maxStock = parseInt(input.getAttribute('max') || 99);

                if (decBtn) {
                    if (qty > 1) qty -= 1;
                } else if (incBtn) {
                    if (qty < maxStock) qty += 1;
                    else {
                        showToast('Maximum stock reached!', 'warning');
                        return;
                    }
                }

                input.value = qty;
                updateQuantityOnServer(productId, qty, row);
            }
        });

        // Keyup input listeners (debounce update slightly)
        let debounceTimer;
        cartTable.addEventListener('input', function (event) {
            const input = event.target.closest('.quantity-form input');
            if (input) {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    const row = input.closest('.cart-row');
                    const productId = row.dataset.productId;
                    let qty = parseInt(input.value);
                    const maxStock = parseInt(input.getAttribute('max') || 99);

                    if (isNaN(qty) || qty < 1) qty = 1;
                    if (qty > maxStock) {
                        qty = maxStock;
                        showToast(`Adjusted to maximum available stock (${maxStock})`, 'warning');
                    }

                    input.value = qty;
                    updateQuantityOnServer(productId, qty, row);
                }, 500);
            }
        });
    }

    /* ==========================================================================
       6. MOBILE NAVIGATION BAR
       ========================================================================== */
    const mobileButton = document.getElementById('mobile-nav-button');
    const mobileNav = document.getElementById('mobile-nav');
    const mobileClose = document.getElementById('mobile-nav-close');
    const mobileBackdrop = document.getElementById('mobile-nav-backdrop');

    function openMobileNav() {
        if (!mobileNav) return;
        mobileNav.classList.add('open');
        mobileButton && mobileButton.setAttribute('aria-expanded', 'true');
        document.body.style.overflow = 'hidden';
    }

    function closeMobileNav() {
        if (!mobileNav) return;
        mobileNav.classList.remove('open');
        mobileButton && mobileButton.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
    }

    mobileButton && mobileButton.addEventListener('click', openMobileNav);
    mobileClose && mobileClose.addEventListener('click', closeMobileNav);
    mobileBackdrop && mobileBackdrop.addEventListener('click', closeMobileNav);

    /* ==========================================================================
       7. IMAGE ERROR FALLBACK SYSTEM
       ========================================================================== */
    document.addEventListener('error', function (event) {
        if (event.target.tagName && event.target.tagName.toLowerCase() === 'img') {
            event.target.src = 'https://images.unsplash.com/photo-1531403009284-440f080d1e12?q=80&w=1200&auto=format&fit=crop';
        }
    }, true);
});