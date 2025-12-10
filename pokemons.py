import random
import pygame

NOT_STARTED = -1
STARTED = 0
HIT_DELAY = 200

class Battle:
    def __init__(self, n, x, y):
        self.n = n
        self.x = x
        self.y = y
        self.turn = 1
        self.state = NOT_STARTED

    def draw(self, surface):
        if self.state == NOT_STARTED:
            return
        for pokemon in self.team1 + self.team2:
            pokemon.draw()
        if len(self.team1) > 0 and len(self.team2) > 0:
            hit_circle = pygame.Surface((110, 110), pygame.SRCALPHA)
            pygame.draw.circle(hit_circle, (255, 0, 0, 100), hit_circle.get_rect().center,
                               hit_circle.get_rect().width // 2 - 5, 0)

            if self.turn == 1:
                surface.blit(hit_circle, (
                self.team2[0].x, self.team2[0].y))
            else:
                surface.blit(hit_circle, (
                self.team1[0].x, self.team1[0].y))

    def start(self, trainer1, trainer2):
        if self.state == NOT_STARTED:
            self.trainer1 = trainer1
            self.trainer2 = trainer2
            self.team1 = trainer1.best_team(self.n)
            self.team2 = trainer2.best_team(self.n)

            if len(self.team1) < self.n or len(self.team2) < self.n:
                return

            y = self.y
            for pokemon in self.team1:
                pokemon.x, pokemon.y = self.x, y
                y += 150
                pokemon.vx = pokemon.vy = 0

            y = self.y
            for pokemon in self.team2:
                pokemon.x, pokemon.y = self.x + 280, y
                y += 150
                pokemon.vx = pokemon.vy = 0
            self.state = STARTED
            self.last_update = pygame.time.get_ticks()

    def update(self):
        if self.state == STARTED:
            nowTime = pygame.time.get_ticks()
            if nowTime - self.last_update > HIT_DELAY:
                self.last_update = nowTime
            else:
                return
            if self.turn == 1 and len(self.team1) > 0 and len(self.team2) > 0:
                self.team1[0].attack(self.team2[0])
                if self.team2[0].hp <= 0:
                    self.team2.remove(self.team2[0])
                if len(self.team2) == 0:
                    return self.finish(1)
            elif self.turn == 2 and len(self.team1) > 0 and len(self.team2) > 0:
                self.team2[0].attack(self.team1[0])
                if self.team1[0].hp <= 0:
                    self.team1.remove(self.team1[0])
                if len(self.team1) == 0:
                    return self.finish(2)
            if self.turn == 1:
                self.turn = 2
            else:
                self.turn = 1

    def finish(self, result):
        self.state = NOT_STARTED
        for p in self.team1:
            self.trainer1.add(p)
        for p in self.team2:
            self.trainer2.add(p)
        if result == 1:
            self.trainer1.wins += 1
        else:
            self.trainer2.wins += 1

    def started(self):
        return True if self.state == STARTED else False
class World:
    MAX_POKEMON_ATK = 5
    MAX_POKEMON_DF = 5

    def __init__(self, n_pok, x1, y1, x2, y2, facade):
        self.facade = facade
        self.n_poc = n_pok
        self.rect = facade.create_rect(x1, y1, x2 - x1, y2 - y1)
        self.pokemons = []
        self.generate_pokemons()

    def generate_pokemons(self):
        for _ in range(self.n_poc):
            pokemon_type = random.randint(0, 3)
            if pokemon_type == 0:
                self.pokemons.append(ElectricPokemon("ep", random.randint(1, World.MAX_POKEMON_ATK), random.randint(1, World.MAX_POKEMON_DF), 30, 200, self.facade, im4))
            if pokemon_type == 1:
                self.pokemons.append(FirePokemon("fp", random.randint(1, World.MAX_POKEMON_ATK), random.randint(1, World.MAX_POKEMON_DF), 300, 100, self.facade, im2))
            if pokemon_type == 2:
                self.pokemons.append(WaterPokemon("wp", random.randint(1, World.MAX_POKEMON_ATK), random.randint(1, World.MAX_POKEMON_DF), 370, 154, self.facade, im1))
            if pokemon_type == 3:
                self.pokemons.append(GrassPokemon("gp", random.randint(1, World.MAX_POKEMON_ATK), random.randint(1, World.MAX_POKEMON_DF), 60, 430, self.facade, im3))

    def draw(self):
        for pokemon in self.pokemons:
            pokemon.draw()

    def update(self):
        for pokemon in self.pokemons:
            pokemon.update()

    def catch_pokemon(self, pos):
        for pokemon in self.pokemons:
            rect = pokemon.img.get_rect()
            if rect.left + pokemon.x <= pos[0] <= rect.right + pokemon.x and rect.top + pokemon.y <= pos[1] <= rect.bottom + pokemon.y:
                self.pokemons.remove(pokemon)
                return pokemon
        return None


SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 30
class PygameFacade:
    def __init__(self, screen_size):
        pygame.init()
        self.screen = pygame.display.set_mode(screen_size)
        self.clock = pygame.time.Clock()
        self.flag_player = True

    def draw_circle(self, x, y, color, radius):
        pygame.draw.circle(self.screen, color, (x, y), radius)

    def draw_rectangle(self, x, y, width, height, color):
        pygame.draw.rect(self.screen, color, pygame.Rect(x, y, width, height))

    def update_screen(self):
        pygame.display.flip()

    def clear_screen(self):
        self.screen.fill((0, 0, 0))

    def create_rect(self, x, y, width, height):
        return pygame.rect.Rect(x, y, width, height)

    def write_text(self, text, x, y):
        f = pygame.font.SysFont('arial', 36)
        t = f.render(text, True, "white")
        self.screen.blit(t, (x, y))

    def show_image(self, link, x, y):
        pygame_facade.screen.blit(link, (x, y))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                catched_pokemon = world.catch_pokemon(event.pos)
                if catched_pokemon:
                    if self.flag_player:
                        player.add(catched_pokemon)
                    else:
                        bot.add(catched_pokemon)

                    self.flag_player = not self.flag_player



pygame_facade = PygameFacade((SCREEN_WIDTH, SCREEN_HEIGHT))

im1 = pygame.image.load("водный покемон.webp").convert_alpha()
im1 = pygame.transform.scale(im1, (100, 100))
im2 = pygame.image.load("огненный покемон.webp").convert_alpha()
im2 = pygame.transform.scale(im2, (100, 100))
im3 = pygame.image.load("травяной покемон.webp").convert_alpha()
im3 = pygame.transform.scale(im3, (100, 100))
im4 = pygame.image.load("электрический покемон.webp").convert_alpha()
im4 = pygame.transform.scale(im4, (100, 100))

class Pokemon:
    """Родительский класс, который используется для описания покемона (Pokemon)"""

    def __init__(self, name: str, atk: int, df: int, x: int, y: int, facade, im) -> None:
        """Инициализация нового покемона
        Parametrs:

        name : str
            имя покемона
        hp : int
            здоровье покемона
        atk : int
            сила атаки покемона
        df : int
            уровень защиты покемона
        path : str
            путь к изображению покемона
        x : int
            координата X покемона
        y : int
            координата Y покемона
        """

        self._name = name
        self.hp = 10
        self.atk = atk
        self.df = df
        self.x = x
        self.y = y
        self.vx = random.choice([5, -5])
        self.vy = random.choice([5, -5])
        self.img = im

        pygame_facade.show_image(self.img, self.x, self.y)

    def __str__(self):
        return self._name

    @property
    def name(self) -> str:
        """Свойство имени"""
        return self._name

    @property
    def hp(self) -> int:
        """Свойство здоровья покемона"""
        return self.__hp

    @hp.setter
    def hp(self, hp: int) -> None:
        """Устанавливает неотрицательное значение здоровья покемона"""
        self.__hp = max(0, hp)

    @property
    def atk(self) -> int:
        """Свойство силы атаки покемона"""
        return self.__atk

    @atk.setter
    def atk(self, atk: int) -> None:
        """Устанавливает неотрицательное значение силы атаки покемона"""
        self.__atk = max(0, atk)

    @property
    def df(self) -> int:
        """Свойство уровня защиты покемона"""
        return self.__df

    @df.setter
    def df(self, df: int) -> None:
        """Устанавливает неотрицательное значение уровня защиты покемона"""
        self.__df = max(0, df)

    def attack(self, other: "Pokemon") -> None:
        """Атака другого покемона

        Передается параметр 'other', который содержит имя защищающегося покемона
        """
        if self.hp > 0 and other.hp > 0:
            damage = self.atk - other.df

            if damage >= 0:
                other.hp -= damage
            else:
                other.hp -= 1


    def update(self):
        """Обновление позиции покемона"""
        self.x += self.vx
        self.y += self.vy

        if self.x <= 0 or self.x + 50 >= SCREEN_WIDTH:
            self.vx *= -1
        if self.y <= 0 or self.y + 50 >= SCREEN_HEIGHT:
            self.vy *= -1

    def draw(self):
        """Отрисовка покемона на экране"""
        pygame_facade.show_image(self.img, self.x, self.y)
        stats_text = f"ATK:{self.atk} DF:{self.df}"
        pygame_facade.write_text(stats_text, self.x, self.y - 35)

class WaterPokemon(Pokemon):
    """Дочерний класс покемона (Pokemon), который описывает водного покемона"""

    def __init__(self, name: str, atk: int, df: int, x: int, y: int, facade, im1):
        super().__init__(name, atk, df, x, y, facade, im1)
    def attack(self, other: Pokemon) -> None:
        if isinstance(other, WaterPokemon):
            self.atk *= 3
            super().attack(other)
            self.atk //= 3

        else:
            super().attack(other)


class FirePokemon(Pokemon):
    """Дочерний класс покемона (Pokemon), который описывает огненного покемона"""

    def __init__(self, name: str, atk: int, df: int, x: int, y: int, facade, im2):
        super().__init__(name, atk, df, x, y, facade, im2)
    pass


class GrassPokemon(Pokemon):
    """Дочерний класс покемона (Pokemon), который описывает травяного покемона"""

    def __init__(self, name: str, atk: int, df: int, x: int, y: int, facade, im3):
        super().__init__(name, atk, df, x, y, facade, im3)
    def attack(self, other: Pokemon) -> None:
        if isinstance(other, GrassPokemon):
            old = other.df
            other.df //= 2
            super().attack(other)
            other.df = old
        else:
            super().attack(other)


class ElectricPokemon(Pokemon):
    """Дочерний класс покемона (Pokemon), который описывает электрического покемона"""

    def __init__(self, name: str, atk: int, df: int, x: int, y: int, facade, im4):
        super().__init__(name, atk, df, x, y, facade, im4)
    def attack(self, other: Pokemon) -> None:
        if isinstance(other, ElectricPokemon):
            old = other.df
            other.df = 0
            super().attack(other)
            other.df = old

        else:
            super().attack(other)


class Trainer:

    def __init__(self, x, y, facade):
       self.wins = 0
       self.box = []
       self.facade = facade
       self.x = x
       self.y = y

    def draw(self):
        self.facade.screen.blit(pygame.transform.scale(pygame.image.load("trainer.png"), (100, 100)), (self.x, self.y))


    def add(self, pokemon):
        self.box.append(pokemon)


class SmartTrainer(Trainer):
    def best_team(self, n: int) -> list:
        team = sorted(self.box, key = lambda i: i.atk + i.df, reverse = True)
        return team[:n]

running = True
world = World(10, 0,0, SCREEN_WIDTH, SCREEN_HEIGHT, pygame_facade)
player = SmartTrainer(0, 300, pygame_facade)
bot = SmartTrainer(SCREEN_WIDTH-100, 300, pygame_facade)
battle = Battle(5, 300, 0)

while running:
    pygame_facade.handle_events()
    pygame_facade.clear_screen()

    world.draw()
    world.update()
    player.draw()
    bot.draw()

    if not world.pokemons:
        battle.start(player, bot)
    battle.draw(pygame_facade.screen)
    battle.update()

    pygame_facade.update_screen()
    pygame_facade.clock.tick(FPS)
