from app.models import Category, MegaGroup

def get_mega_menu():
    categories = Category.query.order_by(Category.sort_order).all()
    result = []
    
    for cat in categories:
        cat_data = {
            "slug": str(cat.slug),
            "icon": str(getattr(cat, 'icon_class', 'bi-folder')),
            "name_ka": str(getattr(cat, 'name_ka', '')),
            "name_en": str(getattr(cat, 'name_en', '')),
            "groups": []
        }
        
        for group in cat.mega_groups.order_by(MegaGroup.sort_order).all():
            group_data = {
                "title_ka": str(getattr(group, 'title_ka', '')),
                "title_en": str(getattr(group, 'title_en', '')),
                "items": []
            }
            
            group_items = group.items.all()
            
            
            for item in group_items:
                group_data["items"].append({
                    "name_ka": str(getattr(item, 'title_ka', '')),
                    "name_en": str(getattr(item, 'title_en', '')),
                    "url": str(getattr(item, 'url', '#'))
                })
            
            cat_data["groups"].append(group_data)
        
        result.append(cat_data)
    
    return result