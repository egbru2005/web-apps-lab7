# admin login: egbru
# admin password: labspass

import io

from django.contrib import admin
from django.http import FileResponse
from reportlab.lib.pagesizes import A4
# генерация pdf отчетов
from reportlab.pdfgen import canvas

from .models import *

# inline для админки
class MatchParticipationInline(admin.TabularInline):
    model = MatchParticipation
    extra = 1  # Количество пустых строк для добавления
    raw_id_fields = ('athlete',)


# Register your models here.

def export_match_pdf(modeladmin, request, queryset):
    response = io.BytesIO()

    p = canvas.Canvas(response, pagesize=A4)

    y = 800
    p.drawString(100, y, "Match Report")
    y -= 40

    for match in queryset:
        text = f"{match.date_time.strftime('%Y-%m-%d')}: {match.home_team} vs {match.away_team} ({match.score_home}:{match.score_away})"
        p.drawString(50, y, text)
        y -= 20

        if y < 50:  # Если страница кончилась
            p.showPage()
            y = 800

    p.showPage()
    p.save()
    response.seek(0)
    return FileResponse(response, as_attachment=True, filename="report.pdf")


export_match_pdf.short_description = "Download pdf report"

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('home_team', 'away_team', 'score_home', 'score_away', 'status')
    list_filter = ('status', 'tournament')
    # Чтобы не грузить список всех команд мира в список:
    raw_id_fields = ('home_team', 'away_team', 'tournament')
    inlines = [MatchParticipationInline]
    actions = [export_match_pdf]

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