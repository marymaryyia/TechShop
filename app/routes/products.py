from flask import Blueprint, render_template, request, session
from app.models import Product, Category, Brand, Subcategory
from extensions import db
from app.utils.filters_config import CATEGORY_FILTERS

products_bp = Blueprint('products', __name__)

@products_bp.route('/products')
def products():
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    selected_category = request.args.get('category', '')
    selected_subcategory = request.args.get('subcategory', '')
    selected_type = request.args.get('type', '') 
    selected_sort = request.args.get('sort', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    selected_brands = request.args.getlist('brands') or request.args.getlist('brand')
    if not selected_brands and request.args.get('brand'):
        selected_brands = [request.args.get('brand')]

    lang = session.get('lang', 'ka')

    query = Product.query.filter(Product.is_active == True)

    if selected_type == 'laptop-mouse':
        query = query.join(Product.category).join(Product.subcategory).filter(
            db.or_(
                db.and_(Category.slug == 'accessories', Subcategory.slug == 'laptop-accessories'),
                db.and_(Category.slug == 'gaming', Subcategory.slug == 'gaming-accessories')
            )
        )
    else:
        if selected_category:
            query = query.join(Product.category).filter(Category.slug == selected_category)
        if selected_subcategory:
            query = query.join(Product.subcategory).filter(Subcategory.slug == selected_subcategory)

    if selected_type:
        if selected_type == 'laptop-mouse':
            query = query.filter(
                db.or_(
                    Product.specs.ilike('%"type": "laptop-mouse"%'),
                    Product.specs.ilike('%"type": "gaming-mouse"%')
                )
            )
        else:
            query = query.filter(Product.specs.ilike(f'%"type": "{selected_type}"%'))

    if selected_brands:
        selected_brands_lower = [b.lower().strip() for b in selected_brands]
        query = query.join(Product.brand).filter(db.func.lower(Brand.slug).in_(selected_brands_lower))
        
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    active_spec_filters = {}
    available_spec_filters = CATEGORY_FILTERS.get(selected_category, [])

    if selected_category and available_spec_filters:
        for spec in available_spec_filters:
            selected_vals = request.args.getlist(spec['key'])
            if selected_vals:
                active_spec_filters[spec['key']] = selected_vals
                conditions = []
                for val in selected_vals:
                    search_term = f'"{spec["key"]}": "{val}"'
                    conditions.append(Product.specs.ilike(f'%{search_term}%'))
                
                query = query.filter(db.or_(*conditions))

    if selected_sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif selected_sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif selected_sort == 'rating':
        query = query.order_by(Product.reviews_count.desc()) 
    elif selected_sort == 'new':
        query = query.order_by(Product.created_at.desc()) 
    else:
        query = query.order_by(Product.id.asc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    if selected_category:
        brands_query = Brand.query.join(Product).join(Product.category).filter(
            Category.slug == selected_category,
            Product.is_active == True
        ).distinct()
    else:
        brands_query = Brand.query.all()

    return render_template(
        'products.html',
        products=pagination.items,
        total=pagination.total,
        page=page,
        total_pages=pagination.pages,
        sidebar_categories=Category.query.all(),
        brands=brands_query,
        selected_category=selected_category,
        selected_subcategory=selected_subcategory,
        selected_brands=selected_brands,
        min_price=min_price,
        max_price=max_price,
        selected_sort=selected_sort,
        available_spec_filters=available_spec_filters,
        active_spec_filters=active_spec_filters,
        lang=lang
    )