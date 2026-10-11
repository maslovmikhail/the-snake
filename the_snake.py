from random import randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Центр экрана
SCREEN_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

BOARD_BACKGROUND_COLOR = (60, 60, 60)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

REVERSE_DIRECTIONS = {
    (LEFT, pg.K_UP): UP,
    (RIGHT, pg.K_UP): UP,
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_DOWN): DOWN,
    (UP, pg.K_LEFT): LEFT,
    (DOWN, pg.K_LEFT): LEFT,
    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_RIGHT): RIGHT,
}

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка. Для выхода из игры нажмите ESC')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов.

    Предоставляет общую структуру для объектов игры (позиция и цвет).
    Является абстрактным базовым классом: метод `draw` должен быть
    переопределён в дочерних классах.
    """

    def __init__(self, position=SCREEN_CENTER, body_color=()):
        """Инициализирует игровой объект.

        Args:
            position (tuple[int, int] | None): Начальная позиция объекта
            в пикселях. Если None, устанавливается в центр экрана.
            body_color (tuple[int, int, int]): Цвет объекта в формате RGB.
        """
        self.body_color = body_color
        self.position = position

    def draw(self):
        """Отрисовывает объект на игровом экране.

        Этот метод является абстрактным и должен быть переопределён
        в дочерних классах, так как логика отрисовки зависит от типа объекта.
        """
        raise NotImplementedError(
            f'Метод draw() не реализован в {type(self).__name__}')

    def draw_cell(self, position, color=()):
        """
        Отрисовывает одну ячейку объекта.

        :param position: Кортеж (x, y) - позиция в клетках.
        :param color: Цвет ячейки. Если не указан,
        используется self.body_color.
        """
        color = color or self.body_color
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        if color != BOARD_BACKGROUND_COLOR:
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Класс, описывающий игровой объект «яблоко».

    Отвечает за генерацию случайной позиции яблока и его отрисовку
    на игровом поле.
    """

    def __init__(self, busy_cells=()):
        """Создаёт экземпляр яблока.

        Args:
            busy_cells (tuple[int, int]): Набор занятых ячеек.
            body_color (tuple[int, int, int]): Цвет яблока.
        """
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position(busy_cells)

    def randomize_position(self, busy_cells):
        """Устанавливает случайное положение яблока на игровом поле.

        Позиция выбирается строго по сетке, чтобы совпадать с ячейками поля.
        """
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if self.position not in busy_cells:
                break

    def draw(self):
        """Отрисовывает яблоко на игровой поверхности."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Класс, описывающий игровой объект «змейка».

    Управляет движением, ростом, отрисовкой и сбросом состояния змейки.
    Поддерживает запрет разворота на 180 градусов и циклические границы поля.
    """

    def __init__(self):
        """Инициализирует змейку.

        Args:
            body_color (tuple[int, int, int]): Цвет змейки.
        """
        super().__init__(body_color=SNAKE_COLOR)

        self.reset()

    def update_direction(self, new_direction):
        """Обновляет направление движения змейки после обработки ввода.

        Применяет сохранённое в `new_direction` направление, если оно есть.
        Это предотвращает «перескакивание» направления при быстрых нажатиях.
        """
        self.direction = new_direction

    def move(self):
        """Выполняет один шаг движения змейки."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction

        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def draw(self):
        """Отрисовывает змейку на игровой поверхности."""
        self.draw_cell(self.get_head_position())

        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR)

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает состояние змейки к начальному."""
        self.length = 1
        self.positions = [SCREEN_CENTER]
        self.direction = RIGHT
        self.last = None


def handle_keys(snake):
    """Обрабатывает события ввода (нажатия клавиш) и закрытие окна."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                raise SystemExit

            new_direction = REVERSE_DIRECTIONS.get(
                (snake.direction, event.key),
                snake.direction,
            )
            snake.update_direction(new_direction)


def main():
    """Основная функция игры.

    Инициализирует PyGame, создаёт экземпляры яблока и змейки,
    запускает игровой цикл: обработка ввода, обновление логики, отрисовка.
    """
    pg.display.init()
    snake = Snake()
    apple = Apple(busy_cells=snake.position)

    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        handle_keys(snake)
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.position)
        elif snake.get_head_position() in snake.positions[1:]:
            screen.fill(BOARD_BACKGROUND_COLOR)
            snake.reset()
            apple.randomize_position(snake.position)

        apple.draw()
        snake.draw()
        pg.display.update()
        clock.tick(SPEED)


if __name__ == '__main__':
    main()
