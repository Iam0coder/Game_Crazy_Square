import pygame
import random


# Класс Player описывает игрока (квадратик) в игре.
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, size, screen_width, screen_height):
        super().__init__()
        # Создание изображения для спрайта игрока
        self.image = pygame.Surface([size, size])
        self.image.fill((0, 255, 0))  # Зеленый квадрат
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)  # Начальное положение игрока
        self.screen_width = screen_width  # Ширина экрана
        self.screen_height = screen_height  # Высота экрана

    # Обновление позиции игрока с помощью координат мыши
    def update(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        # Устанавливает позицию игрока в зависимости от положения курсора мыши, не выходя за границы экрана
        self.rect.centerx = max(0, min(self.screen_width, mouse_x))
        self.rect.centery = max(0, min(self.screen_height, mouse_y))


# Класс Enemy описывает врагов, которые движутся к игроку.
class Enemy(pygame.sprite.Sprite):
    def __init__(self, screen_width, screen_height, size, initial_speed):
        super().__init__()
        self.image = pygame.Surface([size, size], pygame.SRCALPHA)  # Создание изображения с прозрачным фоном
        self.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.image, (255, 255, 255), (size // 2, size // 2), size // 2)  # Белый круг
        self.rect = self.image.get_rect()
        self.set_random_position(screen_width, screen_height)  # Рандомная позиция при создании
        self.speed = initial_speed  # Скорость движения врага
        self.player_pos = (screen_width // 2, screen_height // 2)  # Позиция игрока для навигации

    # Установка случайной начальной позиции врага
    def set_random_position(self, screen_width, screen_height):
        if random.choice([True, False]):
            self.rect.x = random.choice([0, screen_width - self.rect.width])
            self.rect.y = random.randint(0, screen_height - self.rect.height)
        else:
            self.rect.x = random.randint(0, screen_width - self.rect.width)
            self.rect.y = random.choice([0, screen_height - self.rect.height])

    # Обновление позиции врага, движение к позиции игрока
    def update(self, player_pos):
        self.player_pos = player_pos
        dir_vector = pygame.math.Vector2(self.player_pos[0] - self.rect.centerx, self.player_pos[1] - self.rect.centery)
        if dir_vector.length() > 0:
            dir_vector = dir_vector.normalize()  # Нормализация вектора для равномерного движения
        self.rect.x += int(dir_vector.x * self.speed)
        self.rect.y += int(dir_vector.y * self.speed)


# Класс Game управляет основными аспектами игры.
class Game:
    def __init__(self):
        pygame.init()
        self.screen_width, self.screen_height = 800, 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Crazy Square")
        self.clock = pygame.time.Clock()
        self.player = Player(self.screen_width // 2, self.screen_height // 2, 30, self.screen_width, self.screen_height)
        self.enemies = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group(self.player)
        self.running = True
        self.start_ticks = pygame.time.get_ticks()
        self.difficulty = 1
        self.last_difficulty_increase_time = self.start_ticks

    # Основной цикл игры
    def run(self):
        while self.running:
            self.handle_events()  # Обработка событий
            if not self.running:
                break  # Прервать цикл, если игра должна остановиться
            self.update_game()
            self.render()
        pygame.quit()  # Закрытие Pygame после выхода из цикла

    # Обработка событий (нажатие клавиш)
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.restart_game()

    # Обновление игры (логика игры)
    def update_game(self):
        self.player.update()
        self.enemies.update(self.player.rect.center)
        if pygame.sprite.spritecollide(self.player, self.enemies, False):
            self.game_over()
        self.spawn_enemies()
        self.update_difficulty()

    # Отрисовка элементов на экране
    def render(self):
        if not self.running:  # Проверка, что игра все еще запущена перед рисованием
            return
        self.screen.fill((0, 0, 0))  # Очистка экрана
        self.all_sprites.draw(self.screen)
        self.render_time()
        pygame.display.flip()
        self.clock.tick(60)  # Ограничение кадров в секунду

    # Перезапуск игры
    def restart_game(self):
        self.enemies.empty()
        self.all_sprites = pygame.sprite.Group(self.player)
        self.start_ticks = pygame.time.get_ticks()
        self.running = True

    # Действия при окончании игры
    def game_over(self):
        font = pygame.font.Font(None, 60)
        game_over_surface = font.render("Игра окончена! Нажмите Пробел!", True, (255, 0, 0))
        self.screen.blit(game_over_surface, (self.screen_width // 2 - game_over_surface.get_width() // 2,
                                             self.screen_height // 2 - game_over_surface.get_height() // 2))
        pygame.display.flip()
        self.difficulty = 1
        self.running = False  # Установить, что игра не запущена
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return  # Выход из цикла и функции
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.restart_game()
                        return

    # Создание врагов в игре
    def spawn_enemies(self):
        spawn_rate = max(1, 5 - self.difficulty)
        if random.randint(1, 1000) <= spawn_rate * self.difficulty:
            initial_speed = max(2, self.difficulty) # Скорость появления врагов
            enemy = Enemy(self.screen_width, self.screen_height, 20, initial_speed)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

    # Обновление сложности игры каждые 20 сек
    def update_difficulty(self):
        current_time = pygame.time.get_ticks()
        if (current_time - self.last_difficulty_increase_time) > 20000:
            self.difficulty += 1
            self.last_difficulty_increase_time = current_time

    # Отображение времени выживания в игре
    def render_time(self):
        font = pygame.font.Font(None, 36)
        time_elapsed = (pygame.time.get_ticks() - self.start_ticks) // 1000
        time_surface = font.render(f"Время: {time_elapsed} секунд", True, (255, 255, 255))
        self.screen.blit(time_surface, (10, 10))

        # Добавление отображения текущей сложности игры
        difficulty_surface = font.render(f"Сложность: {self.difficulty}", True, (255, 255, 255))
        self.screen.blit(difficulty_surface, (600, 10))


if __name__ == "__main__":
    game = Game()
    game.run()
