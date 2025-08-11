from django.urls import path
from .views import egg_view, hatch_egg_view, buy_egg, add_tickets_view, wake_creature, companions, toggle_selected, feed

urlpatterns = [
    path("", companions, name="companions"),
    path("eggs/", egg_view, name="eggs_page"),
    path("buy/<int:egg_id>/", buy_egg, name="buy_egg"),
    path("add_ticket/<int:user_egg_id>/", add_tickets_view, name="add_ticket"),
    path("hatch/<int:user_egg_id>/", hatch_egg_view, name="hatch_egg"),
    path("wake/<int:creature_id>/", wake_creature, name="wake-creature"),
    path('toggle/', toggle_selected, name='toggle_selected'),
    path("feed/", feed, name="feed"),

]
