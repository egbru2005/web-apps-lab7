import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from faker import Faker
from sports.models import Sport, Tournament, Team, Athlete, Match, MatchParticipation, Article, Tag


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными'

    def handle(self, *args, **kwargs):
        # Инициализируем Faker с русской локалью
        fake = Faker(['ru_RU'])

        self.stdout.write("Начинаем заполнение БД...")

        # 1. Создаем Суперюзера (если нет) и Авторов
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin')

        users = []
        for _ in range(5):
            username = fake.user_name()
            if not User.objects.filter(username=username).exists():
                users.append(User.objects.create_user(username, 'test@test.com', 'password'))

        # Если юзеры уже были, берем их
        if not users:
            users = list(User.objects.all())

        # 2. Виды спорта (фиксированный список)
        sports_data = [
            ('Футбол', 'soccer'),
            ('Хоккей', 'hockey'),
            ('Баскетбол', 'basketball'),
            ('Теннис', 'tennis'),
        ]

        sports_objs = []
        for name, slug in sports_data:
            # get_or_create предотвращает дубликаты при повторном запуске
            obj, created = Sport.objects.get_or_create(name=name, defaults={'slug': slug})
            sports_objs.append(obj)

        self.stdout.write(f"Создано видов спорта: {len(sports_objs)}")

        # 3. Турниры (по 2-3 на каждый вид спорта)
        tournaments = []
        for sport in sports_objs:
            for _ in range(3):
                t_name = f"Чемпионат {fake.city()} по {sport.name}у"
                t, _ = Tournament.objects.get_or_create(
                    name=t_name,
                    sport=sport,
                    defaults={
                        'slug': fake.slug() + str(random.randint(1, 9999)),
                        'is_active': random.choice([True, False])
                    }
                )
                tournaments.append(t)

        self.stdout.write(f"Создано турниров: {len(tournaments)}")

        # 4. Команды (по 10 на каждый вид спорта)
        teams = []
        for sport in sports_objs:
            for _ in range(10):
                team = Team.objects.create(
                    name=f"ФК {fake.city()}" if sport.name == 'Футбол' else f"Клуб {fake.word().capitalize()}",
                    short_name=fake.word()[:5].upper(),
                    sport=sport,
                    city=fake.city(),
                    slug=fake.unique.slug()
                )
                teams.append(team)

        self.stdout.write(f"Создано команд: {len(teams)}")

        # 5. Игроки (Спортсмены) - по 15 на команду
        athletes = []
        for team in teams:
            for _ in range(15):
                athlete = Athlete.objects.create(
                    first_name=fake.first_name_male(),
                    last_name=fake.last_name_male(),
                    current_team=team,
                    sport=team.sport,
                    birth_date=fake.date_of_birth(minimum_age=18, maximum_age=40),
                    position=fake.job()  # Или random.choice(['Нападающий', 'Вратарь'])
                )
                athletes.append(athlete)

        self.stdout.write(f"Создано спортсменов: {len(athletes)}")

        # 6. Матчи (Генерируем 30 матчей)
        matches = []
        for _ in range(30):
            # Выбираем случайный турнир
            tournament = random.choice(tournaments)
            # Берем команды только этого вида спорта
            possible_teams = list(Team.objects.filter(sport=tournament.sport))

            if len(possible_teams) < 2:
                continue

            home, away = random.sample(possible_teams, 2)

            match = Match.objects.create(
                tournament=tournament,
                home_team=home,
                away_team=away,
                date_time=fake.date_time_between(start_date='-1y', end_date='+1y',
                                                 tzinfo=timezone.get_current_timezone()),
                status=random.choice(['scheduled', 'live', 'finished']),
                score_home=random.randint(0, 5),
                score_away=random.randint(0, 5)
            )
            matches.append(match)

        self.stdout.write(f"Создано матчей: {len(matches)}")

        # 7. Статистика (MatchParticipation - through table)
        # Для каждого матча добавим несколько игроков со статистикой
        for match in matches:
            # Игроки домашней команды
            home_players = list(match.home_team.players.all())  # related_name='players' из модели
            # Игроки гостей
            away_players = list(match.away_team.players.all())

            # Берем по 3 случайных игрока из каждой команды
            participants = []
            if home_players:
                participants.extend(random.sample(home_players, min(len(home_players), 3)))
            if away_players:
                participants.extend(random.sample(away_players, min(len(away_players), 3)))

            for p in participants:
                MatchParticipation.objects.create(
                    match=match,
                    athlete=p,
                    goals_scored=random.choice([0, 0, 0, 1, 2]),  # Чаще 0 голов
                    minutes_played=random.randint(10, 90),
                    yellow_card=random.choice([True, False, False, False])
                )

        self.stdout.write("Статистика игроков сгенерирована")

        # 8. Теги
        tags = []
        for _ in range(10):
            tag_name = fake.word()
            tag, _ = Tag.objects.get_or_create(name=tag_name, slug=tag_name)
            tags.append(tag)

        # 9. Новости (Статьи)
        for _ in range(20):
            title = fake.sentence(nb_words=6)
            # Создаем статью
            article = Article.objects.create(
                title=title,
                # Слаг генерируется сам в save(), его не пишем
                content=fake.text(max_nb_chars=2000),
                author=random.choice(users),
                is_published=True,
                # match=random.choice(matches) # Можно привязать к случайному матчу
            )

            # Добавляем M2M связи
            article.tags.set(random.sample(tags, random.randint(1, 3)))

            # Привязываем случайные команды
            random_teams = random.sample(teams, random.randint(0, 2))
            article.related_teams.set(random_teams)

        self.stdout.write(self.style.SUCCESS('УСПЕШНО: База данных заполнена!'))