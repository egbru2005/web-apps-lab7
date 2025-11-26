from django.contrib import admin

# Register your models here.

from .models import *

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('home_team', 'away_team', 'score_home', 'score_away', 'status')
    list_filter = ('status', 'tournament')
    #admin password: labspass

admin.site.register(Sport)
admin.site.register(Team)
admin.site.register(Tournament)
admin.site.register(Athlete)
admin.site.register(Article)
admin.site.register(Tag)