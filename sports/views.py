from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum, Q
from django.utils import timezone
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