# admin login: egbru
# admin password: labspass

from django.contrib import admin

# Register your models here.

from .models import *

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('home_team', 'away_team', 'score_home', 'score_away', 'status')
    list_filter = ('status', 'tournament')
    # Чтобы не грузить список всех команд мира в список:
    raw_id_fields = ('home_team', 'away_team', 'tournament')

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'sport', 'city')
    search_fields = ('name',)

@admin.register(Athlete)
class AthleteAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'current_team')
    search_fields = ('last_name', 'first_name')
    # У игрока есть связь с командой. Команд много, поэтому используем raw_id_fields
    raw_id_fields = ('current_team',)

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_published')
    search_fields = ('title',)

    # У статьи связи ManyToMany с командами и игроками.
    # В таком случае при большом количестве игроков будет очень большой удар по производительности.
    raw_id_fields = ('match', 'related_teams', 'related_athletes', 'author')

admin.site.register(Tournament)
admin.site.register(Sport)
admin.site.register(Tag)