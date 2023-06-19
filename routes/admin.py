from django.contrib import admin
from routes.models import Route, Comment, RouteRate, RouteArea

admin.site.register(Route)
admin.site.register(RouteArea)
admin.site.register(Comment)
admin.site.register(RouteRate)
