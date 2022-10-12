from django.contrib import admin
from .models import Playlist, TopsGroup

class TopsNightAdmin(admin.ModelAdmin):
	readonly_fields = ('created')

admin.site.register(Playlist)
admin.site.register(TopsGroup)

