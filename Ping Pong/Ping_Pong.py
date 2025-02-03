import sqlite3
import pygame
import sys
import random
import math
import time
from pygame.locals import*

import blockblast

# Инициализация Pygame
pygame.init()

clock = pygame.time.Clock()

# Настройки экрана
WIDTH, HEIGHT = 960, 600
screen = pygame.display.set_mode((int(WIDTH), int(HEIGHT)))
pygame.display.set_caption("Main Menu")

chil = pygame.image.load('i.png')
chil1 = pygame.image.load('i1.png')
img = pygame.image.load('cat.png')

frames = [] # to store the different images of the GIF
for i in range(121):
    if i < 10:
        frames.append(pygame.image.load(f'ezgif-split/frame_00{i}_delay-0.04s.gif').convert_alpha())
    elif i >= 10 and i < 100:
        frames.append(pygame.image.load(f"ezgif-split/frame_0{i}_delay-0.04s.gif").convert_alpha())
    else:
        frames.append(pygame.image.load(f"ezgif-split/frame_{i}_delay-0.04s.gif").convert_alpha())

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (100, 100, 100)
LIGHT_GREY = (200, 200, 200)
HOVER_GREY = (150, 150, 150)
BUTTON_BORDER = (50, 50, 50)
BUTTON_BACKGROUND = LIGHT_GREY
TABLE_BLUE = (0, 0, 128)  # Синий цвет для стола
PADDLE_RED = (255, 0, 0)  # Красный цвет для ракеток
LINE_GRAY = (200, 200, 200)  # Серый цвет для центральной линии

# Настройки мяча
ball_size = 25
ball_x = WIDTH // 2
ball_y = HEIGHT // 2
ball_speed = 7  # Скорость мяча
acceleration = 10  # Величина ускорения при каждом ударе

# Функция для установки начальной скорости мяча
def set_ball_velocity():
    angle = math.radians(random.randrange(-60, 60))
    ball_speed_x = ball_speed * math.cos(angle)
    ball_speed_y = ball_speed * math.sin(angle)
    return ball_speed_x, ball_speed_y

ball_speed_x, ball_speed_y = set_ball_velocity()

# Настройки ракеток
paddle_width = 10
paddle_height = 120  # Увеличена высота ракетки
player1_x = 30
player1_y = HEIGHT // 2 - paddle_height // 2
player2_x = WIDTH - 40
player2_y = HEIGHT // 2 - paddle_height // 2
paddle_speed = 11
score1 = 0
score2 = 0

# Шрифты
font = pygame.font.Font(None, 40)
game_over_font = pygame.font.Font(None, 100)
pause_font = pygame.font.Font(None, 70)
button_font = pygame.font.Font(None, 40)  # Уменьшенный шрифт для кнопок
selected_font = pygame.font.Font(None, 45)
clock = pygame.time.Clock()

game_over = False
# Функция для инициализации базы данных
def init_db():
    try:
        conn = sqlite3.connect('ping_pong_scores.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS match_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player1_score INTEGER,
                player2_score INTEGER,
                winner TEXT
            )
        ''')
        conn.commit()
        return conn
    except sqlite3.Error as e:
        print(f"Ошибка при подключении к базе данных: {e}")
        return None

# Функция для сохранения результата матча в базу данных
def save_score(conn, score1, score2):
    try:
        cursor = conn.cursor()
        winner = 'Игрок 1' if score1 > score2 else 'Игрок 2'
        cursor.execute('''
            INSERT INTO match_history (player1_score, player2_score, winner)
            VALUES (?, ?, ?)
        ''', (score1, score2, winner))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при сохранении результата матча: {e}")

# Функция для отображения истории матчей
def show_match_history():
    selected = 0
    try:
        conn = sqlite3.connect('ping_pong_scores.db')
        cursor = conn.cursor()
        cursor.execute('SELECT player1_score, player2_score, winner FROM match_history')
        matches = cursor.fetchall()

        screen.fill(BLACK)
        title = font.render("История матчей", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 28))
        matchi = [(i, match) for i, match in enumerate(matches)]
        k = 0
        if len(matchi) <= 10:
            for i, match in matchi:
                match_text = f"Матч {i + 1}:         {match[0]} : {match[1]} (Победил: {match[2]})"
                text_surface = font.render(match_text, True, WHITE)
                screen.blit(text_surface, (50, 80 + i * 45))
        else:
            for i, match in matchi[-10:]:
                match_text = f"Матч {k + 1}:{' ' * (9 - 2 * ((k + 1) // 10))}{match[0]} : {match[1]} (Победил: {match[2]})"
                text_surface = font.render(match_text, True, WHITE)
                screen.blit(text_surface, (50, 80 + k * 45))
                k += 1

        # Ожидание выхода
        waiting = True
        while waiting:
            main_menu_button_rect = pygame.Rect(WIDTH - 350, HEIGHT - 50, 310, 30)
            #selected_main_menu_text = button_font.render("Выйти в главное меню", True, GREY)
            main_menu_text = button_font.render("Выйти в главное меню", True, WHITE if selected != 1 else GREY)
            pygame.draw.rect(screen, BLACK, main_menu_button_rect)
            screen.blit(main_menu_text, (WIDTH - 350, HEIGHT - 50))

            # Проверка наведения курсора на кнопку выхода
            mouse_pos = pygame.mouse.get_pos()
            if main_menu_button_rect.collidepoint(mouse_pos):
                screen.blit(main_menu_text, (WIDTH - 350, HEIGHT - 50))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEMOTION:
                    mouse_pos = event.pos
                    if main_menu_button_rect.collidepoint(mouse_pos):
                        selected = 1
                    else:
                        selected = 0
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and main_menu_button_rect.collidepoint(event.pos):
                        waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        waiting = False

    except sqlite3.Error as e:
        print(f"Ошибка при извлечении истории матчей: {e}")

def main_menu():
    menu = True
    selected = None  # Выбранный пункт меню
    current_frame = 0
    while menu:
        screen.fill(BLACK)
        for i in range(20):
            screen.fill(BLACK)
            screen.blit(frames[current_frame], (0, 0))
        current_frame += 1
        current_frame %= len(frames) 
        title = font.render("Выберите игру", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        option1_text = "1. Block Blast"
        option1 = button_font.render(option1_text, True, WHITE if selected != 1 else GREY)
        option1_rect = option1.get_rect(topleft=(WIDTH // 2 - option1.get_width() // 2, 250))
        screen.blit(option1, option1_rect)

        option2_text = "2. Ping Pong"
        option2 = button_font.render(option2_text, True, WHITE if selected != 2 else GREY)
        option2_rect = option2.get_rect(topleft=(WIDTH // 2 - option2.get_width() // 2, 350))
        screen.blit(option2, option2_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                if option1_rect.collidepoint(mouse_pos):
                    selected = 1
                elif option2_rect.collidepoint(mouse_pos):
                    selected = 2
                else:
                    selected = None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левый клик
                    if option1_rect.collidepoint(event.pos):
                        menu = False
                        return "block_blast"
                    if option2_rect.collidepoint(event.pos):
                        menu = False
                        return "ping_pong"
        clock.tick(60)

def ping_pong():
    mode = show_menu()
    if mode == "main_menu":
        return "main_menu"
    elif mode == 'history':
        show_match_history()
    else:
        game_loop(mode)
        
def block_blast():
    blockblast.main()

# Функция для отображения меню игры в пинг-понг
def show_menu():
    global game_over, score1, score2, player1_y, player2_y, ball_x, ball_y
    ball_x = WIDTH // 2
    ball_y = HEIGHT // 2
    player1_y = HEIGHT // 2 - paddle_height // 2
    player2_y = HEIGHT // 2 - paddle_height // 2
    score1 = 0
    score2 = 0
    game_over = False
    menu = True
    selected_option = None  # Выбранный пункт меню
    current_frame = 0
    while menu:
        screen.fill(BLACK)
        title_text = font.render("Выберите режим", True, WHITE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))

        option1_text = "1. С компьютером"
        option1_surface = button_font.render(option1_text, True, WHITE if selected_option != 'computer' else GREY)
        option1_rect = option1_surface.get_rect(topleft=(WIDTH // 2 - option1_surface.get_width() // 2, 200))
        screen.blit(option1_surface, option1_rect)

        option2_text = "2. Против друга"
        option2_surface = button_font.render(option2_text, True, WHITE if selected_option != 'friend' else GREY)
        option2_rect = option2_surface.get_rect(topleft=(WIDTH // 2 - option2_surface.get_width() // 2, 300))
        screen.blit(option2_surface, (option2_rect))

        history_text = "3. История матчей"
        history_surface = button_font.render(history_text, True, WHITE if selected_option != 'history' else GREY)
        history_rect = history_surface.get_rect(topleft=(WIDTH // 2 - history_surface.get_width() // 2, 400))
        screen.blit(history_surface, (history_rect))

        main_menu_text = "4. Главное меню"
        main_menu_surface = button_font.render(main_menu_text, True, WHITE if selected_option != 'main_menu' else GREY)
        main_menu_rect = main_menu_surface.get_rect(topleft=(WIDTH // 2 - main_menu_surface.get_width() // 2, 500))
        screen.blit(main_menu_surface, (main_menu_rect))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                if option1_rect.collidepoint(mouse_pos):
                    selected_option = 'computer'
                elif option2_rect.collidepoint(mouse_pos):
                    selected_option = 'friend'
                elif history_rect.collidepoint(mouse_pos):
                    selected_option = 'history'
                elif main_menu_rect.collidepoint(mouse_pos):
                    selected_option = 'main_menu'
                else:
                    selected_option = None

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if option1_rect.collidepoint(event.pos):
                        menu = False
                        return "computer"
                    if option2_rect.collidepoint(event.pos):
                        menu = False
                        return "friend"
                    if history_rect.collidepoint(event.pos):
                        menu = False
                        return "history"
                    if main_menu_rect.collidepoint(mouse_pos):
                        menu = True
                        return 'main_menu'
    clock.tick(60)

# Основной игровой цикл для пинг-понга
def game_loop(mode):
    global player1_y, player2_y, score1, score2, ball_x, ball_y, ball_speed_x, ball_speed_y, game_over
    paused = False
    selected_main_menu = None
    selected_resume = None
    pause_button_size = 50
    pause_button_x = WIDTH // 2 - pause_button_size // 2
    pause_button_y = 30
    pause_button_rect = pygame.Rect(pause_button_x, pause_button_y, pause_button_size, pause_button_size)
    pause_icon = pygame.Surface((pause_button_size - 10, pause_button_size - 10))
    pause_icon.fill(WHITE)
    # Создаем значок паузы
    pygame.draw.rect(pause_icon, BLACK, (0, 0, (pause_button_size - 10) // 3, pause_button_size - 10))
    pygame.draw.rect(pause_icon, BLACK, ((pause_button_size - 10) * 2 // 3, 0, (pause_button_size - 10) // 3, pause_button_size - 10))

    # Кнопки паузы
    resume_button_rect = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 - 60, 250, 40)
    main_menu_button_rect = pygame.Rect(WIDTH // 2 - 160, HEIGHT // 2 + 10, 330, 40)

    # Переменные для ошибки компьютера
    last_error_time = time.time()
    error_interval = 3  # Интервал ошибки в секундах
    error_duration = 0.5  # Длительность ошибки в секундах
    in_error = False

    conn = init_db()
    if conn is None:
        return "main_menu"

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                conn.close()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused  # Переключение состояния паузы
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левый клик
                    if pause_button_rect.collidepoint(event.pos):
                        paused = not paused  # Переключение состояния паузы
                    elif paused:
                        if resume_button_rect.collidepoint(event.pos):
                            paused = False
                        elif main_menu_button_rect.collidepoint(event.pos):
                            return "main_menu"

        if paused:
            # Отображение сообщения "Пауза"
            pause_display_text = pause_font.render("Пауза", True, WHITE)
            screen.blit(pause_display_text, (WIDTH // 2 - pause_display_text.get_width() // 2, HEIGHT // 2 - 150))

            resume_text = button_font.render("Возобновить игру", True, WHITE if selected_resume != 1 else BLACK)
            #selected_resume_text = button_font.render("Возобновить игру", True, GREY)
            resume_text_rect = resume_text.get_rect(center=resume_button_rect.center)
            screen.blit(resume_text, resume_text_rect)

            main_menu_text = button_font.render("Выйти в главное меню", True, WHITE if selected_main_menu != 1 else BLACK)
            #selected_main_menu_text = button_font.render("Выйти в главное меню", True, GREY)
            main_menu_text_rect = main_menu_text.get_rect(center=main_menu_button_rect.center)
            screen.blit(main_menu_text, main_menu_text_rect)

            # Проверка наведения курсора на кнопки
            mouse_pos = pygame.mouse.get_pos()
            if resume_button_rect.collidepoint(mouse_pos):
                screen.blit(resume_text, resume_text_rect)
            if main_menu_button_rect.collidepoint(mouse_pos):
                screen.blit(main_menu_text, main_menu_text_rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEMOTION:
                    mouse_pos = event.pos
                    if resume_text_rect.collidepoint(mouse_pos):
                        selected_resume = 1
                    elif main_menu_button_rect.collidepoint((mouse_pos)):
                        selected_main_menu = 1
                    else:
                        selected_main_menu = 0
                        selected_resume = 0


            pygame.display.flip()
            continue  # Пропускаем остальную часть цикла, пока игра на паузе

        # Управление игроком 1
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and player1_y > 0:
            player1_y -= paddle_speed
        if keys[pygame.K_s] and player1_y < HEIGHT - paddle_height:
            player1_y += paddle_speed

        # Управление для компьютера или игрока 2
        current_time = time.time()
        if mode == "computer":
            if not in_error:
                error_chance = random.randint(1, 2)
                # Проверка на ошибку
                if current_time - last_error_time >= error_interval and error_chance == 2:
                    in_error = True
                    last_error_time = current_time
                    # Изменяем направление движения компьютера на противоположное
                    if player2_y + paddle_height // 2 < ball_y:
                        player2_y -= paddle_speed
                    else:
                        player2_y += paddle_speed
                else:
                    # Нормальное движение компьютера
                    if player2_y + paddle_height // 2 < ball_y:
                        player2_y += paddle_speed
                    elif player2_y + paddle_height // 2 > ball_y:
                        player2_y -= paddle_speed
            else:
                # Проверка, закончилась ли ошибка
                if current_time - last_error_time >= error_duration:
                    in_error = False
        else:
            # Управление игроком 2
            if keys[pygame.K_UP] and player2_y > 0:
                player2_y -= paddle_speed
            if keys[pygame.K_DOWN] and player2_y < HEIGHT - paddle_height:
                player2_y += paddle_speed

        # Ограничение движения ракетки
        player2_y = max(0, min(player2_y, HEIGHT - paddle_height))

        # Движение мяча
        ball_x += ball_speed_x
        ball_y += ball_speed_y

        # Отскок мяча от верхнего и нижнего края
        if ball_y <= 0 or ball_y >= HEIGHT - 20:
            ball_speed_y *= -1

        # Проверка столкновения с ракеткой игрока 1 (левая)
        if (player1_x - 5 < ball_x + ball_size < player1_x + paddle_width + 5) and (player1_y - 10 < ball_y
                                                                        < player1_y + paddle_height + 10):
            angle = math.atan2(ball_speed_y, ball_speed_x)
            angle += math.radians(random.randint(-80, 80)) # Изменение угла
            ball_speed_x = ball_speed * math.cos(angle)
            ball_speed_y = ball_speed * math.sin(angle)
            ball_speed_x *= -1  # Отражение по оси X
            ball_speed_x += acceleration if ball_speed_x > 0 else -acceleration
            ball_x = player1_x + paddle_width + 5  # Корректируем позицию мяча

        # Проверка столкновения с ракеткой игрока 2 (правая)
        if (player2_x - 5 < ball_x + ball_size < player2_x + paddle_width + 5) and (player2_y - 10 < ball_y
                                                                            < player2_y + paddle_height + 10):
            angle = math.atan2(ball_speed_y, ball_speed_x)
            angle += math.radians(random.randint(-80, 80))  # Изменение угла
            ball_speed_x = ball_speed * math.cos(angle)
            ball_speed_y = ball_speed * math.sin(angle)
            ball_speed_x *= -1  # Отражение по оси X
            ball_speed_x += acceleration if ball_speed_x > 0 else -acceleration
            ball_x = player2_x - ball_size - 5  # Корректируем позицию мяча

        # Проверка на голы и сброс мяча в центр поля.
        if ball_x <= 0:
            score2 += 1
            ball_x, ball_y = WIDTH // 2, HEIGHT // 2
            ball_speed_x, ball_speed_y = set_ball_velocity()
            ball_speed_x = -ball_speed_x  # Меняем направление мяча при сбросе.

        if ball_x >= WIDTH:
            score1 += 1
            ball_x, ball_y = WIDTH // 2, HEIGHT // 2
            ball_speed_x, ball_speed_y = set_ball_velocity()
            ball_speed_x = ball_speed_x  # Меняем направление мяча при сбросе.

        # Проверка на окончание игры
        if score1 >= 11 or score2 >= 11:
            save_score(conn, score1, score2)
            game_over = True
            break
        screen.fill(TABLE_BLUE)
        screen.blit(img, (0, 0))

        # Рисуем ракетки и мяч.
        pygame.draw.rect(screen, PADDLE_RED, (player1_x, player1_y, paddle_width, paddle_height))
        pygame.draw.rect(screen, PADDLE_RED, (player2_x, player2_y, paddle_width, paddle_height))
        pygame.draw.ellipse(screen, WHITE, (ball_x, ball_y, ball_size, ball_size))

        # Рисуем центральную линию.
        pygame.draw.aaline(screen, LINE_GRAY, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))

        # Отображение счета.
        text1 = font.render(str(score1), True, WHITE)
        text2 = font.render(str(score2), True, WHITE)

        screen.blit(text1, (WIDTH // 4, 20))
        screen.blit(text2, (WIDTH * 3 // 4, 20))

        # Рисуем кнопку паузы.
        pygame.draw.rect(screen, LIGHT_GREY, pause_button_rect)
        screen.blit(pause_icon, (pause_button_rect.x + 5, pause_button_rect.y + 5))
        # Проверка наведения курсора на кнопку паузы
        mouse_pos = pygame.mouse.get_pos()
        if pause_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, HOVER_GREY, pause_button_rect, 3)
        else:
            pygame.draw.rect(screen, BUTTON_BORDER, pause_button_rect, 3)

        pygame.display.flip()
        clock.tick(120)

    while game_over == True:
        game_over_text = game_over_font.render("Игра окончена", True, WHITE)
        winner_text = game_over_font.render(f"Победитель: {'Игрок 1' if score1 > score2 else 'Игрок 2'}", True, WHITE)

        screen.fill(BLACK)
        screen.blit(chil, (342, 58))
        screen.blit(chil1, (-342, 58))
        #screen.blit(img, (0, 0))
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 250))
        screen.blit(winner_text, (WIDTH // 2 - winner_text.get_width() // 2, HEIGHT // 2 - 200))

        # Кнопка для выхода в главное меню
        main_menu_button_rect = pygame.Rect(WIDTH // 2 - 157, HEIGHT // 2 + 150, 300, 30)
        main_menu_text = button_font.render("Выйти в главное меню", True, WHITE if selected_main_menu != 1 else GREY)
        screen.blit(main_menu_text, (WIDTH // 2 - 157, HEIGHT // 2 + 150))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                conn.close()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and main_menu_button_rect.collidepoint(event.pos):
                    return "main_menu"
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                if main_menu_button_rect.collidepoint(mouse_pos):
                    selected_main_menu = 1
                else:
                    selected_main_menu = None

# Запуск меню и игры.
def main():
    while True:
        mode = main_menu()
        if mode == "main_menu":
            continue
        elif mode == "block_blast":
            block_blast()
        elif mode == "ping_pong":
            ping_pong()

if __name__ == "__main__":
    main()