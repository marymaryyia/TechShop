from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy import func
from datetime import datetime, timedelta

from app.models import (
    db, User, Category, Subcategory, Brand, Product, Order, 
    Review, Coupon, MegaGroup, MegaItem
)
from app.utils import admin_required
from app.services.storage import StorageService

admin_bp = Blueprint('admin', __name__, template_folder='../templates/admin')

@admin_bp.route('/customers/<int:customer_id>/suspend', methods=['POST'])
@login_required
@admin_required
def admin_customer_suspend(customer_id):
    customer = User.query.get_or_404(customer_id)
    
    customer.is_active = not customer.is_active
    db.session.commit()
    
    status_text = "გააქტიურებულია" if customer.is_active else "დაბლოკილია"
    flash(f'მომხმარებლის სტატუსი წარმატებით შეიცვალა ({status_text}).', 'success')
    
    return redirect(url_for('admin.admin_customers'))

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
@admin_required
def admin_dashboard():
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_customers = User.query.filter_by(role='user').count()
    active_orders = Order.query.filter(Order.status != 'cancelled').all()
    total_revenue = sum(order.total for order in active_orders)
    total_categories = Category.query.count()
    total_reviews = Review.query.count()
    active_coupons = Coupon.query.filter_by(is_active=True).count()
    low_stock = Product.query.filter(Product.stock_qty <= 5).count()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    low_stock_products = Product.query.filter(Product.stock_qty <= 5).all()

    sales_labels = []
    sales_values = []
    today = datetime.utcnow().date()
    
    for i in range(6, -1, -1):
        target_date = today - timedelta(days=i)
        sales_labels.append(target_date.strftime('%d %b'))
        
        daily_orders = Order.query.filter(
            func.date(Order.created_at) == target_date,
            Order.status != 'cancelled'
        ).all()
        
        daily_revenue = sum(order.total for order in daily_orders)
        
        sales_values.append(float(daily_revenue))
    status_query = db.session.query(Order.status, func.count(Order.id)).group_by(Order.status).all()
    status_labels = []
    status_values = []
    
    for status, count in status_query:
        label = status.capitalize() if status else 'Unknown'
        status_labels.append(label)
        status_values.append(count)
        
    if not status_labels:
        status_labels = ['No Orders']
        status_values = [1]

    return render_template(
        'admin/dashboard.html', 
        total_products=total_products,
        total_orders=total_orders,
        total_customers=total_customers,
        total_revenue=total_revenue,
        total_categories=total_categories,
        total_reviews=total_reviews,
        active_coupons=active_coupons,
        low_stock=low_stock,
        recent_orders=recent_orders, 
        low_stock_products=low_stock_products,
        sales_labels=sales_labels,
        sales_values=sales_values,
        status_labels=status_labels,
        status_values=status_values
    )


# products

@admin_bp.route('/products')
@login_required
@admin_required
def admin_products():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '').strip()
    status = request.args.get('status')
    category_id = request.args.get('category', type=int)
    
    query = Product.query
    
    if search:
        query = query.filter(
            Product.name_en.ilike(f'%{search}%') | 
            Product.sku.ilike(f'%{search}%')
        )
    
    if status == 'out_of_stock':
        query = query.filter(Product.stock_qty == 0)
    elif status == 'active':
        query = query.filter(Product.is_active == True)
    elif status == 'inactive':
        query = query.filter(Product.is_active == False)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    products = query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    
    categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order).all()
        
    return render_template(
        'admin/products.html', 
        products=products, 
        search=search,
        pagination=products,
        categories=categories
    )


@admin_bp.route('/products/create', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_product_create():
    if request.method == 'POST':
        product = Product(
            name_ka=request.form['name_ka'],
            name_en=request.form['name_en'],
            slug=request.form['slug'],
            description_ka=request.form.get('description_ka'),
            description_en=request.form.get('description_en'),
            price=float(request.form['price']),
            old_price=float(request.form['old_price']) if request.form.get('old_price') else None,
            stock_qty=int(request.form.get('stock_qty', 0)),
            sku=request.form.get('sku'),
            badge=request.form.get('badge') or None,
            category_id=int(request.form['category_id']),
            subcategory_id=int(request.form['subcategory_id']) if request.form.get('subcategory_id') else None,
            brand_id=int(request.form['brand_id']) if request.form.get('brand_id') else None,
            is_active=bool(request.form.get('is_active'))
        )
        
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                try:
                    url = StorageService.save(file, folder='uploads')
                    product.image = url
                except ValueError as e:
                    flash(str(e), 'warning')
        
        db.session.add(product)
        db.session.commit()
        flash('Product created successfully.', 'success')
        return redirect(url_for('admin.admin_products'))
    
    categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order).all()
    subcategories = Subcategory.query.filter_by(is_active=True).order_by(Subcategory.sort_order).all()
    brands = Brand.query.filter_by(is_active=True).order_by(Brand.name).all()
    return render_template('admin/product_form.html', categories=categories, subcategories=subcategories, brands=brands)


@admin_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_product_edit(product_id):
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product.name_ka = request.form['name_ka']
        product.name_en = request.form['name_en']
        product.slug = request.form['slug']
        product.description_ka = request.form.get('description_ka')
        product.description_en = request.form.get('description_en')
        product.price = float(request.form['price'])
        product.old_price = float(request.form['old_price']) if request.form.get('old_price') else None
        product.stock_qty = int(request.form.get('stock_qty', 0))
        product.sku = request.form.get('sku')
        product.badge = request.form.get('badge') or None
        product.category_id = int(request.form['category_id'])
        product.subcategory_id = int(request.form['subcategory_id']) if request.form.get('subcategory_id') else None
        product.brand_id = int(request.form['brand_id']) if request.form.get('brand_id') else None
        product.is_active = bool(request.form.get('is_active'))
        
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                try:
                    if product.image:
                        StorageService.delete(product.image)
                    url = StorageService.save(file, folder='uploads')
                    product.image = url
                except ValueError as e:
                    flash(str(e), 'warning')
        
        db.session.commit()
        flash('Product updated successfully.', 'success')
        return redirect(url_for('admin.admin_products'))
    
    categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order).all()
    subcategories = Subcategory.query.filter_by(is_active=True).order_by(Subcategory.sort_order).all()
    brands = Brand.query.filter_by(is_active=True).order_by(Brand.name).all()
    return render_template('admin/product_form.html', product=product, categories=categories, subcategories=subcategories, brands=brands)


@admin_bp.route('/products/<int:product_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_product_delete(product_id):
    product = Product.query.get_or_404(product_id)
    if product.image:
        StorageService.delete(product.image)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully.', 'success')
    return redirect(url_for('admin.admin_products'))


# categroies

@admin_bp.route('/categories')
@login_required
@admin_required
def admin_categories():
    categories = Category.query.order_by(Category.sort_order).all()
    return render_template('admin/categories.html', categories=categories)


@admin_bp.route('/categories/create', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_category_create():
    if request.method == 'POST':
        category = Category(
            name_ka=request.form['name_ka'],
            name_en=request.form['name_en'],
            slug=request.form['slug'],
            icon_class=request.form.get('icon_class', 'bi-box'),
            sort_order=int(request.form.get('sort_order', 0))
        )
        db.session.add(category)
        db.session.commit()
        flash('Category created successfully.', 'success')
        return redirect(url_for('admin.admin_categories'))
    return render_template('admin/category_form.html')


@admin_bp.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_category_edit(category_id):
    category = Category.query.get_or_404(category_id)
    if request.method == 'POST':
        category.name_ka = request.form['name_ka']
        category.name_en = request.form['name_en']
        category.slug = request.form['slug']
        category.icon_class = request.form.get('icon_class', 'bi-box')
        category.sort_order = int(request.form.get('sort_order', 0))
        db.session.commit()
        flash('Category updated successfully.', 'success')
        return redirect(url_for('admin.admin_categories'))
    return render_template('admin/category_form.html', category=category)


@admin_bp.route('/categories/<int:category_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_category_delete(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully.', 'success')
    return redirect(url_for('admin.admin_categories'))


#subcat

@admin_bp.route('/subcategories')
@login_required
@admin_required
def admin_subcategories():
    subcategories = Subcategory.query.order_by(Subcategory.sort_order).all()
    return render_template('admin/subcategories.html', subcategories=subcategories)


@admin_bp.route('/subcategories/create', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_subcategory_create():
    if request.method == 'POST':
        subcategory = Subcategory(
            category_id=int(request.form['category_id']),
            name_ka=request.form['name_ka'],
            name_en=request.form['name_en'],
            slug=request.form['slug'],
            sort_order=int(request.form.get('sort_order', 0))
        )
        db.session.add(subcategory)
        db.session.commit()
        flash('Subcategory created successfully.', 'success')
        return redirect(url_for('admin.admin_subcategories'))
    
    categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order).all()
    return render_template('admin/subcategory_form.html', categories=categories)


@admin_bp.route('/subcategories/<int:subcategory_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_subcategory_edit(subcategory_id):
    subcategory = Subcategory.query.get_or_404(subcategory_id)
    if request.method == 'POST':
        subcategory.category_id = int(request.form['category_id'])
        subcategory.name_ka = request.form['name_ka']
        subcategory.name_en = request.form['name_en']
        subcategory.slug = request.form['slug']
        subcategory.sort_order = int(request.form.get('sort_order', 0))
        db.session.commit()
        flash('Subcategory updated successfully.', 'success')
        return redirect(url_for('admin.admin_subcategories'))
    
    categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order).all()
    return render_template('admin/subcategory_form.html', subcategory=subcategory, categories=categories)


@admin_bp.route('/subcategories/<int:subcategory_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_subcategory_delete(subcategory_id):
    subcategory = Subcategory.query.get_or_404(subcategory_id)
    db.session.delete(subcategory)
    db.session.commit()
    flash('Subcategory deleted successfully.', 'success')
    return redirect(url_for('admin.admin_subcategories'))


#mega groups

@admin_bp.route('/mega-groups')
@login_required
@admin_required
def admin_mega_groups():
    groups = MegaGroup.query.order_by(MegaGroup.sort_order).all()
    categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order).all()
    selected_category = request.args.get('category', type=int)
    
    if selected_category:
        groups = MegaGroup.query.filter_by(category_id=selected_category).order_by(MegaGroup.sort_order).all()
    
    return render_template('admin/mega_groups.html', groups=groups, categories=categories, selected_category=selected_category)


@admin_bp.route('/mega-groups/create', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_mega_group_create():
    if request.method == 'POST':
        group = MegaGroup(
            category_id=int(request.form['category_id']),
            title_ka=request.form['title_ka'],
            title_en=request.form['title_en'],
            sort_order=int(request.form.get('sort_order', 0))
        )
        db.session.add(group)
        db.session.commit()
        flash('Mega Group created successfully.', 'success')
        return redirect(url_for('admin.admin_mega_groups'))
    
    categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order).all()
    return render_template('admin/mega_group_form.html', categories=categories)


@admin_bp.route('/mega-groups/<int:group_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_mega_group_edit(group_id):
    group = MegaGroup.query.get_or_404(group_id)
    if request.method == 'POST':
        group.category_id = int(request.form['category_id'])
        group.title_ka = request.form['title_ka']
        group.title_en = request.form['title_en']
        group.sort_order = int(request.form.get('sort_order', 0))
        db.session.commit()
        flash('Mega Group updated successfully.', 'success')
        return redirect(url_for('admin.admin_mega_groups'))
    
    categories = Category.query.filter_by(is_active=True).order_by(Category.sort_order).all()
    return render_template('admin/mega_group_form.html', group=group, categories=categories)


@admin_bp.route('/mega-groups/<int:group_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_mega_group_delete(group_id):
    group = MegaGroup.query.get_or_404(group_id)
    db.session.delete(group)
    db.session.commit()
    flash('Mega Group deleted successfully.', 'success')
    return redirect(url_for('admin.admin_mega_groups'))


# megaitems

@admin_bp.route('/mega-items')
@login_required
@admin_required
def admin_mega_items():
    items = MegaItem.query.order_by(MegaItem.sort_order).all()
    groups = MegaGroup.query.order_by(MegaGroup.sort_order).all()
    selected_group = request.args.get('group', type=int)
    
    if selected_group:
        items = MegaItem.query.filter_by(group_id=selected_group).order_by(MegaItem.sort_order).all()
    
    return render_template('admin/mega_items.html', items=items, groups=groups, selected_group=selected_group)


@admin_bp.route('/mega-items/create', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_mega_item_create():
    if request.method == 'POST':
        item = MegaItem(
            group_id=int(request.form['group_id']),
            title_ka=request.form['title_ka'],
            title_en=request.form['title_en'],
            url=request.form['url'],
            sort_order=int(request.form.get('sort_order', 0))
        )
        db.session.add(item)
        db.session.commit()
        flash('Mega Item created successfully.', 'success')
        return redirect(url_for('admin.admin_mega_items'))
    
    groups = MegaGroup.query.order_by(MegaGroup.sort_order).all()
    return render_template('admin/mega_item_form.html', groups=groups)


@admin_bp.route('/mega-items/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_mega_item_edit(item_id):
    item = MegaItem.query.get_or_404(item_id)
    if request.method == 'POST':
        item.group_id = int(request.form['group_id'])
        item.title_ka = request.form['title_ka']
        item.title_en = request.form['title_en']
        item.url = request.form['url']
        item.sort_order = int(request.form.get('sort_order', 0))
        db.session.commit()
        flash('Mega Item updated successfully.', 'success')
        return redirect(url_for('admin.admin_mega_items'))
    
    groups = MegaGroup.query.order_by(MegaGroup.sort_order).all()
    return render_template('admin/mega_item_form.html', item=item, groups=groups)


@admin_bp.route('/mega-items/<int:item_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_mega_item_delete(item_id):
    item = MegaItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Mega Item deleted successfully.', 'success')
    return redirect(url_for('admin.admin_mega_items'))


# orders

@admin_bp.route('/orders')
@login_required
@admin_required
def admin_orders():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    search = request.args.get('q', '').strip()
    
    query = Order.query
    
    if status:
        query = query.filter_by(status=status)
    
    if search:
        query = query.filter(
            Order.customer_name.ilike(f'%{search}%') |
            Order.customer_email.ilike(f'%{search}%')
        )
    
    orders = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    
    return render_template('admin/orders.html', orders=orders, status=status, pagination=orders)


@admin_bp.route('/orders/<int:order_id>')
@login_required
@admin_required
def admin_order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)


@admin_bp.route('/orders/<int:order_id>/status', methods=['POST'])
@login_required
@admin_required
def admin_order_update_status(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = request.form['status']
    db.session.commit()
    flash('Order status updated.', 'success')
    return redirect(url_for('admin.admin_order_detail', order_id=order.id))


# customers

@admin_bp.route('/customers')
@login_required
@admin_required
def admin_customers():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '').strip()
    status = request.args.get('status')
    
    query = User.query.filter_by(role='user')
    
    if search:
        query = query.filter(
            (User.first_name.ilike(f'%{search}%')) |
            (User.last_name.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )
    
    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'suspended':
        query = query.filter_by(is_active=False)
    
    customers = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    
    return render_template('admin/customers.html', customers=customers, search=search, pagination=customers)


@admin_bp.route('/customers/<int:customer_id>')
@login_required
@admin_required
def admin_customer_detail(customer_id):
    customer = User.query.get_or_404(customer_id)
    orders = Order.query.filter_by(user_id=customer.id).order_by(Order.created_at.desc()).all()
    return render_template('admin/customer_detail.html', customer=customer, orders=orders)


@admin_bp.route('/customers/<int:customer_id>/toggle', methods=['POST'])
@login_required
@admin_required
def admin_customer_toggle(customer_id):
    customer = User.query.get_or_404(customer_id)
    customer.is_active = not customer.is_active
    db.session.commit()
    flash('Customer status updated.', 'success')
    return redirect(url_for('admin.admin_customers'))


# coupons

@admin_bp.route('/coupons')
@login_required
@admin_required
def admin_coupons():
    page = request.args.get('page', 1, type=int)
    coupons = Coupon.query.order_by(Coupon.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    return render_template('admin/coupons.html', coupons=coupons, pagination=coupons)


@admin_bp.route('/coupons/create', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_coupon_create():
    if request.method == 'POST':
        expires = request.form.get('expires_at')
        coupon = Coupon(
            code=request.form['code'].upper(),
            type=request.form['type'],
            value=float(request.form['value']),
            max_uses=int(request.form['max_uses']) if request.form.get('max_uses') else None,
            min_order=float(request.form.get('min_order', 0)),
            expires_at=datetime.strptime(expires, '%Y-%m-%d') if expires else None,
            is_active=bool(request.form.get('is_active'))
        )
        db.session.add(coupon)
        db.session.commit()
        flash('Coupon created successfully.', 'success')
        return redirect(url_for('admin.admin_coupons'))
    return render_template('admin/coupon_form.html')


@admin_bp.route('/coupons/<int:coupon_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_coupon_edit(coupon_id):
    coupon = Coupon.query.get_or_404(coupon_id)
    if request.method == 'POST':
        expires = request.form.get('expires_at')
        coupon.code = request.form['code'].upper()
        coupon.type = request.form['type']
        coupon.value = float(request.form['value'])
        coupon.max_uses = int(request.form['max_uses']) if request.form.get('max_uses') else None
        coupon.min_order = float(request.form.get('min_order', 0))
        coupon.expires_at = datetime.strptime(expires, '%Y-%m-%d') if expires else None
        coupon.is_active = bool(request.form.get('is_active'))
        db.session.commit()
        flash('Coupon updated successfully.', 'success')
        return redirect(url_for('admin.admin_coupons'))
    return render_template('admin/coupon_form.html', coupon=coupon)


@admin_bp.route('/coupons/<int:coupon_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_coupon_delete(coupon_id):
    coupon = Coupon.query.get_or_404(coupon_id)
    db.session.delete(coupon)
    db.session.commit()
    flash('Coupon deleted successfully.', 'success')
    return redirect(url_for('admin.admin_coupons'))


# ─── Reviews ───

@admin_bp.route('/reviews')
@login_required
@admin_required
def admin_reviews():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'pending')
    
    query = Review.query
    
    if status == 'pending':
        query = query.filter_by(is_approved=False)
    elif status == 'approved':
        query = query.filter_by(is_approved=True)
    elif status == 'rejected':
        query = query.filter_by(status='rejected')
    
    reviews = query.order_by(Review.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    
    return render_template('admin/reviews.html', reviews=reviews, status=status, pagination=reviews)


@admin_bp.route('/reviews/<int:review_id>/approve', methods=['POST'])
@login_required
@admin_required
def admin_review_approve(review_id):
    review = Review.query.get_or_404(review_id)
    review.is_approved = True
    review.status = 'approved'
    db.session.commit()
    flash('Review approved.', 'success')
    return redirect(url_for('admin.admin_reviews'))


@admin_bp.route('/reviews/<int:review_id>/reject', methods=['POST'])
@login_required
@admin_required
def admin_review_reject(review_id):
    review = Review.query.get_or_404(review_id)
    review.status = 'rejected'
    db.session.commit()
    flash('Review rejected.', 'success')
    return redirect(url_for('admin.admin_reviews'))


@admin_bp.route('/reviews/<int:review_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_review_delete(review_id):
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    flash('Review deleted.', 'success')
    return redirect(url_for('admin.admin_reviews'))

