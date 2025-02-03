import pygame
import sys
import random

import shapes
import highscore
import Ping_Pong

# Инициализация Pygame
pygame.init()

# Константы для размеров экрана и цветов
INIT_WIDTH = 1300
INIT_HEIGHT = 900
BACKGROUND_COLOR = (220, 220, 220)
FPS = 60
TRANSITION_SPEED = 255 // 17

clock = pygame.time.Clock()


def main():
    # Установка основного экрана игры
    main_screen = pygame.display.set_mode((INIT_WIDTH, INIT_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Block Blast")
    # Толщина линий сетки
    grid_line_width = 2

    # Инициализация игровой сетки (8x8) с нулями
    grid = [[0, 0, 0, 0, 0, 0, 0, 0] for i in range(8)]

    chosen_shape = -1  # Изначально форма не выбрана
    current_shapes = shapes.generate_shapes()  # Генерация начальных форм
    slide_animation = False
    shape_animation_dist = 0
    shape_animation_velocity = 0

    transition_in = True
    fade_alpha = 255
    transition_out = False

    score = 0
    displayed_score = 0
    highest_score = highscore.get_score()

    combos = [["COMBO 0"], 0]
    combo_streak = False
    combo_names = {1: "", 2: "DOUBLE ", 3: "TRIPLE ", 4: "QUAD ", 5: "PENTA ", 6: "HEXA "}

    game_over = False
    game_over_alpha = 0
    game_over_text = 'YOUR SCORE'

    def fade_in():
        """Постепенное появление экрана (эффект затемнения)."""
        nonlocal fade_alpha, transition_in

        curr_main_width, curr_main_height = main_screen.get_size()

        # Уменьшение значения альфа-канала для эффекта появления
        fade_alpha = max(0, fade_alpha - TRANSITION_SPEED)

        transition_screen = pygame.Surface((curr_main_width, curr_main_height), pygame.SRCALPHA)
        transition_screen.fill((220, 220, 220, fade_alpha))
        main_screen.blit(transition_screen, (0, 0))

        if fade_alpha == 0:
            transition_in = False

    def fade_out():
        """Постепенное исчезновение экрана (эффект затемнения) и перезапуск игры."""
        nonlocal fade_alpha, transition_out

        curr_main_width, curr_main_height = main_screen.get_size()

        # Увеличение значения альфа-канала для эффекта исчезновения
        fade_alpha = min(255, fade_alpha + TRANSITION_SPEED)

        transition_screen = pygame.Surface((curr_main_width, curr_main_height), pygame.SRCALPHA)
        transition_screen.fill((220, 220, 220, fade_alpha))
        main_screen.blit(transition_screen, (0, 0))

        if fade_alpha == 255:
            main()  # Перезапуск игры при полном исчезновении экрана

    def handle_events():
        """Обработка пользовательских событий (клавиатура и мышь)."""
        nonlocal chosen_shape, transition_out

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_BACKSPACE:
                    transition_out = True
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3] and not game_over:
                    mapping = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2}
                    if mapping[event.key] == chosen_shape:
                        chosen_shape = -1
                    else:
                        chosen_shape = mapping[event.key]
                if event.key == pygame.K_SPACE:
                    place_shape()  # Размещение выбранной формы на сетке
            elif event.type == pygame.MOUSEBUTTONDOWN:
                place_shape()  # Размещение формы при клике мыши

    def draw_grid():
        """Отрисовка игровой сетки."""
        curr_main_width, curr_main_height = main_screen.get_size()
        grid_padding = curr_main_height // 10  # значения верхнего и нижнего отступов
        grid_side = curr_main_height - 2 * grid_padding
        grid_side = grid_side - (grid_side % 8) + (
                grid_line_width * 7)
        grid_screen = pygame.Surface((grid_side, grid_side))
        grid_pos_x, grid_pos_y = (curr_main_width / 2) - (grid_side / 2), grid_padding

        grid_screen.fill((255, 255, 255))
        rect_padding = 2
        outline_rect_side = grid_side + 2 * rect_padding
        outline_rect = pygame.Rect(grid_pos_x - rect_padding, grid_pos_y - rect_padding, outline_rect_side,
                                   outline_rect_side)
        # Рисуем контур сетки.
        pygame.draw.rect(main_screen, (0, 0, 0), outline_rect)

        # Рисуем линии сетки.
        start_lines_pos = (grid_side - grid_line_width * 7) / 8
        for i in range(7):
            pygame.draw.line(grid_screen,
                             (200, 200, 200),
                             (0, start_lines_pos),
                             (grid_side,
                              start_lines_pos),
                             grid_line_width)
            pygame.draw.line(grid_screen, (200, 200, 200), (start_lines_pos, 0), (start_lines_pos, grid_side),
                             grid_line_width)
            start_lines_pos += (grid_side - grid_line_width * 7) / 8 + grid_line_width

        # Рисуем заполненные квадраты в зависимости от состояния сетки.
        square_side = (grid_side - grid_line_width * 7) / 8
        for i in range(8):
            for j in range(8):
                if (grid[i][j]):
                    pos_x = (square_side + grid_line_width) * j
                    pos_y = (square_side + grid_line_width) * i
                    square = pygame.Rect(pos_x, pos_y, square_side, square_side)
                    bg_square = pygame.Rect(pos_x - 2, pos_y - 2, square_side + 4, square_side + 4)
                    pygame.draw.rect(grid_screen, (0, 0, 0), bg_square)
                    pygame.draw.rect(grid_screen, grid[i][j], square)

        main_screen.blit(grid_screen, (grid_pos_x, grid_pos_y))

    def draw_exit_button():
        """Отрисовка кнопки выхода в главное меню."""

        button_width = 100
        button_height = 100
        button_x = 35  # Отступ от правого края экрана
        button_y = INIT_HEIGHT - button_height - 35  # Отступ от нижнего края экрана

        exit_button = pygame.Rect(button_x, button_y, button_width, button_height)

        # Рисуем кнопку с текстом "В меню"
        pygame.draw.rect(main_screen, (100, 100, 100), exit_button)  # Красный цвет кнопки

        font_button = pygame.font.Font(None, 36)
        text_surface = font_button.render("В меню", True, (255, 255, 255))  # Белый текст на кнопке
        text_rect = text_surface.get_rect(center=exit_button.center)
        main_screen.blit(text_surface, text_rect)
        '''for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and exit_button.collidepoint(event.pos):
                    Ping_Pong.main_menu()'''

    def check_game_over():
        """Проверка окончания игры по наличию возможных размещений."""
        nonlocal game_over

        game_over = True
        # Проверяем каждую форму на возможность размещения на доске.
        for shape in current_shapes:
            if shape:
                size = [len(shape.form), len(shape.form[0])]

                for i in range(8):
                    for j in range(8):
                        valid = True
                        for i1 in range(size[0]):
                            for j1 in range(size[1]):
                                if shape.form[i1][j1]:
                                    if (i + i1 > 7) or (j + j1 > 7) or grid[i + i1][j + j1]:
                                        valid = False

                        if valid:
                            game_over = False
                            return None

    def place_shape():
        """Размещает выбранную форму на игровом поле."""
        nonlocal chosen_shape, current_shapes, slide_animation, combo_streak

        # Убедимся что форма выбрана перед размещением.
        if chosen_shape != -1 and current_shapes[chosen_shape]:
            curr_main_width, curr_main_height = main_screen.get_size()
            grid_padding = curr_main_height // 10
            grid_side = curr_main_height - 2 * grid_padding
            grid_side = grid_side - (grid_side % 8) + (grid_line_width * 7)
            grid_pos_x, grid_pos_y = (curr_main_width / 2) - (grid_side / 2), grid_padding
            square_side = (grid_side - grid_line_width * 7) / 8
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Корректируем координаты мыши для размещения блока
            mouse_x -= square_side / 2
            mouse_y -= square_side / 2

            chosen_square = [-1, -1]
            lowest_distance = float('inf')
            # Определяем ближайший квадрат к месту клика мыши.
            for i in range(8):
                for j in range(8):
                    current_pos = [grid_pos_x + (j + 0.5) * square_side, grid_pos_y + (i + 0.5) * square_side]
                    distance = (current_pos[0] - mouse_x) ** 2 + (current_pos[1] - mouse_y) ** 2
                    if distance < lowest_distance:
                        lowest_distance = distance
                        chosen_square = [i, j]

            shape = current_shapes[chosen_shape]
            size = [len(shape.form), len(shape.form[0])]
            valid_placement = True
            to_change = []

            # Проверяем возможность размещения формы на доске.
            for i in range(size[0]):
                for j in range(size[1]):
                    if shape.form[i][j] != 0:
                        pos_square = (chosen_square[0] - size[0] + 1 + i, chosen_square[1] - size[1] + 1 + j)
                        if pos_square[0] < 0 or pos_square[1] < 0 or grid[pos_square[0]][pos_square[1]]:
                            valid_placement = False
                        else:
                            to_change.append(pos_square)

            if valid_placement:
                current_shapes[chosen_shape] = 0
                chosen_shape = -1

                # Обновляем доску с новыми размещениями форм.
                for square in to_change:
                    grid[square[0]][square[1]] = shape.color

                update_grid()

                # Если все формы были размещены в этом раунде.
                if set(current_shapes) == {0}:
                    if not combo_streak:
                        combos[1] = 0
                        combos[0][-1] = "COMBO 0"
                    combo_streak = False
                    current_shapes = shapes.generate_shapes()
                    slide_animation = True

                check_game_over()

    def draw_shapes():
        """Отрисовка доступных форм на экране."""
        nonlocal shape_animation_dist, slide_animation, shape_animation_velocity

        curr_main_width, curr_main_height = main_screen.get_size()
        grid_padding = curr_main_height // 10
        grid_side = curr_main_height - 2 * grid_padding
        grid_side = grid_side - (grid_side % 8) + (grid_line_width * 7)
        grid_pos_x, grid_pos_y = (curr_main_width / 2) - (grid_side / 2), grid_padding
        square_side = grid_pos_x // 11.5

        if slide_animation:
            shape_animation_dist = grid_pos_x * 1.5
            shape_animation_velocity = shape_animation_dist / 10
            slide_animation = False
        if shape_animation_dist:
            shape_animation_dist = max(1, shape_animation_dist - shape_animation_velocity)
            if (shape_animation_dist == 1): shape_animation_dist = 0
            shape_animation_velocity = shape_animation_dist / 10

        center_x = (grid_pos_x * 1.5) + (grid_side + 4) + shape_animation_dist
        shapes_margin = curr_main_height // 4
        center_y = [shapes_margin, shapes_margin * 2, shapes_margin * 3]

        for cshape in range(3):
            shape = current_shapes[cshape]
            if (chosen_shape != cshape and shape):
                size = [len(shape.form), len(shape.form[0])]

                for i in range(size[0]):
                    for j in range(size[1]):
                        if shape.form[i][j]:
                            pos_x = center_x - (square_side * size[1] // 2) + j * (square_side + 2)
                            pos_y = center_y[cshape] - (square_side * size[0] // 2) + i * (square_side + 2)
                            square = pygame.Rect(pos_x, pos_y, square_side, square_side)
                            bg_square = pygame.Rect(pos_x - 2, pos_y - 2, square_side + 4, square_side + 4)

                            # Рисуем фон и заполненные квадраты форм.
                            pygame.draw.rect(main_screen, (0, 0, 0), bg_square)
                            pygame.draw.rect(main_screen, shape.color, square)

    def draw_cursor():
        """Рисует курсор для выбранной формы."""
        if chosen_shape != -1 and current_shapes[chosen_shape]:
            curr_main_width, curr_main_height = main_screen.get_size()
            grid_padding = curr_main_height // 10
            grid_side = curr_main_height - 2 * grid_padding
            grid_side = grid_side - (grid_side % 8) + (grid_line_width * 7)
            square_side = (grid_side - grid_line_width * 7) // 8

            shape = current_shapes[chosen_shape]
            size = [len(shape.form), len(shape.form[0])]

            mouse_x, mouse_y = pygame.mouse.get_pos()

            for i in range(size[0]):
                for j in range(size[1]):
                    if shape.form[i][j]:
                        pos_x = mouse_x - (square_side + grid_line_width) * (size[1] + 0.5 - j)
                        pos_y = mouse_y - (square_side + grid_line_width) * (size[0] + 0.5 - i)
                        square = pygame.Rect(pos_x, pos_y, square_side, square_side)
                        bg_square = pygame.Rect(pos_x - 2, pos_y - 2, square_side + 4, square_side + 4)
                        pygame.draw.rect(main_screen, (0, 0, 0), bg_square)
                        pygame.draw.rect(main_screen, shape.color, square)

    def update_grid():
        """Обновление игровой доски путем очистки завершенных строк и столбцов."""
        nonlocal score, combo_streak

        rows_to_delete = []
        cols_to_delete = []

        # Проверяем каждую строку и столбец на полноту.
        for i in range(8):
            valid_row = True
            valid_col = True
            for j in range(8):
                if not grid[i][j]:
                    valid_row = False
                if not grid[j][i]:
                    valid_col = False

            if valid_row:
                rows_to_delete.append(i)
            if valid_col:
                cols_to_delete.append(i)

        # Очищаем завершенные строки из доски.
        for row in rows_to_delete:
            for i in range(8):
                grid[row][i] = 0

        # Очищаем завершенные столбцы из доски.
        for col in cols_to_delete:
            for i in range(8):
                grid[i][col] = 0

        all_clear = True

        # Проверяем остались ли какие-либо квадраты на доске.
        for i in range(8):
            for j in range(8):
                if grid[i][j]:
                    all_clear = False

        # Обновляем счет на основе очищенных линий.
        lines_cleared = len(rows_to_delete) + len(cols_to_delete)
        if lines_cleared:

            bonus = lines_cleared * 10 * (combos[1] + 1)
            if lines_cleared > 2:
                bonus *= lines_cleared - 1

            combo = combo_names[lines_cleared] + f"CLEAR +{bonus}"
            combos[0].insert(-1, combo)
            if all_clear:
                bonus += 300
                combos[0].insert(-1, "ALL CLEAR +300")
            combos[0] = combos[0][-8:]

            combos[1] += 1
            combos[0][-1] = f"COMBO {combos[1]}"
            combo_streak = True
            score += bonus

    def draw_game_over():
        """Отображение экрана окончания игры с финальным счетом и сообщением."""
        nonlocal game_over_alpha, highest_score, game_over_text

        curr_main_width, curr_main_height = main_screen.get_size()

        game_over_alpha = min(220, game_over_alpha + TRANSITION_SPEED)

        transition_screen = pygame.Surface((curr_main_width, curr_main_height), pygame.SRCALPHA)
        transition_screen.fill((220, 220, 220))
        transition_screen.set_alpha(game_over_alpha)

        text_screen = pygame.Surface((curr_main_width, curr_main_height), pygame.SRCALPHA)
        text_screen.set_alpha(game_over_alpha + 20)

        # Проверяем и обновляем лучший счет.
        if score > highest_score:
            game_over_text = 'NEW RECORD'
            highscore.save_score(score)
            highest_score = highscore.get_score()

        font_text = pygame.font.Font('шрифт/LECO.ttf', curr_main_width // 13)
        text = font_text.render(game_over_text, True, (140, 140, 140))
        text_rect = text.get_rect()
        text_rect.center = (curr_main_width // 2, (curr_main_height // 20) * 7.5)
        text_screen.blit(text, text_rect)

        font_score = pygame.font.Font('шрифт/LECO.ttf', curr_main_width // 15)
        score_text = font_score.render(str(score), True, (140, 140, 140))
        score_rect = score_text.get_rect()
        score_rect.center = (curr_main_width // 2, (curr_main_height // 20) * 12.5)
        text_screen.blit(score_text, score_rect)

        main_screen.blit(transition_screen, (0, 0))
        main_screen.blit(text_screen, (0, 0))

    def draw_score():
        """Отрисовывка текущего и лучшего счета на экране."""
        nonlocal displayed_score

        curr_main_width, curr_main_height = main_screen.get_size()
        grid_padding = curr_main_height // 10

        font_highest = pygame.font.Font('шрифт/LECO.ttf', int(grid_padding / 2))
        text_highest = font_highest.render("HIGH SCORE", True, (135, 135, 135))
        text_highest_value = font_highest.render(str(highest_score), True, (135, 135, 135))
        main_screen.blit(text_highest, (grid_padding // 3, grid_padding // 6))
        main_screen.blit(text_highest_value, (grid_padding // 3, grid_padding // 1.3))

        font_score = pygame.font.Font('шрифт/LECO.ttf', int(grid_padding / 1.3))
        score_text = font_score.render(str(displayed_score), True, (135, 135, 135))
        score_rect = score_text.get_rect()
        score_rect.center = (curr_main_width // 2, grid_padding // 2)
        main_screen.blit(score_text, score_rect)

        if displayed_score < score:
            displayed_score += max(1, (score - displayed_score) // 40)
            displayed_score = min(score, displayed_score)

    def draw_combos():
        '''Отображение надписи "KOMBO" на экране'''
        curr_main_width, curr_main_height = main_screen.get_size()
        grid_padding = curr_main_height // 10
        grid_side = curr_main_height - 2 * grid_padding
        grid_side = grid_side - (grid_side % 8) + (grid_line_width * 7)
        grid_pos_x, grid_pos_y = (curr_main_width / 2) - (grid_side / 2), grid_padding

        combos_padding = grid_pos_x // 10

        combo_screen_x = grid_pos_x - combos_padding * 2
        combo_screen_y = grid_pos_x - combos_padding * 4
        combos_screen = pygame.Surface((combo_screen_x, combo_screen_y))
        combos_screen.fill(BACKGROUND_COLOR)

        combo_pos_x = (grid_pos_x / 2) - (combo_screen_x / 2)
        combo_pos_y = (curr_main_height / 2) - (combo_screen_y / 2)

        j = 1
        for i in range(len(combos[0]) - 1, -1, -1):
            font_size = int(grid_padding / 3)
            font_combo = pygame.font.Font('шрифт/LECO.ttf', font_size)
            text_combo = font_combo.render(combos[0][i], True, (135, 135, 135))
            combos_screen.blit(text_combo, (0, combo_screen_y - font_size * j))

            j += 1

        main_screen.blit(combos_screen, (combo_pos_x, combo_pos_y))

    # Основной цикл для запуска игры до тех пор пока не будет выполнено условие выхода.
    def draw_main():
        main_screen.fill(BACKGROUND_COLOR)

        draw_grid()
        draw_shapes()
        draw_score()
        draw_combos()
        draw_cursor()
        draw_exit_button()

        if game_over:
            draw_game_over()
        if transition_in:
            fade_in()
        elif transition_out:
            fade_out()

        pygame.display.flip()

    while True:
        handle_events()

        draw_main()

        clock.tick(FPS)

def perehod():
    flag = draw_exit_button()
    if flag == True:
        main()
    else:
        main_screen.fill((0, 0, 0))

if __name__ == "__main__":
    main()
