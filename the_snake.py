from random import randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов.

    Предоставляет общую структуру для объектов игры (позиция и цвет).
    Является абстрактным базовым классом: метод `draw` должен быть
    переопределён в дочерних классах.
    """

    def __init__(self, position=None, body_color=''):
        """Инициализирует игровой объект.

        Args:
            position (tuple[int, int] | None): Начальная позиция объекта
            в пикселях. Если None, устанавливается в центр экрана.
            body_color (tuple[int, int, int]): Цвет объекта в формате RGB.
        """
        if position is None:
            self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        else:
            self.position = position

        self.body_color = body_color

    def draw(self):
        """Отрисовывает объект на игровом экране.

        Этот метод является абстрактным и должен быть переопределён
        в дочерних классах, так как логика отрисовки зависит от типа объекта.
        """
        pass


class Apple(GameObject):
    """Класс, описывающий игровой объект «яблоко».

    Отвечает за генерацию случайной позиции яблока и его отрисовку
    на игровом поле.
    """

    def __init__(self, position=None, body_color=APPLE_COLOR):
        """Создаёт экземпляр яблока.

        Если позиция не указана, она генерируется случайным образом.

        Args:
            position (tuple[int, int] | None): Позиция яблока в пикселях.
            body_color (tuple[int, int, int]): Цвет яблока
            (по умолчанию — красный).
        """
        if position is None:
            position = self.randomize_position()

        super().__init__(position, body_color)

    def randomize_position(self):
        """Устанавливает случайное положение яблока на игровом поле.

        Позиция выбирается строго по сетке, чтобы совпадать с ячейками поля.

        Returns:
            tuple[int, int]: Новые координаты яблока (x, y) в пикселях.
        """
        new_x = randint(0, SCREEN_WIDTH // GRID_SIZE - 1) * GRID_SIZE
        new_y = randint(0, SCREEN_HEIGHT // GRID_SIZE - 1) * GRID_SIZE

        self.position = (new_x, new_y)

        return self.position

    def draw(self):
        """Отрисовывает яблоко на игровой поверхности.

        Яблоко рисуется как цветной прямоугольник с обводкой по сетке.
        """
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс, описывающий игровой объект «змейка».

    Управляет движением, ростом, отрисовкой и сбросом состояния змейки.
    Поддерживает запрет разворота на 180 градусов и циклические границы поля.
    """

    def __init__(
            self,
            position=None,
            body_color=SNAKE_COLOR,
    ):
        """Инициализирует змейку.

        Args:
            position (tuple[int, int] | None): Начальная позиция головы змейки.
            Если None, устанавливается в центр экрана.
            body_color (tuple[int, int, int]):
            Цвет змейки (по умолчанию — зелёный).
        """
        if position is None:
            position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        # positions хранит список сегментов змейки от головы к хвосту
        self.positions = [position]

        super().__init__(position, body_color)

        self.direction = (1, 0)
        self.length = 1
        self.next_direction = None
        self.last = None

    def update_direction(self):
        """Обновляет направление движения змейки после обработки ввода.

        Применяет сохранённое в `next_direction` направление, если оно есть.
        Это предотвращает «перескакивание» направления при быстрых нажатиях.
        """
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self, grow_this_frame=False):
        """Выполняет один шаг движения змейки.

        Обновляет позиции сегментов, обрабатывает столкновение с собственным
        телом и реализует рост змейки, если она съела яблоко.
        Границы поля — циклические.

        Args:
            grow_this_frame (bool): Если True,
            змейка увеличивается на один сегмент
            в этом кадре (после поедания яблока).
        """
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction

        new_x = (head_x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        new_head = (new_x, new_y)

        # Проверка столкновения с собственным телом (кроме головы)
        if new_head in self.positions[1:]:
            self.reset()
            return

        self.positions.insert(0, new_head)

        if grow_this_frame:
            # Сохраняем последний сегмент, чтобы добавить его ещё раз (рост)
            last_segment = self.positions[-1]
            self.positions.append(last_segment)
        else:
            # Удаляем последний сегмент (движение без роста)
            self.positions.pop()

        self.position = self.positions[0]

    def draw(self):
        """Отрисовывает змейку на игровой поверхности.

        Рисует все сегменты змейки с обводкой, отдельно выделяет голову
        и затирает старый последний сегмент, если он есть.
        """
        # Отрисовка тела (все сегменты, кроме головы)
        for position in self.positions[:-1]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента на старом месте
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self):
        """Возвращает координаты головы змейки.

        Returns:
            tuple[int, int]: Позиция головы (x, y) в пикселях.
        """
        return self.positions[0]

    def reset(self):
        """Сбрасывает состояние змейки к начальному.

        Устанавливает позицию в центр, направление вправо, длину 1,
        очищает флаги и временные переменные.
        """
        start_position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.positions = [start_position]
        self.direction = (1, 0)
        self.next_direction = None
        self.last = None

        # Обновляем позицию базового класса
        super().__init__(start_position, self.body_color)


def handle_keys(game_object):
    """Обрабатывает события ввода (нажатия клавиш) и закрытие окна.

    Проверяет очередь событий PyGame, реагирует на нажатие клавиш-стрелок
    с учётом запрета разворота на 180 градусов, а также корректно завершает
    игру при попытке закрыть окно.

    Args:
        game_object (Snake): Экземпляр змейки,
        которому передаются новые направления.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Основная функция игры.

    Инициализирует PyGame, создаёт экземпляры яблока и змейки,
    запускает игровой цикл: обработка ввода, обновление логики, отрисовка.
    """
    pygame.init()
    apple = Apple()
    snake = Snake()

    while True:

        handle_keys(snake)
        snake.update_direction()

        ate_apple = snake.get_head_position() == apple.position

        if ate_apple:
            apple.randomize_position()

        snake.move(grow_this_frame=ate_apple)

        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()
        pygame.display.update()
        clock.tick(SPEED)


if __name__ == '__main__':
    main()
