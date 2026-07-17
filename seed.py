import re
import os
from extensions import db
from app.models import User, Category, Subcategory, MegaGroup, MegaItem, Brand, Product
from app.utils.products_data import PRODUCTS

SUPER_ADMIN_EMAIL = os.environ.get("SUPER_ADMIN_EMAIL", "admin@test.com")
SUPER_ADMIN_DEFAULT_PASSWORD = os.environ.get("SUPER_ADMIN_PASSWORD", "fallback-password-123")


CATEGORIES = [
    ("mobile-phones", "bi-phone", "მობილური ტელეფონები", "Mobile Phones"),
    ("tablets", "bi-tablet", "ტაბლეტები", "Tablets"),
    ("smart-watches", "bi-smartwatch", "სმარტ საათები", "Smart Watches"),
    ("laptops", "bi-laptop", "ლეპტოპები", "Laptops"),
    ("audio-systems", "bi-headphones", "აუდიო სისტემები", "Audio Systems"),
    ("gaming", "bi-controller", "გეიმინგი", "Gaming"),
    ("tv-monitors", "bi-tv", "ტელევიზორები და მონიტორები", "TV & Monitors"),
    ("photo-video", "bi-camera", "ფოტო და ვიდეო", "Photo & Video"),
    ("beauty", "bi-brush", "სილამაზე", "Beauty"),
    ("accessories", "bi-bag", "აქსესუარები", "Accessories"),
]

SUBCATEGORIES = {
    "mobile-phones": [
        ("smartphones", "სმარტფონები", "Smartphones"),
        ("brands", "მობილურის ბრენდები", "Mobile Brands"),
        ("wireless-chargers", "უსადენო დამტენები", "Wireless Chargers"),
        ("headphones", "ყურსასმენები", "Headphones"),
        ("mobile-cases", "მობილურის ჩასადებები", "Mobile Cases"),
        ("smart-watches", "სმარტ საათები", "Smart Watches"),
    ],
    "tablets": [
        ("ipads", "iPad", "iPad"),
        ("android-tablets", "Android ტაბლეტები", "Android Tablets"),
        ("brands", "ბრენდები", "Brands"),
        ("hub-adapters", "HUB გადამყვანები", "HUB Adapters"),
        ("charging-adapters", "დამტენი ადაპტერი", "Charging Adapters"),
        ("cables", "კაბელები", "Cables"),
        ("power-banks", "Power Banks", "Power Banks"),
    ],
    "smart-watches": [
        ("smartwatches", "სმარტ საათები", "Smartwatches"),
        ("brands", "ბრენდები", "Brands"),
        ("charging-adapters", "დამტენი ადაპტერი", "Charging Adapters"),
        ("wireless-chargers", "უსადენო დამტენები", "Wireless Chargers"),
        ("power-banks", "Power Banks", "Power Banks"),
        ("accessories", "აქსესუარები", "Accessories"),
    ],
    "laptops": [
        ("classic", "კლასიკური ლეპტოპები", "Classic Laptops"),
        ("business", "ბიზნეს ლეპტოპები", "Business Laptops"),
        ("brands", "ბრენდები", "Brands"),
        ("gaming-laptops", "Gaming ლეპტოპები", "Gaming Laptops"),
        ("laptop-type", "ლეპტოპის ტიპი", "Laptop Type"),
        ("laptop-bags", "ლეპტოპის ჩანთები", "Laptop Bags"),
        ("headphones", "ყურსასმენები", "Headphones"),
        ("storage", "მეხსიერება", "Storage"),
    ],
    "audio-systems": [
        ("earbuds", "ყურსასმენები (Earbuds)", "Earbuds"),
        ("portable-speakers", "პორტატული დინამიკები", "Portable Speakers"),
        ("brands", "ბრენდები", "Brands"),
        ("headphones", "ყურსასმენები", "Headphones"),
        ("audio-equipment", "აუდიო ტექნიკა", "Audio Equipment"),
        ("microphones", "მიკროფონები", "Microphones"),
        ("accessories", "აქსესუარები", "Accessories"),
    ],
    "gaming": [
        ("consoles", "კონსოლები", "Consoles"),
        ("controllers", "კონტროლერები", "Controllers"),
        ("playstation", "PlayStation", "PlayStation"),
        ("xbox", "XBOX", "XBOX"),
        ("nintendo", "Nintendo", "Nintendo"),
        ("portable-vr", "პორტატული & VR", "Portable & VR"),
        ("gaming-monitors", "Gaming მონიტორები", "Gaming Monitors"),
        ("gaming-chairs", "სავარძლები", "Gaming Chairs"),
        ("gaming-desks", "მაგიდები", "Gaming Desks"),
        ("gaming-accessories", "გეიმინგ აქსესუარები", "Gaming Accessories"),
    ],
    "tv-monitors": [
        ("tv", "ტელევიზორები", "TV"),
        ("projectors", "პროექტორები", "Projectors"),
        ("tv-stick", "TV Stick", "TV Stick"),
        ("projector-accessories", "პროექტორის აქსესუარები", "Projector Accessories"),
        ("monitors", "მონიტორები", "Monitors"),
    ],
    "photo-video": [
        ("cameras", "ფოტოაპარატები", "Cameras"),
        ("action-cameras", "ექშენ კამერები", "Action Cameras"),
        ("drones", "დრონები", "Drones"),
        ("smart-glasses", "სმარტ სათვალეები", "Smart Glasses"),
        ("photo-printers", "ფოტო პრინტერები", "Photo Printers"),
        ("smartphone-photography", "Smartphone ფოტოგრაფია", "Smartphone Photography"),
        ("power-banks", "Power Banks", "Power Banks"),
        ("photo-video-accessories", "ფოტო | ვიდეო აქსესუარები", "Photo | Video Accessories"),
    ],
    "beauty": [
        ("hair-care", "თმის მოვლა", "Hair Care"),
        ("hair-dryers", "თმის ფენი", "Hair Dryers"),
        ("beard-care", "წვერის მოვლა", "Beard Care"),
        ("sports-fitness", "სპორტი", "Sports & Fitness"),
        ("personal-care", "თავის მოვლა", "Personal Care"),
        ("climate-control", "კლიმატის მართვა", "Climate Control"),
        ("clothing-care", "ტანსაცმლის მოვლა", "Clothing Care"),
    ],
    "accessories": [
        ("screen-protectors", "მობილურის ეკრანის დამცავები", "Phone Screen Protectors"),
        ("phone-cases", "მობილურის ჩასადებები", "Phone Cases"),
        ("wireless-chargers", "უსადენო დამტენები", "Wireless Chargers"),
        ("power-banks", "Power Banks", "Power Banks"),
        ("cables", "კაბელები", "Cables"),
        ("charging-adapters", "დამტენი ადაპტერი", "Charging Adapters"),
        ("laptop-accessories", "ლეპტოპის აქსესუარები", "Laptop Accessories"),
        ("tablet-accessories", "ტაბის აქსესუარები", "Tablet Accessories"),
    ],
}

MEGA_MENU_DATA = {
    "mobile-phones": [
        (
            "მობილურის ბრენდები", "Mobile Brands",
            [
                ("Apple", "Apple", "/products?category=mobile-phones&brand=Apple"),
                ("Samsung", "Samsung", "/products?category=mobile-phones&brand=Samsung"),
                ("Xiaomi", "Xiaomi", "/products?category=mobile-phones&brand=Xiaomi"),
                ("Google", "Google", "/products?category=mobile-phones&brand=Google"),
                ("Realme", "Realme", "/products?category=mobile-phones&brand=Realme"),
                ("OnePlus", "OnePlus", "/products?category=mobile-phones&brand=OnePlus"),
                ("Blackview", "Blackview", "/products?category=mobile-phones&brand=Blackview"),
                ("Vivo", "Vivo", "/products?category=mobile-phones&brand=Vivo"),
                ("Motorola", "Motorola", "/products?category=mobile-phones&brand=Motorola"),
                ("Nokia", "Nokia", "/products?category=mobile-phones&brand=Nokia")
            ]
        ),
        (
            "უსადენო დამტენები", "Wireless Chargers",
            [
                ("Apple Chargers", "Apple Chargers", "/products?category=accessories&subcategory=wireless-chargers&brand=Apple"),
                ("Samsung Chargers", "Samsung Chargers", "/products?category=accessories&subcategory=wireless-chargers&brand=Samsung"),
                ("Xiaomi Chargers", "Xiaomi Chargers", "/products?category=accessories&subcategory=wireless-chargers&brand=Xiaomi"),
                ("Havit Chargers", "Havit Chargers", "/products?category=accessories&subcategory=wireless-chargers&brand=Havit"),
                ("Anker Chargers", "Anker Chargers", "/products?category=accessories&subcategory=wireless-chargers&brand=Anker"),
                ("Hoco Chargers", "Hoco Chargers", "/products?category=accessories&subcategory=wireless-chargers&brand=Hoco"),
                ("Baseus", "Baseus", "/products?category=accessories&subcategory=wireless-chargers&brand=Baseus"),
                ("Ecoflow Chargers", "Ecoflow Chargers", "/products?category=accessories&subcategory=wireless-chargers&brand=Ecoflow"),
                ("Belkin Chargers", "Belkin Chargers", "/products?category=accessories&subcategory=wireless-chargers&brand=Belkin"),
                ("Ugreen Chargers", "Ugreen Chargers", "/products?category=accessories&subcategory=wireless-chargers&brand=Ugreen")
            ]
        ),
        (
            "ყურსასმენები", "Headphones",
            [
                ("Apple AirPods", "Apple AirPods", "/products?category=audio-systems&subcategory=earbuds&brand=Apple"),
                ("Samsung Galaxy Buds", "Samsung Galaxy Buds", "/products?category=audio-systems&subcategory=earbuds&brand=Samsung"),
                ("OnePlus Buds", "OnePlus Buds", "/products?category=audio-systems&subcategory=earbuds&brand=OnePlus"),
                ("Sony", "Sony", "/products?category=audio-systems&subcategory=headphones&brand=Sony"),
                ("Xiaomi", "Xiaomi", "/products?category=audio-systems&subcategory=earbuds&brand=Xiaomi"), # შეიცვალა earbuds-ით
                ("Google Pixel Buds", "Google Pixel Buds", "/products?category=audio-systems&subcategory=earbuds&brand=Google"),
                ("Realme Buds", "Realme Buds", "/products?category=audio-systems&subcategory=earbuds&brand=Realme"),
                ("Nothing Buds", "Nothing Buds", "/products?category=audio-systems&subcategory=earbuds&brand=Nothing"),
                ("JBL", "JBL", "/products?category=audio-systems&subcategory=earbuds&brand=JBL"), # შეიცვალა earbuds-ით
                ("Bose", "Bose", "/products?category=audio-systems&subcategory=earbuds&brand=Bose"), # შეიცვალა earbuds-ით
                ("Marshall", "Marshall", "/products?category=audio-systems&subcategory=earbuds&brand=Marshall"), # შეიცვალა earbuds-ით
                ("ყველას ნახვა", "View All", "/products?category=audio-systems")
            ]
        ),
        (
            "მობილურის ჩასადებები", "Mobile Cases",
            [
                ("For Apple", "For Apple", "/products?category=accessories&subcategory=phone-cases&brand=Apple"),
                ("For Samsung", "For Samsung", "/products?category=accessories&subcategory=phone-cases&brand=Samsung"),
                ("For Xiaomi", "For Xiaomi", "/products?category=accessories&subcategory=phone-cases&brand=Xiaomi"),
                ("For OnePlus", "For OnePlus", "/products?category=accessories&subcategory=phone-cases&brand=OnePlus"),
                ("For Realme", "For Realme", "/products?category=accessories&subcategory=phone-cases&brand=Realme"),
                ("For Google", "For Google", "/products?category=accessories&subcategory=phone-cases&brand=Google"),
                ("For Motorola", "For Motorola", "/products?category=accessories&subcategory=phone-cases&brand=Motorola"),
                ("For Oppo", "For Oppo", "/products?category=accessories&subcategory=phone-cases&brand=Oppo")
            ]
        ),
        (
            "სმარტ საათები", "Smart Watches",
            [
                ("Apple Watch", "Apple Watch", "/products?category=smart-watches&brand=Apple"),
                ("Samsung Galaxy Watch", "Samsung Galaxy Watch", "/products?category=smart-watches&brand=Samsung"),
                ("Xiaomi Mi Watch", "Xiaomi Mi Watch", "/products?category=smart-watches&brand=Xiaomi"),
                ("Google Watch", "Google Watch", "/products?category=smart-watches&brand=Google"),
                ("Amazfit", "Amazfit", "/products?category=smart-watches&brand=Amazfit"),
                ("Garmin", "Garmin", "/products?category=smart-watches&brand=Garmin"),
                ("OnePlus Watch", "OnePlus Watch", "/products?category=smart-watches&brand=OnePlus"),
                ("Nothing Watch", "Nothing Watch", "/products?category=smart-watches&brand=Nothing"),
                ("Fossil Gen 6", "Fossil Gen 6", "/products?category=smart-watches&brand=Fossil")
            ]
        ),
    ],
    "tablets": [
        (
            "ბრენდები", "Brands",
            [
                ("Apple", "Apple", "/products?category=tablets&brand=Apple"),
                ("Samsung", "Samsung", "/products?category=tablets&brand=Samsung"),
                ("Xiaomi", "Xiaomi", "/products?category=tablets&brand=Xiaomi"),
                ("Honor", "Honor", "/products?category=tablets&brand=Honor"),
                ("Lenovo", "Lenovo", "/products?category=tablets&brand=Lenovo"),
                ("Blackview", "Blackview", "/products?category=tablets&brand=Blackview"),
                ("Realme", "Realme", "/products?category=tablets&brand=Realme"),
                ("OnePlus", "OnePlus", "/products?category=tablets&brand=OnePlus"),
                ("ZTE", "ZTE", "/products?category=tablets&brand=ZTE"),
            ]
        ),
        (
            "HUB გადამყვანები", "HUB Adapters",
            [
                ("Anker", "Anker", "/products?category=tablets&subcategory=hub-adapters&brand=Anker"),
                ("Xiaomi", "Xiaomi", "/products?category=tablets&subcategory=hub-adapters&brand=Xiaomi"),
                ("Baseus", "Baseus", "/products?category=tablets&subcategory=hub-adapters&brand=Baseus"),
                ("Apple", "Apple", "/products?category=tablets&subcategory=hub-adapters&brand=Apple"),
                ("Havit", "Havit", "/products?category=tablets&subcategory=hub-adapters&brand=Havit"),
                ("TP-Link", "TP-Link", "/products?category=tablets&subcategory=hub-adapters&brand=TP-Link"),
                ("Belkin", "Belkin", "/products?category=tablets&subcategory=hub-adapters&brand=Belkin"),
                ("Ugreen", "Ugreen", "/products?category=tablets&subcategory=hub-adapters&brand=Ugreen"),
                ("ყველას ნახვა", "View All", "/products?category=tablets&subcategory=hub-adapters"),
            ]
        ),
        (
            "დამტენი ადაპტერი", "Charging Adapters",
            [
                ("Apple Adapter", "Apple Adapter", "/products?category=accessories&subcategory=charging-adapters&brand=Apple"),
                ("Samsung Adapter", "Samsung Adapter", "/products?category=accessories&subcategory=charging-adapters&brand=Samsung"),
                ("Anker Adapter", "Anker Adapter", "/products?category=accessories&subcategory=charging-adapters&brand=Anker"),
                ("Spigen Adapter", "Spigen Adapter", "/products?category=accessories&subcategory=charging-adapters&brand=Spigen"),
                ("Belkin Adapter", "Belkin Adapter", "/products?category=accessories&subcategory=charging-adapters&brand=Belkin"),
                ("Ugreen Adapter", "Ugreen Adapter", "/products?category=accessories&subcategory=charging-adapters&brand=Ugreen"),
                ("Xiaomi Adapter", "Xiaomi Adapter", "/products?category=accessories&subcategory=charging-adapters&brand=Xiaomi"),
                ("Baseus Adapter", "Baseus Adapter", "/products?category=accessories&subcategory=charging-adapters&brand=Baseus"),
                ("ყველას ნახვა", "View All", "/products?category=accessories&subcategory=charging-adapters"),
            ]
        ),
        (
            "კაბელები", "Cables",
            [
                ("Lightning", "Lightning", "/products?category=accessories&subcategory=cables&type=lightning"),
                ("Micro USB", "Micro USB", "/products?category=accessories&subcategory=cables&type=micro-usb"),
                ("Type-C", "Type-C", "/products?category=accessories&subcategory=cables&type=type-c"),
                ("Aux", "Aux", "/products?category=accessories&subcategory=cables&type=aux"),
                ("ყველას ნახვა", "View All", "/products?category=accessories&subcategory=cables"),
            ]
        ),
        (
            "Power Banks", "Power Banks",
            [
                ("Anker", "Anker", "/products?category=accessories&subcategory=power-banks&brand=Anker"),
                ("Ugreen", "Ugreen", "/products?category=accessories&subcategory=power-banks&brand=Ugreen"),
                ("Xiaomi", "Xiaomi", "/products?category=accessories&subcategory=power-banks&brand=Xiaomi"),
                ("Lenovo", "Lenovo", "/products?category=accessories&subcategory=power-banks&brand=Lenovo"),
                ("EcoFlow", "EcoFlow", "/products?category=accessories&subcategory=power-banks&brand=EcoFlow"),
                ("Belkin", "Belkin", "/products?category=accessories&subcategory=power-banks&brand=Belkin"),
                ("Samsung", "Samsung", "/products?category=accessories&subcategory=power-banks&brand=Samsung"),
                ("ყველას ნახვა", "View All", "/products?category=accessories&subcategory=power-banks"),
            ]
        ),
    ],
    "smart-watches": [
        (
            "ბრენდები", "Brands",
            [
                ("Apple", "Apple", "/products?category=smart-watches&brand=Apple"),
                ("Samsung", "Samsung", "/products?category=smart-watches&brand=Samsung"),
                ("Xiaomi", "Xiaomi", "/products?category=smart-watches&brand=Xiaomi"),
                ("Google", "Google", "/products?category=smart-watches&brand=Google"),
                ("Amazfit", "Amazfit", "/products?category=smart-watches&brand=Amazfit"),
                ("Garmin", "Garmin", "/products?category=smart-watches&brand=Garmin"),
                ("Nothing", "Nothing", "/products?category=smart-watches&brand=Nothing"),
                ("OnePlus", "OnePlus", "/products?category=smart-watches&brand=OnePlus"),
                ("ყველას ნახვა", "View All", "/products?category=smart-watches"),
            ]
        ),
        (
            "დამტენი ადაპტერი", "Charging Adapters",
            [
                ("Apple", "Apple", "/products?category=smart-watches&subcategory=charging-adapters&brand=Apple"),
                ("Samsung", "Samsung", "/products?category=smart-watches&subcategory=charging-adapters&brand=Samsung"),
                ("Xiaomi", "Xiaomi", "/products?category=smart-watches&subcategory=charging-adapters&brand=Xiaomi"),
                ("Spigen", "Spigen", "/products?category=smart-watches&subcategory=charging-adapters&brand=Spigen"),
                ("Anker", "Anker", "/products?category=smart-watches&subcategory=charging-adapters&brand=Anker"),
                ("Ugreen", "Ugreen", "/products?category=smart-watches&subcategory=charging-adapters&brand=Ugreen"),
                ("Belkin", "Belkin", "/products?category=smart-watches&subcategory=charging-adapters&brand=Belkin"),
                ("Baseus", "Baseus", "/products?category=smart-watches&subcategory=charging-adapters&brand=Baseus"),
                ("ყველას ნახვა", "View All", "/products?category=smart-watches&subcategory=charging-adapters"),
            ]
        ),
        (
            "უსადენო დამტენები", "Wireless Chargers",
            [
                ("Apple", "Apple", "/products?category=accessories&subcategory=wireless-chargers&brand=Apple"),
                ("Samsung", "Samsung", "/products?category=accessories&subcategory=wireless-chargers&brand=Samsung"),
                ("Xiaomi", "Xiaomi", "/products?category=accessories&subcategory=wireless-chargers&brand=Xiaomi"),
                ("Anker", "Anker", "/products?category=accessories&subcategory=wireless-chargers&brand=Anker"),
                ("Belkin", "Belkin", "/products?category=accessories&subcategory=wireless-chargers&brand=Belkin"),
                ("Havit", "Havit", "/products?category=accessories&subcategory=wireless-chargers&brand=Havit"),
                ("Hoco", "Hoco", "/products?category=accessories&subcategory=wireless-chargers&brand=Hoco"),
                ("Ugreen", "Ugreen", "/products?category=accessories&subcategory=wireless-chargers&brand=Ugreen"),
                ("ყველას ნახვა", "View All", "/products?category=accessories&subcategory=wireless-chargers"),
            ]
        ),
        (
            "Power Banks", "Power Banks",
            [
                ("Belkin", "Belkin", "/products?category=accessories&subcategory=power-banks&brand=Belkin"),
                ("Xiaomi", "Xiaomi", "/products?category=accessories&subcategory=power-banks&brand=Xiaomi"),
                ("Anker", "Anker", "/products?category=accessories&subcategory=power-banks&brand=Anker"),
                ("EcoFlow", "EcoFlow", "/products?category=accessories&subcategory=power-banks&brand=EcoFlow"),
                ("Ugreen", "Ugreen", "/products?category=accessories&subcategory=power-banks&brand=Ugreen"),
                ("Lenovo", "Lenovo", "/products?category=accessories&subcategory=power-banks&brand=Lenovo"),
                ("Samsung", "Samsung", "/products?category=accessories&subcategory=power-banks&brand=Samsung"),
                ("ყველას ნახვა", "View All", "/products?category=accessories&subcategory=power-banks"),
            ]
        ),
        (
            "აქსესუარები", "Accessories",
            [
                ("ეკრანის დამცავები", "Screen Protectors", "/products?category=smart-watches&subcategory=accessories&type=screen-protectors"),
                ("სამაჯურები", "Watch Bands", "/products?category=smart-watches&subcategory=accessories&type=bands"),
                ("ყველას ნახვა", "View All", "/products?category=smart-watches&subcategory=accessories"),
            ]
        ),
    ],
    "laptops": [
        (
            "ბრენდები", "Brands",
            [
                ("Apple", "Apple", "/products?category=laptops&brand=Apple"),
                ("HP", "HP", "/products?category=laptops&brand=HP"),
                ("Asus", "Asus", "/products?category=laptops&brand=Asus"),
                ("Acer", "Acer", "/products?category=laptops&brand=Acer"),
                ("Lenovo", "Lenovo", "/products?category=laptops&brand=Lenovo"),
                ("ყველას ნახვა", "View All", "/products?category=laptops"),
            ]
        ),
        (
            "Gaming ლეპტოპები", "Gaming Laptops",
            [
                ("HP Victus | OMEN", "HP Victus | OMEN", "/products?category=laptops&subcategory=gaming-laptops&brand=HP"),
                ("ACER Nitro | Predator", "ACER Nitro | Predator", "/products?category=laptops&subcategory=gaming-laptops&brand=Acer"),
                ("Dell Inspiron | Alienware", "Dell Inspiron | Alienware", "/products?category=laptops&subcategory=gaming-laptops&brand=Dell"),
                ("Lenovo LEGION | LOQ", "Lenovo LEGION | LOQ", "/products?category=laptops&subcategory=gaming-laptops&brand=Lenovo"),
                ("ASUS ROG | TUF", "ASUS ROG | TUF", "/products?category=laptops&subcategory=gaming-laptops&brand=Asus"),
                ("MSI Katana | Crosshair", "MSI Katana | Crosshair", "/products?category=laptops&subcategory=gaming-laptops&brand=MSI"),
                ("ყველას ნახვა", "View All", "/products?category=laptops&subcategory=gaming-laptops"),
            ]
        ),
        (
            "ლეპტოპის ტიპი", "Laptop Type",
            [
                ("Classic", "Classic", "/products?category=laptops&subcategory=classic"),
                ("Business", "Business", "/products?category=laptops&subcategory=business"),
                ("Gaming", "Gaming", "/products?category=laptops&subcategory=gaming-laptops"),
                ("მონიტორები", "Monitors", "/products?category=tv-monitors&subcategory=monitors"),
                ("პროექტორები", "Projectors", "/products?category=tv-monitors&subcategory=projectors"),
                ("პრინტერები", "Printers", "/products?category=photo-video&subcategory=photo-printers"),
                ("მაგიდები", "Desks", "/products?category=gaming&subcategory=gaming-desks"),
                ("ყველას ნახვა", "View All", "/products?category=laptops"),
            ]
        ),
        (
            "ლეპტოპის ჩანთები", "Laptop Bags",
            [
                ("BackPack", "BackPack", "/products?category=laptops&subcategory=laptop-bags&type=backpack"),
                ("Briefcase", "Briefcase", "/products?category=laptops&subcategory=laptop-bags&type=briefcase"),
                ("Sleeve", "Sleeve", "/products?category=laptops&subcategory=laptop-bags&type=sleeve"),
                ("Shoulder Strap", "Shoulder Strap", "/products?category=laptops&subcategory=laptop-bags&type=shoulder"),
                ("ყველას ნახვა", "View All", "/products?category=laptops&subcategory=laptop-bags"),
            ]
        ),
        (
            "ყურსასმენები", "Headphones",
            [
                ("Headphones", "Headphones", "/products?category=audio-systems&subcategory=headphones&type=headphones"),
                ("Buds", "Buds", "/products?category=audio-systems&subcategory=headphones&type=buds"),
                ("Earphones", "Earphones", "/products?category=audio-systems&subcategory=headphones&type=earphones"),
                ("ყველას ნახვა", "View All", "/products?category=audio-systems&subcategory=headphones"),
            ]
        ),
        (
            "მეხსიერება", "Storage",
            [
                ("პორტატული SSD", "Portable SSD", "/products?category=laptops&subcategory=storage&type=portable-ssd"),
                ("პორტატული HDD", "Portable HDD", "/products?category=laptops&subcategory=storage&type=portable-hdd"),
                ("შიდა SSD", "Internal SSD", "/products?category=laptops&subcategory=storage&type=internal-ssd"),
                ("ფლეშ მეხსიერებები", "Flash Memory", "/products?category=laptops&subcategory=storage&type=flash"),
                ("მეხსიერების ბარათები", "Memory Cards", "/products?category=laptops&subcategory=storage&type=memory-cards"),
                ("ყველას ნახვა", "View All", "/products?category=laptops&subcategory=storage"),
            ]
        ),
    ],
    "audio-systems": [
        (
            "ბრენდები", "Brands",
            [
                ("Apple", "Apple", "/products?category=audio-systems&brand=Apple"),
                ("Samsung", "Samsung", "/products?category=audio-systems&brand=Samsung"),
                ("Xiaomi", "Xiaomi", "/products?category=audio-systems&brand=Xiaomi"),
                ("JBL", "JBL", "/products?category=audio-systems&brand=JBL"),
                ("Sony", "Sony", "/products?category=audio-systems&brand=Sony"),
                ("Bose", "Bose", "/products?category=audio-systems&brand=Bose"),
                ("Beats", "Beats", "/products?category=audio-systems&brand=Beats"),
                ("Realme", "Realme", "/products?category=audio-systems&brand=Realme"),
                ("Marshall", "Marshall", "/products?category=audio-systems&brand=Marshall"),
                ("ყველას ნახვა", "View All", "/products?category=audio-systems"),
            ]
        ),
        (
            "ყურსასმენები", "Headphones",
            [
                ("Headphones", "Headphones", "/products?category=audio-systems&subcategory=headphones&type=headphones"),
                ("Buds", "Buds", "/products?category=audio-systems&subcategory=earbuds"),
                ("Gaming", "Gaming", "/products?category=audio-systems&subcategory=headphones&type=gaming"),
                ("სპორტული", "Sports", "/products?category=audio-systems&subcategory=headphones&type=sport"),
                ("საბავშვო", "Kids", "/products?category=audio-systems&subcategory=headphones&type=kids"),
                ("ყველას ნახვა", "View All", "/products?category=audio-systems&subcategory=headphones"),
            ]
        ),
        (
            "აუდიო ტექნიკა", "Audio Equipment",
            [
                ("პორტატული დინამიკები", "Portable Speakers", "/products?category=audio-systems&subcategory=portable-speakers"),
                ("სახლის დინამიკები", "Home Speakers", "/products?category=audio-systems&subcategory=audio-equipment&type=home-speakers"),
                ("ფირსაკრავები", "Turntables", "/products?category=audio-systems&subcategory=audio-equipment&type=turntables"),
                ("სმარტ ასისტენტები", "Smart Assistants", "/products?category=audio-systems&subcategory=audio-equipment&type=smart-assistants"),
                ("Soundbar", "Soundbar", "/products?category=audio-systems&subcategory=audio-equipment&type=soundbar"),
                ("ყველას ნახვა", "View All", "/products?category=audio-systems&subcategory=audio-equipment"),
            ]
        ),
        (
            "მიკროფონები", "Microphones",
            [
                ("სტრიმინგ მიკროფონები", "Streaming Microphones", "/products?category=audio-systems&subcategory=microphones&type=streaming"),
                ("გეიმინგ მიკროფონები", "Gaming Microphones", "/products?category=audio-systems&subcategory=microphones&type=gaming"),
                ("ლაპელური მიკროფონები", "Lavalier Microphones", "/products?category=audio-systems&subcategory=microphones&type=lavalier"),
                ("უსადენო მიკროფონები", "Wireless Microphones", "/products?category=audio-systems&subcategory=microphones&type=wireless"),
                ("ფოტოაპარატის მიკროფონები", "Camera Microphones", "/products?category=audio-systems&subcategory=microphones&type=camera"),
                ("ყველას ნახვა", "View All", "/products?category=audio-systems&subcategory=microphones"),
            ]
        ),
        (
            "აქსესუარები", "Accessories",
            [
                ("Power Banks", "Power Banks", "/products?category=accessories&subcategory=power-banks"),
                ("დენის დამაგრძელებლები", "Power Extensions", "/products?category=audio-systems&subcategory=accessories&type=extensions"),
                ("კაბელები", "Cables", "/products?category=accessories&subcategory=cables"),
                ("უსადენო დამტენები", "Wireless Chargers", "/products?category=accessories&subcategory=wireless-chargers"),
                ("ყველას ნახვა", "View All", "/products?category=audio-systems&subcategory=accessories"),
            ]
        ),
    ],
    "gaming": [
        (
            "PlayStation", "PlayStation",
            [
                ("კონსოლი", "Console", "/products?category=gaming&subcategory=consoles&brand=Sony"),
                ("თამაშები", "Games", "/products?category=gaming&subcategory=playstation&type=games"),
                ("კონტროლერები", "Controllers", "/products?category=gaming&subcategory=controllers&brand=Sony"),
                ("აქსესუარები", "Accessories", "/products?category=gaming&subcategory=playstation&type=accessories"),
                ("PlayStation VR", "PlayStation VR", "/products?category=gaming&subcategory=portable-vr"),
                ("ყველას ნახვა", "View All", "/products?category=gaming&brand=Sony"),
            ]
        ),
        (
            "XBOX", "XBOX",
            [
                ("კონსოლი", "Console", "/products?category=gaming&subcategory=consoles&brand=Microsoft"),
                ("თამაშები", "Games", "/products?category=gaming&subcategory=xbox&type=games"),
                ("კონტროლერები", "Controllers", "/products?category=gaming&subcategory=controllers&brand=Microsoft"),
                ("აქსესუარები", "Accessories", "/products?category=gaming&subcategory=xbox&type=accessories"),
                ("ყველას ნახვა", "View All", "/products?category=gaming&brand=Microsoft"),
            ]
        ),
        (
            "Nintendo", "Nintendo",
            [
                ("კონსოლები", "Consoles", "/products?category=gaming&subcategory=consoles&brand=Nintendo"),
                ("თამაშები", "Games", "/products?category=gaming&subcategory=nintendo&type=games"),
                ("კონტროლერები", "Controllers", "/products?category=gaming&subcategory=controllers&brand=Nintendo"),
                ("აქსესუარები", "Accessories", "/products?category=gaming&subcategory=nintendo&type=accessories"),
                ("ყველას ნახვა", "View All", "/products?category=gaming&brand=Nintendo"),
            ]
        ),
        (
            "Gaming ლეპტოპები", "Gaming Laptops",
            [
                ("HP Pavilion | Victus | OMEN", "HP Pavilion | Victus | OMEN", "/products?category=laptops&subcategory=gaming-laptops&brand=HP"),
                ("ACER Nitro | Predator", "ACER Nitro | Predator", "/products?category=laptops&subcategory=gaming-laptops&brand=Acer"),
                ("Dell Inspiron | Alienware", "Dell Inspiron | Alienware", "/products?category=laptops&subcategory=gaming-laptops&brand=Dell"),
                ("Lenovo LEGION | LOQ", "Lenovo LEGION | LOQ", "/products?category=laptops&subcategory=gaming-laptops&brand=Lenovo"),
                ("ASUS ROG | TUF", "ASUS ROG | TUF", "/products?category=laptops&subcategory=gaming-laptops&brand=Asus"),
                ("MSI Katana | Crosshair", "MSI Katana | Crosshair", "/products?category=laptops&subcategory=gaming-laptops&brand=MSI"),
                ("ყველას ნახვა", "View All", "/products?category=laptops&subcategory=gaming-laptops"),
            ]
        ),
        (
            "პორტატული & VR", "Portable & VR",
            [
                ("Lenovo Legion Go S", "Lenovo Legion Go S", "/products?category=gaming&subcategory=portable-vr&type=legion-go"),
                ("Steam Deck", "Steam Deck", "/products?category=gaming&subcategory=portable-vr&type=steam-deck"),
                ("Asus Rog Ally", "Asus Rog Ally", "/products?category=gaming&subcategory=portable-vr&type=rog-ally"),
                ("Backbone", "Backbone", "/products?category=gaming&subcategory=portable-vr&type=backbone"),
                ("Meta Quest", "Meta Quest", "/products?category=gaming&subcategory=portable-vr&type=meta-quest"),
                ("VR სათვალის აქსესუარები", "VR Accessories", "/products?category=gaming&subcategory=portable-vr&type=accessories"),
                ("ყველას ნახვა", "View All", "/products?category=gaming&subcategory=portable-vr"),
            ]
        ),
        (
            "Gaming მონიტორები", "Gaming Monitors",
            [
                ("Acer", "Acer", "/products?category=gaming&subcategory=gaming-monitors&brand=Acer"),
                ("BenQ", "BenQ", "/products?category=gaming&subcategory=gaming-monitors&brand=BenQ"),
                ("AOC", "AOC", "/products?category=gaming&subcategory=gaming-monitors&brand=AOC"),
                ("MSI", "MSI", "/products?category=gaming&subcategory=gaming-monitors&brand=MSI"),
                ("Dell", "Dell", "/products?category=gaming&subcategory=gaming-monitors&brand=Dell"),
                ("HP", "HP", "/products?category=gaming&subcategory=gaming-monitors&brand=HP"),
                ("Xiaomi", "Xiaomi", "/products?category=gaming&subcategory=gaming-monitors&brand=Xiaomi"),
                ("ყველას ნახვა", "View All", "/products?category=gaming&subcategory=gaming-monitors"),
            ]
        ),
        (
            "სავარძლები", "Gaming Chairs",
            [
                ("Razer", "Razer", "/products?category=gaming&subcategory=gaming-chairs&brand=Razer"),
                ("Havit", "Havit", "/products?category=gaming&subcategory=gaming-chairs&brand=Havit"),
                ("ყველას ნახვა", "View All", "/products?category=gaming&subcategory=gaming-chairs"),
            ]
        ),
        (
            "მაგიდები", "Gaming Desks",
            [
                ("Xiaomi", "Xiaomi", "/products?category=gaming&subcategory=gaming-desks&brand=Xiaomi"),
                ("2E", "2E", "/products?category=gaming&subcategory=gaming-desks&brand=2E"),
                ("ყველას ნახვა", "View All", "/products?category=gaming&subcategory=gaming-desks"),
            ]
        ),
        (
            "გეიმინგ აქსესუარები", "Gaming Accessories",
            [
                ("ყურსასმენები", "Headphones", "/products?category=audio-systems&subcategory=headphones&type=gaming"),
                ("მაუსები", "Gaming Mouses", "/products?category=gaming&type=mouse"),
                ("კლავიატურები", "Keyboards", "/products?category=gaming&subcategory=gaming-accessories&type=keyboards"),
                ("სათამაშო საჭეები", "Gaming Wheels", "/products?category=gaming&subcategory=gaming-accessories&type=wheels"),
                ("გამაგრილებელი პედები", "Cooling Pads", "/products?category=gaming&subcategory=gaming-accessories&type=cooling-pads"),
                ("დინამიკები", "Speakers", "/products?category=gaming&subcategory=gaming-accessories&type=speakers"),
                ("სტრიმინგ მიკროფონები", "Streaming Microphones", "/products?category=audio-systems&subcategory=microphones&type=streaming"),
                ("ყველას ნახვა", "View All", "/products?category=gaming&subcategory=gaming-accessories"),
            ]
        ),
    ],
    "tv-monitors": [
        (
            "ტელევიზორები", "TV",
            [
                ("Samsung", "Samsung", "/products?category=tv-monitors&subcategory=tv&brand=Samsung"),
                ("Xiaomi", "Xiaomi", "/products?category=tv-monitors&subcategory=tv&brand=Xiaomi"),
                ("Sony", "Sony", "/products?category=tv-monitors&subcategory=tv&brand=Sony"),
                ("LG", "LG", "/products?category=tv-monitors&subcategory=tv&brand=LG"),
                ("TCL", "TCL", "/products?category=tv-monitors&subcategory=tv&brand=TCL"),
                ("Toshiba", "Toshiba", "/products?category=tv-monitors&subcategory=tv&brand=Toshiba"),
                ("ტელევიზორის საკიდები", "TV Mounts", "/products?category=tv-monitors&subcategory=tv&type=tv-mounts"),
                ("TV Soundbar", "TV Soundbar", "/products?category=audio-systems&subcategory=audio-equipment&type=soundbar"),
                ("ყველას ნახვა", "View All", "/products?category=tv-monitors&subcategory=tv"),
            ]
        ),
        (
            "პროექტორები", "Projectors",
            [
                ("XGIMI", "XGIMI", "/products?category=tv-monitors&subcategory=projectors&brand=XGIMI"),
                ("Xiaomi", "Xiaomi", "/products?category=tv-monitors&subcategory=projectors&brand=Xiaomi"),
                ("Wanbo", "Wanbo", "/products?category=tv-monitors&subcategory=projectors&brand=Wanbo"),
                ("Aurzen", "Aurzen", "/products?category=tv-monitors&subcategory=projectors&brand=Aurzen"),
                ("Epson", "Epson", "/products?category=tv-monitors&subcategory=projectors&brand=Epson"),
                ("BenQ", "BenQ", "/products?category=tv-monitors&subcategory=projectors&brand=BenQ"),
                ("ყველას ნახვა", "View All", "/products?category=tv-monitors&subcategory=projectors"),
            ]
        ),
        (
            "TV Stick", "TV Stick",
            [
                ("Xiaomi TV", "Xiaomi TV", "/products?category=tv-monitors&subcategory=tv-stick&brand=Xiaomi"),
                ("Apple TV", "Apple TV", "/products?category=tv-monitors&subcategory=tv-stick&brand=Apple"),
                ("Amazon Fire TV Stick", "Amazon Fire TV Stick", "/products?category=tv-monitors&subcategory=tv-stick&brand=Amazon"),
                ("ყველას ნახვა", "View All", "/products?category=tv-monitors&subcategory=tv-stick"),
            ]
        ),
        (
            "პროექტორის აქსესუარები", "Projector Accessories",
            [
                ("პროექტორის დაფები", "Projector Screens", "/products?category=tv-monitors&subcategory=projector-accessories&type=projector-screens"),
                ("პროექტორის Tripod", "Projector Tripod", "/products?category=tv-monitors&subcategory=projector-accessories&type=projector-tripod"),
                ("პრეზენტერები", "Presenters", "/products?category=tv-monitors&subcategory=projector-accessories&type=presenters"),
                ("პროექტორის ჩანთა", "Projector Bag", "/products?category=tv-monitors&subcategory=projector-accessories&type=projector-bag"),
                ("ყველას ნახვა", "View All", "/products?category=tv-monitors&subcategory=projector-accessories"),
            ]
        ),
        (
            "მონიტორები", "Monitors",
            [
                ("Samsung", "Samsung", "/products?category=tv-monitors&subcategory=monitors&brand=Samsung"),
                ("DELL", "DELL", "/products?category=tv-monitors&subcategory=monitors&brand=Dell"),
                ("BenQ", "BenQ", "/products?category=tv-monitors&subcategory=monitors&brand=BenQ"),
                ("Lenovo", "Lenovo", "/products?category=tv-monitors&subcategory=monitors&brand=Lenovo"),
                ("AOC", "AOC", "/products?category=tv-monitors&subcategory=monitors&brand=AOC"),
                ("HP", "HP", "/products?category=tv-monitors&subcategory=monitors&brand=HP"),
                ("Xiaomi", "Xiaomi", "/products?category=tv-monitors&subcategory=monitors&brand=Xiaomi"),
                ("ყველას ნახვა", "View All", "/products?category=tv-monitors&subcategory=monitors"),
            ]
        ),
    ],
    "photo-video": [
        (
            "ფოტოაპარატები", "Cameras",
            [
                ("Canon", "Canon", "/products?category=photo-video&subcategory=cameras&brand=Canon"),
                ("Nikon", "Nikon", "/products?category=photo-video&subcategory=cameras&brand=Nikon"),
                ("Sony", "Sony", "/products?category=photo-video&subcategory=cameras&brand=Sony"),
                ("ყველას ნახვა", "View All", "/products?category=photo-video&subcategory=cameras"),
            ]
        ),
        (
            "ექშენ კამერები", "Action Cameras",
            [
                ("GoPro", "GoPro", "/products?category=photo-video&subcategory=action-cameras&brand=GoPro"),
                ("DJI Osmo", "DJI Osmo", "/products?category=photo-video&subcategory=action-cameras&brand=DJI"),
                ("Insta360", "Insta360", "/products?category=photo-video&subcategory=action-cameras&brand=Insta360"),
                ("აქსესუარები", "Accessories", "/products?category=photo-video&subcategory=photo-video-accessories"),
                ("ყველას ნახვა", "View All", "/products?category=photo-video&subcategory=action-cameras"),
            ]
        ),
        (
            "დრონები", "Drones",
            [
                ("DJI", "DJI", "/products?category=photo-video&subcategory=drones&brand=DJI"),
                ("Insta360", "Insta360", "/products?category=photo-video&subcategory=drones&brand=Insta360"),
                ("ყველას ნახვა", "View All", "/products?category=photo-video&subcategory=drones"),
            ]
        ),
        (
            "სმარტ სათვალეები", "Smart Glasses",
            [
                ("Ray-Ban Meta", "Ray-Ban Meta", "/products?category=photo-video&subcategory=smart-glasses&brand=Ray-Ban-Meta"),
                ("Oakley Meta", "Oakley Meta", "/products?category=photo-video&subcategory=smart-glasses&brand=Oakley-Meta"),
                ("ყველას ნახვა", "View All", "/products?category=photo-video&subcategory=smart-glasses"),
            ]
        ),
        (
            "ფოტო პრინტერები", "Photo Printers",
            [
                ("Canon", "Canon", "/products?category=photo-video&subcategory=photo-printers&brand=Canon"),
                ("Xiaomi", "Xiaomi", "/products?category=photo-video&subcategory=photo-printers&brand=Xiaomi"),
                ("Polaroid", "Polaroid", "/products?category=photo-video&subcategory=photo-printers&brand=Polaroid"),
                ("Fujifilm", "Fujifilm", "/products?category=photo-video&subcategory=photo-printers&brand=Fujifilm"),
                ("Kodak", "Kodak", "/products?category=photo-video&subcategory=photo-printers&brand=Kodak"),
                ("აქსესუარები", "Accessories", "/products?category=photo-video&subcategory=photo-video-accessories"),
                ("ყველას ნახვა", "View All", "/products?category=photo-video&subcategory=photo-printers"),
            ]
        ),
        (
            "Smartphone ფოტოგრაფია", "Smartphone Photography",
            [
                ("სტაბილიზატორები", "Gimbals", "/products?category=photo-video&subcategory=smartphone-photography&type=gimbals"),
                ("ლაპელური მიკროფონები", "Lavalier Microphones", "/products?category=audio-systems&subcategory=microphones&type=lavalier"),
                ("Tripod | სელფის ჯოხი", "Tripod | Selfie Stick", "/products?category=photo-video&subcategory=smartphone-photography&type=tripod"),
                ("ყველას ნახვა", "View All", "/products?category=photo-video&subcategory=smartphone-photography"),
            ]
        ),
        (
            "Power Banks", "Power Banks",
            [
                ("Anker", "Anker", "/products?category=accessories&subcategory=power-banks&brand=Anker"),
                ("Ugreen", "Ugreen", "/products?category=accessories&subcategory=power-banks&brand=Ugreen"),
                ("Xiaomi", "Xiaomi", "/products?category=accessories&subcategory=power-banks&brand=Xiaomi"),
                ("Lenovo", "Lenovo", "/products?category=accessories&subcategory=power-banks&brand=Lenovo"),
                ("EcoFlow", "EcoFlow", "/products?category=accessories&subcategory=power-banks&brand=EcoFlow"),
                ("Belkin", "Belkin", "/products?category=accessories&subcategory=power-banks&brand=Belkin"),
                ("Samsung", "Samsung", "/products?category=accessories&subcategory=power-banks&brand=Samsung"),
                ("ყველას ნახვა", "View All", "/products?category=accessories&subcategory=power-banks"),
            ]
        ),
        (
            "ფოტო | ვიდეო აქსესუარები", "Photo | Video Accessories",
            [
                ("ობიექტივები | ლინზა", "Lenses", "/products?category=photo-video&subcategory=photo-video-accessories&type=lenses"),
                ("Gimbal სტაბილიზატორები", "Gimbal Stabilizers", "/products?category=photo-video&subcategory=photo-video-accessories&type=gimbal"),
                ("Speedlite განათებები", "Speedlite Lights", "/products?category=photo-video&subcategory=photo-video-accessories&type=speedlite"),
                ("შტატივები", "Tripods", "/products?category=photo-video&subcategory=photo-video-accessories&type=tripods"),
                ("უსადენო მიკროფონები", "Wireless Microphones", "/products?category=audio-systems&subcategory=microphones&type=wireless-mics"),
                ("ფოტოაპარატის ჩანთები", "Camera Bags", "/products?category=photo-video&subcategory=photo-video-accessories&type=camera-bags"),
                ("მეხსიერების ბარათები", "Memory Cards", "/products?category=laptops&subcategory=storage&type=memory-cards"),
                ("ციფრული ჩარჩო", "Digital Frames", "/products?category=photo-video&subcategory=photo-video-accessories&type=digital-frames"),
                ("ყველას ნახვა", "View All", "/products?category=photo-video&subcategory=photo-video-accessories"),
            ]
        ),
    ],
    "beauty": [
        (
            "თმის მოვლა", "Hair Care",
            [
                ("თმის სტაილერი | უთო", "Hair Stylers", "/products?category=beauty&subcategory=hair-care&type=hair-stylers"),
                ("Dyson", "Dyson", "/products?category=beauty&subcategory=hair-care&brand=Dyson"),
                ("Philips", "Philips", "/products?category=beauty&subcategory=hair-care&brand=Philips"),
                ("Dreame", "Dreame", "/products?category=beauty&subcategory=hair-care&brand=Dreame"),
                ("ყველას ნახვა", "View All", "/products?category=beauty&subcategory=hair-care"),
            ]
        ),
        (
            "თმის ფენი", "Hair Dryers",
            [
                ("Dyson", "Dyson", "/products?category=beauty&subcategory=hair-dryers&brand=Dyson"),
                ("Xiaomi", "Xiaomi", "/products?category=beauty&subcategory=hair-dryers&brand=Xiaomi"),
                ("Philips", "Philips", "/products?category=beauty&subcategory=hair-dryers&brand=Philips"),
                ("Laifen", "Laifen", "/products?category=beauty&subcategory=hair-dryers&brand=Laifen"),
                ("Dreame", "Dreame", "/products?category=beauty&subcategory=hair-dryers&brand=Dreame"),
                ("ყველას ნახვა", "View All", "/products?category=beauty&subcategory=hair-dryers"),
            ]
        ),
        (
            "წვერის მოვლა", "Beard Care",
            [
                ("წვერსაპარსები", "Shavers", "/products?category=beauty&subcategory=beard-care&type=shavers"),
                ("Philips", "Philips", "/products?category=beauty&subcategory=beard-care&brand=Philips"),
                ("Xiaomi", "Xiaomi", "/products?category=beauty&subcategory=beard-care&brand=Xiaomi"),
                ("წვერსაპარსის თავაკები", "Replacement Heads", "/products?category=beauty&subcategory=beard-care&type=shaver-heads"),
                ("ტრიმერები", "Trimmers", "/products?category=beauty&subcategory=beard-care&type=trimmers"),
                ("ყველას ნახვა", "View All", "/products?category=beauty&subcategory=beard-care"),
            ]
        ),
        (
            "სპორტი", "Sports & Fitness",
            [
                ("სარბენი ბილიკები", "Treadmills", "/products?category=beauty&subcategory=sports-fitness&type=treadmills"),
                ("მასაჟორები", "Massagers", "/products?category=beauty&subcategory=sports-fitness&type=massagers"),
                ("სმარტ სასწორები", "Smart Scales", "/products?category=beauty&subcategory=sports-fitness&type=smart-scales"),
                ("ფიტნეს ტრეკერები", "Fitness Trackers", "/products?category=beauty&subcategory=sports-fitness&type=fitness-trackers"),
                ("სპორტული ყურსასმენები", "Sports Headphones", "/products?category=audio-systems&subcategory=headphones&type=sports"),
                ("სკუტერი", "Scooters", "/products?category=beauty&subcategory=sports-fitness&type=scooters"),
                ("სმარტ საათები", "Smart Watches", "/products?category=smart-watches"),
                ("ლახტი", "Jump Rope", "/products?category=beauty&subcategory=sports-fitness&type=jump-rope"),
                ("ფიტნეს ველოსიპედი", "Fitness Bike", "/products?category=beauty&subcategory=sports-fitness&type=fitness-bike"),
                ("ყველას ნახვა", "View All", "/products?category=beauty&subcategory=sports-fitness"),
            ]
        ),
        (
            "თავის მოვლა", "Personal Care",
            [
                ("კბილის ჯაგრისები", "Electric Toothbrushes", "/products?category=beauty&subcategory=personal-care&type=toothbrushes"),
                ("კბილის ჯაგრისის თავაკები", "Brush Heads", "/products?category=beauty&subcategory=personal-care&type=brush-heads"),
                ("საპნის დისპენსერი", "Soap Dispensers", "/products?category=beauty&subcategory=personal-care&type=soap-dispenser"),
                ("ირიგატორები", "Water Flossers", "/products?category=beauty&subcategory=personal-care&type=irrigators"),
                ("ყველას ნახვა", "View All", "/products?category=beauty&subcategory=personal-care"),
            ]
        ),
        (
            "კლიმატის მართვა", "Climate Control",
            [
                ("ჰაერის გამწმენდი", "Air Purifiers", "/products?category=beauty&subcategory=climate-control&type=air-purifiers"),
                ("ჰაერის დამატენიანებელი", "Humidifiers", "/products?category=beauty&subcategory=climate-control&type=humidifiers"),
                ("საჭირო აქსესუარები", "Accessories", "/products?category=beauty&subcategory=climate-control&type=climate-accessories"),
                ("ყველას ნახვა", "View All", "/products?category=beauty&subcategory=climate-control"),
            ]
        ),
        (
            "ტანსაცმლის მოვლა", "Clothing Care",
            [
                ("ქსოვილის ტრიმერი", "Fabric Trimmer", "/products?category=beauty&subcategory=clothing-care&type=fabric-trimmer"),
                ("ტანსაცმლის უთო", "Clothes Iron", "/products?category=beauty&subcategory=clothing-care&type=iron"),
                ("ყველას ნახვა", "View All", "/products?category=beauty&subcategory=clothing-care"),
            ]
        ),
    ],
    "accessories": [
        (
            "მობილურის ეკრანის დამცავები", "Phone Screen Protectors",
            [
                ("For Apple", "For Apple", "/products?category=accessories&subcategory=screen-protectors&brand=Apple"),
                ("For Samsung", "For Samsung", "/products?category=accessories&subcategory=screen-protectors&brand=Samsung"),
                ("For Xiaomi", "For Xiaomi", "/products?category=accessories&subcategory=screen-protectors&brand=Xiaomi"),
                ("For Google", "For Google", "/products?category=accessories&subcategory=screen-protectors&brand=Google"),
                ("For Oppo", "For Oppo", "/products?category=accessories&subcategory=screen-protectors&brand=Oppo"),
                ("For Realme", "For Realme", "/products?category=accessories&subcategory=screen-protectors&brand=Realme"),
                ("For Honor", "For Honor", "/products?category=accessories&subcategory=screen-protectors&brand=Honor"),
                ("For Nothing", "For Nothing", "/products?category=accessories&subcategory=screen-protectors&brand=Nothing"),
                ("For Oneplus", "For Oneplus", "/products?category=accessories&subcategory=screen-protectors&brand=OnePlus"),
                ("For Motorola", "For Motorola", "/products?category=accessories&subcategory=screen-protectors&brand=Motorola"),
                ("ყველას ნახვა", "View All", "/products?category=accessories&subcategory=screen-protectors"),
            ]
        ),
        (
            "მობილურის ჩასადებები", "Phone Cases",
            [
                ("For Apple", "For Apple", "/products?category=accessories&subcategory=phone-cases&brand=Apple"),
                ("For Samsung", "For Samsung", "/products?category=accessories&subcategory=phone-cases&brand=Samsung"),
                ("For Xiaomi", "For Xiaomi", "/products?category=accessories&subcategory=phone-cases&brand=Xiaomi"),
                ("For Google", "For Google", "/products?category=accessories&subcategory=phone-cases&brand=Google"),
                ("For Oppo", "For Oppo", "/products?category=accessories&subcategory=phone-cases&brand=Oppo"),
                ("For Realme", "For Realme", "/products?category=accessories&subcategory=phone-cases&brand=Realme"),
                ("For Honor", "For Honor", "/products?category=accessories&subcategory=phone-cases&brand=Honor"),
                ("For Nothing", "For Nothing", "/products?category=accessories&subcategory=phone-cases&brand=Nothing"),
                ("For Oneplus", "For Oneplus", "/products?category=accessories&subcategory=phone-cases&brand=OnePlus"),
                ("For Motorola", "For Motorola", "/products?category=accessories&subcategory=phone-cases&brand=Motorola"),
                ("ყველას ნახვა", "View All", "/products?category=accessories&subcategory=phone-cases"),
            ]
        ),
        (
            "უსადენო დამტენები", "Wireless Chargers",
            [
                ("Apple", "Apple", "/products?category=accessories&subcategory=wireless-chargers&brand=Apple"),
                ("Samsung", "Samsung", "/products?category=accessories&subcategory=wireless-chargers&brand=Samsung"),
                ("Xiaomi", "Xiaomi", "/products?category=accessories&subcategory=wireless-chargers&brand=Xiaomi"),
                ("Ugreen", "Ugreen", "/products?category=accessories&subcategory=wireless-chargers&brand=Ugreen"),
                ("Belkin", "Belkin", "/products?category=accessories&subcategory=wireless-chargers&brand=Belkin"),
                ("Havit", "Havit", "/products?category=accessories&subcategory=wireless-chargers&brand=Havit"),
                ("Hoco", "Hoco", "/products?category=accessories&subcategory=wireless-chargers&brand=Hoco"),
                ("Anker", "Anker", "/products?category=accessories&subcategory=wireless-chargers&brand=Anker"),
                ("ყველას ნახვა", "View All", "/products?category=accessories&subcategory=wireless-chargers"),
            ]
        ),
        (
            "Power Banks", "Power Banks",
            [
                ("Anker", "Anker", "/products?category=accessories&subcategory=power-banks&brand=Anker"),
                ("Ugreen", "Ugreen", "/products?category=accessories&subcategory=power-banks&brand=Ugreen"),
                ("Xiaomi", "Xiaomi", "/products?category=accessories&subcategory=power-banks&brand=Xiaomi"),
                ("Lenovo", "Lenovo", "/products?category=accessories&subcategory=power-banks&brand=Lenovo"),
                ("EcoFlow", "EcoFlow", "/products?category=accessories&subcategory=power-banks&brand=EcoFlow"),
                ("Belkin", "Belkin", "/products?category=accessories&subcategory=power-banks&brand=Belkin"),
                ("Samsung", "Samsung", "/products?category=accessories&subcategory=power-banks&brand=Samsung"),
                ("ყველას ნახვა", "View All", "/products?category=accessories&subcategory=power-banks"),
            ]
        ),
        (
            "კაბელები", "Cables",
            [
                ("Lightning", "Lightning", "/products?category=accessories&subcategory=cables&format=lightning"),
                ("Micro USB", "Micro USB", "/products?category=accessories&subcategory=cables&format=micro-usb"),
                ("Type-C", "Type-C", "/products?category=accessories&subcategory=cables&format=type-c"),
                ("ყველას ნახვა", "View All", "/products?category=accessories&subcategory=cables"),
            ]
        ),
        (
            "დამტენი ადაპტერი", "Charging Adapters",
            [
                ("Apple Adapter", "Apple Adapter", "/products?category=accessories&subcategory=charging-adapters&brand=Apple"),
                ("Samsung Adapter", "Samsung Adapter", "/products?category=accessories&subcategory=charging-adapters&brand=Samsung"),
                ("Anker Adapter", "Anker Adapter", "/products?category=accessories&subcategory=charging-adapters&brand=Anker"),
                ("Spigen Adapter", "Spigen Adapter", "/products?category=accessories&subcategory=charging-adapters&brand=Spigen"),
                ("Belkin Adapter", "Belkin Adapter", "/products?category=accessories&subcategory=charging-adapters&brand=Belkin"),
                ("Ugreen Adapter", "Ugreen Adapter", "/products?category=accessories&subcategory=charging-adapters&brand=Ugreen"),
                ("Xiaomi Adapter", "Xiaomi Adapter", "/products?category=accessories&subcategory=charging-adapters&brand=Xiaomi"),
                ("Baseus Adapter", "Baseus Adapter", "/products?category=accessories&subcategory=charging-adapters&brand=Baseus"),
                ("ყველას ნახვა", "View All", "/products?category=accessories&subcategory=charging-adapters"),
            ]
        ),
        (
            "ლეპტოპის აქსესუარები", "Laptop Accessories",
            [
                ("მაუსები", "Mouses", "/products?category=accessories&subcategory=laptop-accessories&type=laptop-mouse"),
                ("მაუს პედები", "Mouse Pads", "/products?category=accessories&subcategory=laptop-accessories&type=mouse-pad"),
                ("კლავიატურები", "Keyboards", "/products?category=accessories&subcategory=laptop-accessories&type=keyboard"),
                ("HUB გადამყვანები", "HUB Adapters", "/products?category=tablets&subcategory=hub-adapters"),
                ("გამაგრილებელი სტენდები", "Cooling Stands", "/products?category=accessories&subcategory=laptop-accessories&type=cooling-stand"),
                ("ლეპტოპის დამტენი", "Laptop Chargers", "/products?category=accessories&subcategory=laptop-accessories&type=laptop-charger"),
                ("მონიტორის საწმენდები", "Monitor Cleaners", "/products?category=accessories&subcategory=laptop-accessories&type=monitor-cleaner"),
                ("მეხსიერების ბარათები | SSD", "Memory Cards | SSD", "/products?category=laptops&subcategory=storage"),
                ("ყველას ნახვა", "View All", "/products?category=accessories&subcategory=laptop-accessories"),
            ]
        ),
        (
            "ტაბის აქსესუარები", "Tablet Accessories",
            [
                ("ქეისები", "Cases", "/products?category=accessories&subcategory=tablet-accessories&type=tablet-case"),
                ("ეკრანის დამცავი", "Screen Protectors", "/products?category=accessories&subcategory=tablet-accessories&type=tablet-screen"),
                ("კონექტორები", "Connectors", "/products?category=accessories&subcategory=tablet-accessories&type=tablet-connectors"),
                ("OTG ფლეშ მეხსიერება", "OTG Flash", "/products?category=accessories&subcategory=tablet-accessories&type=otg"),
                ("მეხსიერების ბარათი", "Memory Cards", "/products?category=laptops&subcategory=storage&type=memory-card"),
                ("სმარტ კლავიატურა | კალამი", "Smart Keyboard | Pen", "/products?category=accessories&subcategory=tablet-accessories&type=tablet-keyboard"),
                ("ყველას ნახვა", "View All", "/products?category=accessories&subcategory=tablet-accessories"),
            ]
        ),
    ],
}

BRANDS = [
    "Apple", "Samsung", "Sony", "LG", "DJI", "Dell", 
    "HP", "Bose", "Canon", "Xiaomi", "Google", "Realme", 
    "Lenovo", "Honor", "Blackview", "Garmin", "Amazfit", "JBL", 
    "Baseus", "Anker", "Dyson","Marshall", "Nothing", "Microsoft", 
    "Vivo", "Nokia", "Philips", "Braun", "Motorola", "Asus", 
    "Logitech", "Nintendo", "Boya", "Ugreen", "Meta", "Acer", 
    "ZTE", "Beats", "Valve",  "OnePlus", "AOC",  "Backbone",
    "MSI", "BenQ","Razer", "Havit", "2E", "HyperX", "Amazon", 
    "Brateck", "Wanbo", "XGIMI", "Epson", "Aurzen", "Toshiba", "TCL",
    "Nikon", "GoPro", "Insta360", "Ray-Ban-Meta", "Oakley-Meta", "Polaroid", "Fujifilm", "Kodak",
    "EcoFlow", "Belkin", "Sigma", "Zhiyun", "Godox", "Manfrotto", "Lowepro", "Aura", "Rode", "SanDisk"
]


def _ensure_category(slug, icon_class, name_ka, name_en, sort_order):
    cat = Category.query.filter_by(slug=slug).first()
    if not cat:
        cat = Category(
            slug=slug,
            icon_class=icon_class,
            name_ka=name_ka,
            name_en=name_en,
            sort_order=sort_order
        )
        db.session.add(cat)
        db.session.flush()
    else:
        cat.name_ka = name_ka
        cat.name_en = name_en
        cat.icon_class = icon_class
        cat.sort_order = sort_order
    return cat


def _ensure_subcategory(category_id, slug, name_ka, name_en, sort_order):
    sub = Subcategory.query.filter_by(category_id=category_id, slug=slug).first()
    if not sub:
        sub = Subcategory(category_id=category_id, slug=slug,
                          name_ka=name_ka, name_en=name_en, sort_order=sort_order)
        db.session.add(sub)
        db.session.flush()
    else:
        sub.name_ka = name_ka
        sub.name_en = name_en
        sub.sort_order = sort_order
    return sub


def _ensure_mega_group(category_id, title_ka, title_en, sort_order):
    mg = MegaGroup.query.filter_by(category_id=category_id, title_en=title_en).first()
    if not mg:
        mg = MegaGroup(category_id=category_id, title_ka=title_ka,
                       title_en=title_en, sort_order=sort_order)
        db.session.add(mg)
        db.session.flush()
    else:
        mg.title_ka = title_ka
        mg.title_en = title_en
        mg.sort_order = sort_order
    return mg


def _ensure_mega_item(group_id, name_ka, name_en, url, sort_order=0):
    mi = MegaItem.query.filter_by(group_id=group_id, title_en=name_en).first() 
    if not mi:
        mi = MegaItem(
            group_id=group_id,
            title_ka=name_ka,
            title_en=name_en,
            url=url,
            sort_order=sort_order
        )
        db.session.add(mi)
        db.session.flush()
    else:
        mi.title_ka = name_ka
        mi.url = url
        mi.sort_order = sort_order
    return mi


def run():
    Product.query.delete()
    MegaItem.query.delete()
    Subcategory.query.delete()
    MegaGroup.query.delete()
    Brand.query.delete()
    Category.query.delete()
    db.session.commit()

    cat_map = {}
    for i, (slug, icon_class, ka, en) in enumerate(CATEGORIES):
        cat = _ensure_category(slug, icon_class, ka, en, sort_order=i)
        cat_map[slug] = cat
    db.session.commit()

    for cat_slug, subs in SUBCATEGORIES.items():
        cat = cat_map[cat_slug]
        for j, (sub_slug, ka, en) in enumerate(subs):
            _ensure_subcategory(cat.id, sub_slug, ka, en, sort_order=j)
    db.session.commit()

    for cat_slug, groups in MEGA_MENU_DATA.items():
        cat = cat_map.get(cat_slug)
        if not cat: continue
        for g_idx, (title_ka, title_en, items) in enumerate(groups):
            mg = _ensure_mega_group(cat.id, title_ka, title_en, sort_order=g_idx)
            for i_idx, (item_ka, item_en, url) in enumerate(items):
                _ensure_mega_item(mg.id, item_ka, item_en, url, sort_order=i_idx)
    db.session.commit()

    def get_or_create_brand(brand_name):
        b = Brand.query.filter_by(name=brand_name).first()
        if not b:
            b = Brand(name=brand_name, slug=brand_name.lower().replace(" ", "-"))
            db.session.add(b)
            db.session.flush()
        return b

    brand_map = {}
    for name in BRANDS:
        brand_map[name] = get_or_create_brand(name)
    db.session.commit()

    if Product.query.count() == 0:
        for index, item in enumerate(PRODUCTS):
            category_slug    = item[0]
            subcategory_slug = item[1]
            brand_name       = item[2]
            name_ka          = item[3]
            name_en          = item[4]
            price            = item[5]
            old_price        = item[6]
            stock_qty        = item[7]
            sku              = item[8]
            badge            = item[9]
            image            = item[10]
            reviews_count    = item[11]
            desc_ka          = item[12]
            desc_en          = item[13]
            raw_specs        = item[14]

            cat = Category.query.filter_by(slug=category_slug).first()
            brand = Brand.query.filter_by(name=brand_name).first()
            
            subcat = None
            if cat:
                subcat = Subcategory.query.filter_by(category_id=cat.id, slug=subcategory_slug).first()
            
            generated_slug = re.sub(r'[^a-z0-9\s-]', '', name_en.lower())
            generated_slug = re.sub(r'[\s-]+', '-', generated_slug).strip('-')
            
            if not generated_slug:
                generated_slug = f"product-{index}"

            normalized_specs = {}
            if isinstance(raw_specs, dict):
                for key, val in raw_specs.items():
                    normalized_specs[key.lower()] = val

            if cat and brand:
                p = Product(
                    name_ka=name_ka,
                    name_en=name_en,
                    slug=generated_slug,
                    price=price,
                    old_price=old_price,
                    image=image,
                    badge=badge,
                    stock_qty=stock_qty,
                    sku=sku,
                    category_id=cat.id,
                    subcategory_id=subcat.id if subcat else None,
                    brand_id=brand.id,
                    specs=normalized_specs  
                )
                db.session.add(p)
                
        db.session.commit()

    admin = User.query.filter_by(email=SUPER_ADMIN_EMAIL).first()
    if not admin:
        admin = User(
            first_name="Maria",
            last_name="Kashavanidze",
            email=SUPER_ADMIN_EMAIL,
        )
        db.session.add(admin)

    admin.role = "super_admin"
    admin.is_active = True
    admin.set_password(SUPER_ADMIN_DEFAULT_PASSWORD)
    print("done")
    db.session.commit()


if __name__ == "__main__":
    from run import app 
    
    with app.app_context():
        run()