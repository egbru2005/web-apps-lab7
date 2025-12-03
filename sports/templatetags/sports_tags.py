from django import template
from ..models import Article

register = template.Library()

# Задание Простой шаблонный тег
@register.simple_tag
def count_stats(home_score, away_score):
    #Суммирует два числа (например, счет матча)
    if (home_score == None or away_score == None):
        return 0
    return home_score + away_score

# Задание Тег с контекстными переменными
@register.simple_tag(takes_context=True)
def user_status_color(context):
    #Возвращает цвет в зависимости от того, админ юзер или нет
    request = context['request'] # Достаем request из контекста
    if request.user.is_authenticated and request.user.is_superuser:
        return "red" # Админ - красный
    return "blue" # Обычный - синий

# Задание Тег, возвращающий набор запросов (Inclusion tag)
@register.inclusion_tag('sports/tags/latest_news.html')
def show_latest_news(count=3):
    #Возвращает QuerySet последних новостей для отрисовки в боковой панели
    latest = Article.published.all().order_by('-created_at')[:count]
    return {'latest_news': latest}