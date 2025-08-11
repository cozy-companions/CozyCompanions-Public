from django.contrib import admin
from .models import Creature, UserCreature, Egg, UserEgg
# Register your models here.
class CreatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'rarity')
    list_filter = ['rarity']
    search_fields = ['name']

class UserCreatureAdmin(admin.ModelAdmin):
    list_filter = ['user', 'creature']
    search_fields = ['user', 'creature']

admin.site.register(Creature, CreatureAdmin)
admin.site.register(Egg)
admin.site.register(UserCreature)
admin.site.register(UserEgg)
