from django.contrib import admin
from routes.models import Route, Comment, RouteRate, Area, Sigungu, Spot, RouteArea

admin.site.register(Route)
admin.site.register(RouteArea)
admin.site.register(Comment)
admin.site.register(RouteRate)
admin.site.register(Area)
admin.site.register(Sigungu)
admin.site.register(Spot)
