from django.contrib import admin
from watchlist_app.models import Watchlist, StreamingPlatform

# Register your models here.
admin.site.register(Watchlist)
admin.site.register(StreamingPlatform)