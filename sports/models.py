from django.db import models
from django.utils import timezone
from django.urls import reverse

# Create your models here.

'''
Разобьем модели на 4 вида:
- Справочники (вид спорта, название турнира)
- Участники (команда, спортсмен)
- События (игра)
- Контент (вспомогательная модель, отражающая свойства статьи или обзора)
'''

from django.contrib.auth.models import User
from django.utils.text import slugify


#справочники

class Sport(models.Model):
    name = models.CharField("Sport name", max_length=200)
    slug = models.SlugField(unique=True, help_text="URL")
    icon = models.ImageField("Icon", upload_to="sports/icons", blank=True, null=True)
    #Фотографии и логотипы могут быть пустыми ввиду их отсутствия у редактора.
    #Лучше иметь статью или сводку без изображений, чем вообще ничего

    def __str__(self):
        return self.name


class Tournament(models.Model):
    name = models.CharField("Tournament name", max_length=200)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name="tournaments")
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField("Current season", default=True)
    #description can be empty
    description = models.TextField("Description", blank=True)

    def __str__(self):
        return f"{self.name} - {self.sport.name}"


#участники

class Team(models.Model):
    name = models.CharField("Team name", max_length=200)
    short_name = models.CharField("Team short name", max_length=200, blank=True)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name="teams")
    logo = models.ImageField("Logo", upload_to="teams/logos", blank=True, null=True)
    city = models.CharField("City", max_length=200, blank=True)

    slug = models.SlugField(unique=True, help_text="URL")

    def __str__(self):
        return self.name


class Athlete(models.Model):
    first_name = models.CharField("Athlete first name", max_length=200)
    last_name = models.CharField("Athlete last name", max_length=200)

    #Игрок может быть свободным агентом без клуба, либо завершить карьеру и остаться в базе для просмотра его достижений, если бы был такой функционал
    current_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="players", null=True, blank=True)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)

    birth_date = models.DateField("Birth date", blank=True, null=True)
    photo = models.ImageField("Photo", upload_to="athletes/", blank=True, null=True)

    position = models.CharField("Position", max_length=200, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


#события

class Match(models.Model):
    #choices в поле модели
    STATUS_CHOICES = (
        ("scheduled", "Scheduled"),
        ("live", "Live"),
        ("finished", "Finished"),
        ("canceled", "Canceled"),
    )

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="matches")

    # Задание related_name
    # Позволяет обращаться от команды к матчам: team.home_matches.all()
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="home_matches")
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="away_matches")

    date_time = models.DateTimeField("Game start time")
    status = models.CharField("Status", max_length=200, choices=STATUS_CHOICES, default="scheduled")

    score_home = models.PositiveIntegerField("Home score", blank=True, null=True)
    score_away = models.PositiveIntegerField("Away score", blank=True, null=True)
    #При создании события (до начала игры) счет неизвестен, в таком случае он пустой

    broadcast_url = models.URLField("Broadcast URL", blank=True)

    class Meta:
        ordering = ["-date_time"]  #class metadata: order by game start time

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name}"


#контент

class PublishedManager(models.Manager):
    def get_queryset(self):
        # Переопределяем исходный запрос, возвращая только опубликованные статьи
        return super().get_queryset().filter(is_published=True)

class Tag(models.Model):
    name = models.CharField("Tag name", max_length=200)
    slug = models.SlugField(unique=True, help_text="URL")

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField("Title", max_length=200)
    slug = models.SlugField(unique=True, help_text="URL")
    content = models.TextField("Article content", blank=True)

    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    created_at = models.DateTimeField("Article creation time", default=timezone.now) #использование timezone
    updated_at = models.DateTimeField("Article update time", auto_now=True)
    is_published = models.BooleanField("Article published", default=True)

    preview_image = models.ImageField("Preview image", upload_to="articles/", blank=True, null=True)

    #Может быть связана с определенной игрой
    match = models.ForeignKey(Match, on_delete=models.SET_NULL, related_name="articles", blank=True, null=True)

    #Может быть связана с определенной командой или игроком
    related_teams = models.ManyToManyField(Team, related_name="news", blank=True)
    related_athletes = models.ManyToManyField(Athlete, related_name="news", blank=True)
    #Вышеуказанные поля могут быть пустыми, т.к. новость может относиться к спорту в общем

    #article tags
    tags = models.ManyToManyField(Tag, related_name="tags", blank=True)

    #использование менеджеров
    objects = models.Manager()  # Стандартный менеджер
    published = PublishedManager()  # Свой менеджер

    def __str__(self): #метод __str__
        return f"{self.title}"

    def get_absolute_url(self):
        # Генерирует ссылку вида /news/my-article-slug/ (использование get_absolute_url)
        return reverse('article_detail', kwargs={'slug': self.slug})

    class Meta:
        #class Meta: ordering
        ordering = ['-created_at']  # Сортировка: сначала новые