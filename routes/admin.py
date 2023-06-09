from django.contrib import admin
from routes.models import Routes, Comment, RouteRate, Destinations, Places

admin.site.register(Routes)
admin.site.register(Comment)
admin.site.register(RouteRate)
admin.site.register(Destinations)
admin.site.register(Places)
