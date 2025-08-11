from django import template

register = template.Library()

@register.filter
def filter_attr(queryset, attr):
    return [x for x in queryset if getattr(x, attr)]

@register.filter
def sort_by_rarity(queryset):
    """Sort creatures by rarity in specific order"""
    RARITY_ORDER = {
        'Legendary': 0,
        'Epic': 1,
        'Elite': 2, 
        'Rare': 3,
        'Common': 4
    }
    return sorted(queryset, key=lambda x: RARITY_ORDER.get(x.creature.rarity, 5))