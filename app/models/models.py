from datetime import datetime
import math
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(UserMixin, db.Model, TimestampMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(6), nullable=True)
    is_verified = db.Column(db.Boolean, default=False) 
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    avatar = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(20), default='user') 
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    orders = db.relationship('Order', back_populates='user', lazy='dynamic',
                             cascade='all, delete-orphan')
    reviews = db.relationship('Review', back_populates='user', lazy='dynamic',
                              cascade='all, delete-orphan')
    addresses = db.relationship('Address', back_populates='user', lazy='dynamic',
                                cascade='all, delete-orphan')
    
    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f"<User {self.username}>"
    @property
    def total_spent(self):
        if not self.orders:
            return 0.0
        
        return sum(order.total for order in self.orders if order.status not in ['cancelled', 'refunded'])

class Address(db.Model):
    __tablename__ = 'addresses' 
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) 
    
    label = db.Column(db.String(50))
    full_name = db.Column(db.String(100)) 
    phone = db.Column(db.String(20))
    city = db.Column(db.String(50))
    address_line1 = db.Column(db.String(200))
    address_line2 = db.Column(db.String(200)) 
    postal_code = db.Column(db.String(50))   
    is_default = db.Column(db.Boolean, default=False)
    user = db.relationship('User', back_populates='addresses')
    
    def __repr__(self):
        return f"<Address {self.label} for User {self.user_id}>"


class Category(db.Model, TimestampMixin):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name_ka = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    icon_class = db.Column(db.String(50), nullable=True)
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    subcategories = db.relationship('Subcategory', back_populates='category', lazy='dynamic',
                                    cascade='all, delete-orphan')
    products = db.relationship('Product', back_populates='category', lazy='dynamic')
    
    @property
    def name(self):
        return {"ka": self.name_ka, "en": self.name_en}

    def __repr__(self):
        return f"<Category {self.slug}>"


class Subcategory(db.Model, TimestampMixin):
    __tablename__ = 'subcategories'
    
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    name_ka = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False, index=True)
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    
    category = db.relationship('Category', back_populates='subcategories')
    products = db.relationship('Product', back_populates='subcategory', lazy='dynamic')
    __table_args__ = (
        db.UniqueConstraint('category_id', 'slug', name='_category_subcategory_slug_uc'),
    )
    @property
    def name(self):
        return {"ka": self.name_ka, "en": self.name_en}

    def __repr__(self):
        return f"<Subcategory {self.slug}>"


class Brand(db.Model, TimestampMixin):
    __tablename__ = 'brands'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    logo = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    products = db.relationship('Product', back_populates='brand', lazy='dynamic')
    
    def __repr__(self):
        return f"<Brand {self.name}>"


class Product(db.Model, TimestampMixin):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name_ka = db.Column(db.String(200), nullable=False)
    name_en = db.Column(db.String(200), nullable=False, index=True)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    description_ka = db.Column(db.Text, nullable=True)
    description_en = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    old_price = db.Column(db.Float, nullable=True)
    stock_qty = db.Column(db.Integer, default=0)
    sku = db.Column(db.String(100), unique=True, nullable=True)
    image = db.Column(db.String(255), nullable=True)
    badge = db.Column(db.String(20), nullable=True)  # new, hot, sale, none
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategories.id'), nullable=True)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    specs = db.Column(db.JSON, nullable=True)
    meta_title = db.Column(db.String(200), nullable=True)
    meta_description = db.Column(db.Text, nullable=True)
    
    category = db.relationship('Category', back_populates='products')
    subcategory = db.relationship('Subcategory', back_populates='products')
    brand = db.relationship('Brand', back_populates='products')
    reviews = db.relationship('Review', back_populates='product', lazy='dynamic',
                              cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', back_populates='product', lazy='dynamic')
    
    __table_args__ = (
        db.CheckConstraint('price >= 0', name='check_price_non_negative'),
        db.CheckConstraint('stock_qty >= 0', name='check_stock_non_negative'),
    )
    
    @property
    def name(self):
        return {"ka": self.name_ka, "en": self.name_en}

    @property
    def description(self):
        return {"ka": self.description_ka, "en": self.description_en}

    @property
    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return int(round((self.old_price - self.price) / self.old_price * 100))
        return 0
    
    @property
    def is_in_stock(self):
        return self.stock_qty > 0

    @property
    def in_stock(self):
        return self.is_in_stock

    @property
    def brand_name(self):
        return self.brand.name if self.brand else ""
    
    @property
    def average_rating(self):
        reviews = self.reviews.filter_by(is_approved=True).all()
        if not reviews:
            return 0
        return round(sum(r.rating for r in reviews) / len(reviews), 1)
    
    @property
    def reviews_count(self):
        return self.reviews.filter_by(is_approved=True).count()
    
    @property
    def formatted_price(self):
        return f"{self.price:.2f}"
    
    def __repr__(self):
        return f"<Product {self.slug}>"


class Review(db.Model, TimestampMixin):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    is_approved = db.Column(db.Boolean, default=False)
    
    product = db.relationship('Product', back_populates='reviews')
    user = db.relationship('User', back_populates='reviews')
    
    __table_args__ = (
        db.CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
    )
    
    def __repr__(self):
        return f"<Review {self.rating}* for Product {self.product_id}>"


class Order(db.Model, TimestampMixin):
    __tablename__ = 'orders'
    
    STATUS_CHOICES = {
        'pending': 'Pending',
        'processing': 'Processing',
        'shipped': 'Shipped',
        'completed': 'Completed',
        'cancelled': 'Cancelled',
        'refunded': 'Refunded'
    }
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    status = db.Column(db.String(20), default='pending')
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=True)
    shipping_address = db.Column(db.Text, nullable=True)
    payment_method = db.Column(db.String(50), nullable=True)
    coupon_code = db.Column(db.String(50), nullable=True)
    discount_amount = db.Column(db.Float, default=0)
    shipping_cost = db.Column(db.Float, default=0)
    notes = db.Column(db.Text, nullable=True)
    
    user = db.relationship('User', back_populates='orders')
    items = db.relationship('OrderItem', back_populates='order', lazy='dynamic',
                            cascade='all, delete-orphan')
    
    @property
    def subtotal(self):
        return sum(item.line_total for item in self.items)
    
    @property
    def total(self):
        return self.subtotal + self.shipping_cost - self.discount_amount
    
    @property
    def item_count(self):
        return sum(item.quantity for item in self.items)
    
    
    @property
    def status_display(self):
        return self.STATUS_CHOICES.get(self.status, self.status.title())
    
    def __repr__(self):
        return f"<Order #{self.id} {self.status}>"
    

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    price_snapshot = db.Column(db.Float, nullable=True)
    
    order = db.relationship('Order', back_populates='items')
    product = db.relationship('Product', back_populates='order_items')
    
    __table_args__ = (
        db.CheckConstraint('quantity > 0', name='check_quantity_positive'),
    )
    
    @property
    def line_total(self):
        return self.quantity * self.unit_price
    
    def __repr__(self):
        return f"<OrderItem {self.quantity}x Product {self.product_id}>"

class Media(db.Model, TimestampMixin):
    """Media library for uploaded files."""
    __tablename__ = 'media'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, default=0)
    mime_type = db.Column(db.String(100), nullable=True)
    alt_text = db.Column(db.String(255), nullable=True)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    @property
    def human_size(self):
        size = self.file_size or 0
        if size == 0:
            return "0 B"
        units = ['B', 'KB', 'MB', 'GB']
        idx = min(int(math.log(max(size, 1), 1024)), len(units) - 1)
        size = size / (1024 ** idx)
        return f"{size:.1f} {units[idx]}"
    
    def __repr__(self):
        return f"<Media {self.filename}>"


class HeroSlide(db.Model, TimestampMixin):
    __tablename__ = 'hero_slides'
    
    id = db.Column(db.Integer, primary_key=True)
    title_ka = db.Column(db.String(200), nullable=False)
    title_en = db.Column(db.String(200), nullable=False)
    subtitle_ka = db.Column(db.String(200), nullable=True)
    subtitle_en = db.Column(db.String(200), nullable=True)
    image = db.Column(db.String(255), nullable=False)
    badge = db.Column(db.String(50), nullable=True)
    discount_text = db.Column(db.String(100), nullable=True)
    installment_text = db.Column(db.String(200), nullable=True)
    button_text_ka = db.Column(db.String(50), default='ყიდვა')
    button_text_en = db.Column(db.String(50), default='Buy Now')
    button_url = db.Column(db.String(255), default='#')
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    
    def title(self, lang='en'):
        return self.title_en if lang == 'en' else self.title_ka
    
    def subtitle(self, lang='en'):
        return self.subtitle_en if lang == 'en' else self.subtitle_ka
    
    def button_text(self, lang='en'):
        return self.button_text_en if lang == 'en' else self.button_text_ka
    
    def __repr__(self):
        return f"<HeroSlide {self.title_en}>"

class Coupon(db.Model, TimestampMixin):
    __tablename__ = 'coupons'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    type = db.Column(db.String(20), default='percentage')  # percentage, fixed_amount
    value = db.Column(db.Float, nullable=False)
    max_uses = db.Column(db.Integer, nullable=True)
    used_count = db.Column(db.Integer, default=0)
    min_order = db.Column(db.Float, default=0)
    expires_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    @property
    def is_expired(self):
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return True
        return False
    
    @property
    def is_valid(self):
        if not self.is_active:
            return False
        if self.is_expired:
            return False
        if self.max_uses and self.used_count >= self.max_uses:
            return False
        return True
    
    @property
    def display_value(self):
        if self.type == 'percentage':
            return f"{int(self.value)}%"
        return f"{self.value:.2f}"
    
    def __repr__(self):
        return f"<Coupon {self.code}>"


class MegaGroup(db.Model, TimestampMixin):
    __tablename__ = 'mega_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    title_ka = db.Column(db.String(100), nullable=False)
    title_en = db.Column(db.String(100), nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    
    category = db.relationship('Category', backref=db.backref('mega_groups', lazy='dynamic',
                              cascade='all, delete-orphan'))
    items = db.relationship('MegaItem', back_populates='group', lazy='dynamic',
                            cascade='all, delete-orphan')
    
    
    def title(self, lang='en'):
        return self.title_en if lang == 'en' else self.title_ka
    
    def __repr__(self):
        return f"<MegaGroup {self.title_en}>"


class MegaItem(db.Model, TimestampMixin):
    __tablename__ = 'mega_items'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('mega_groups.id'), nullable=False)
    title_ka = db.Column(db.String(100), nullable=False)
    title_en = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    
    group = db.relationship('MegaGroup', back_populates='items')
    
    def title(self, lang='en'):
        return self.title_en if lang == 'en' else self.title_ka
    
    def __repr__(self):
        return f"<MegaItem {self.title_en}>"

