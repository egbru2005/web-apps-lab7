from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum, Q
from django.utils import timezone

from .forms import ArticleForm
from .models import Article, Match, Team
from django.contrib.auth import logout
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
#from .forms import UserRegisterForm  # Форму создадим позже


def home(request):
    # Задание filter() и __
    # Ищем матчи, дата которых больше или равна (gte) текущему времени
    upcoming_matches = Match.objects.filter(date_time__gte=timezone.now())

    # Задание exclude()
    # Исключаем отмененные матчи (предположим, такой статус есть)
    upcoming_matches = upcoming_matches.exclude(status='canceled')

    # Задание order_by()
    # Принудительная сортировка от старых к новым
    upcoming_matches = upcoming_matches.order_by('date_time')

    # Задание функция агрегирования
    # Посчитаем общее количество голов, забитых хозяевами во всех матчах
    total_goals = Match.objects.aggregate(Sum('score_home'))

    return render(request, 'sports/home.html', {
        'matches': upcoming_matches,
        'total_goals': total_goals,
    })


def article_list(request):
    # Используем наш кастомный менеджер (.published)
    object_list = Article.published.all()

    # Задание Пагинация (+ try, except)
    paginator = Paginator(object_list, 5)  # 5 статей на странице
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # Если page не целое число, показываем первую страницу
        posts = paginator.page(1)
    except EmptyPage:
        # Если page больше максимального, показываем последнюю
        posts = paginator.page(paginator.num_pages)

    return render(request, 'sports/article_list.html', {'posts': posts})


def article_detail(request, slug):
    # Задание get_object_or_404
    article = get_object_or_404(Article, slug=slug)
    return render(request, 'sports/article_detail.html', {'article': article})


def team_detail(request, pk):
    team = get_object_or_404(Team, pk=pk)

    # Задание использование __ (обращение к связанной таблице)
    # Получаем имена соперников этой команды через связи матчей
    ###
    return render(request, 'sports/team_detail.html', {'team': team})


# Задание Регистрация пользователя


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Сразу логиним после регистрации
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def logout_user(request):
    logout(request) # Удаляет данные сессии (разлогинивает)
    return redirect('home') # Перенаправляет на главную страницу

# values и values_list
def stats_view(request):
    # values() возвращает список словарей
    # [{'name':'CSKA','city':'Moscow'}]
    teams_data = Team.objects.values('name', 'city')

    # values_list() возвращает плоский список
    # ['Live', 'Finished']
    statuses = Match.objects.values_list('status', flat=True).distinct()

    return render(request, 'sports/stats.html', {
        'teams_data': teams_data,
        'statuses': statuses
    })

# создание/изменение/удаление (CRUD)
@login_required
def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            form.save_m2m()
            return redirect('article_list')
    else:
        form = ArticleForm()

    return render(request, 'sports/article_form.html', {'form': form, 'action': 'Create'})


@login_required
def article_update(request, pk):
    article = get_object_or_404(Article, pk=pk)

    # Простая проверка прав
    if article.author != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("You don't have permission to edit this article.")

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            return redirect('article_detail', slug=article.slug)
    else:
        form = ArticleForm(instance=article)

    return render(request, 'sports/article_form.html', {'form': form, 'action': 'Edit'})


@login_required
def article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk)

    if article.author != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("You don't have permission to delete this article.")

    if request.method == 'POST':
        article.delete()
        return redirect('article_list')

    return render(request, 'sports/article_confirm_delete.html', {'article': article})