import random
import pygame

NOT_STARTED = -1
STARTED = 0
HIT_DELAY = 200

COLORS = {
    'background': (20, 20, 40),
    'player_team': (100, 200, 255),
    'bot_team': (255, 100, 100),
    'text': (255, 255, 255),
    'health_bar_green': (50, 200, 50),
    'health_bar_red': (200, 50, 50),
    'attack_effect': (255, 255, 0),
    'special_effect': (200, 50, 200)
}


class Battle:
    def __init__(self, n, x, y):
        self.n = n
        self.x = x
        self.y = y
        self.turn = 1
        self.state = NOT_STARTED
        self.winner = None
        self.attack_effects = []  # Эффекты атак

    def draw(self, surface):
        if self.state == NOT_STARTED:
            if self.winner is not None:
                font_large = pygame.font.SysFont('arial', 72, bold=True)
                font_small = pygame.font.SysFont('arial', 36)

                if self.winner == 1:
                    text = font_large.render("PLAYER WINS!", True, COLORS['player_team'])
                    subtext = font_small.render("Your team was victorious!", True, COLORS['text'])
                else:
                    text = font_large.render("BOT WINS!", True, COLORS['bot_team'])
                    subtext = font_small.render("Better luck next time!", True, COLORS['text'])

                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
                subtext_rect = subtext.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))

                pygame.draw.rect(surface, (0, 0, 0, 180),
                                 (text_rect.x - 20, text_rect.y - 20,
                                  text_rect.width + 40, text_rect.height + subtext_rect.height + 40))

                surface.blit(text, text_rect)
                surface.blit(subtext, subtext_rect)
            return

        for effect in self.attack_effects[:]:
            pygame.draw.circle(surface, COLORS['attack_effect'],
                               (effect['x'], effect['y']), effect['radius'])
            effect['radius'] -= 1
            effect['alpha'] -= 10
            if effect['radius'] <= 0:
                self.attack_effects.remove(effect)


        for pokemon in self.team1 + self.team2:
            pokemon.draw()


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
            self.winner = None
            self.attack_effects = []
            self.critical_hits = []

    def update(self):
        if self.state == STARTED:
            nowTime = pygame.time.get_ticks()
            if nowTime - self.last_update > HIT_DELAY:
                self.last_update = nowTime
            else:
                return

            if self.turn == 1 and len(self.team1) > 0 and len(self.team2) > 0:
                # Шанс критического удара
                is_critical = random.random() < 0.2  # 20% шанс
                damage_multiplier = 2.0 if is_critical else 1.0

                old_hp = self.team2[0].hp
                self.team1[0].attack(self.team2[0])

                # Эффект атаки
                self.attack_effects.append({
                    'x': self.team2[0].x + 50,
                    'y': self.team2[0].y + 50,
                    'radius': 30,
                    'alpha': 255
                })

                # Эффект критического удара
                if is_critical:
                    self.critical_hits.append({
                        'x': self.team2[0].x,
                        'y': self.team2[0].y,
                        'timer': 0
                    })

                if self.team2[0].hp <= 0:
                    self.team2.remove(self.team2[0])
                if len(self.team2) == 0:
                    return self.finish(1)

            elif self.turn == 2 and len(self.team1) > 0 and len(self.team2) > 0:
                is_critical = random.random() < 0.2
                damage_multiplier = 2.0 if is_critical else 1.0

                old_hp = self.team1[0].hp
                self.team2[0].attack(self.team1[0])

                self.attack_effects.append({
                    'x': self.team1[0].x + 50,
                    'y': self.team1[0].y + 50,
                    'radius': 30,
                    'alpha': 255
                })


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
        self.winner = result

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
        self.background_offset = 0

    def generate_pokemons(self):
        for _ in range(self.n_poc):
            pokemon_type = random.randint(0, 3)
            x = random.randint(50, SCREEN_WIDTH - 150)
            y = random.randint(50, SCREEN_HEIGHT - 150)
            if pokemon_type == 0:
                self.pokemons.append(ElectricPokemon("Electro", random.randint(1, World.MAX_POKEMON_ATK),
                                                     random.randint(1, World.MAX_POKEMON_DF), x, y, self.facade))
            if pokemon_type == 1:
                self.pokemons.append(FirePokemon("Blaze", random.randint(1, World.MAX_POKEMON_ATK),
                                                 random.randint(1, World.MAX_POKEMON_DF), x, y, self.facade))
            if pokemon_type == 2:
                self.pokemons.append(WaterPokemon("Aqua", random.randint(1, World.MAX_POKEMON_ATK),
                                                  random.randint(1, World.MAX_POKEMON_DF), x, y, self.facade))
            if pokemon_type == 3:
                self.pokemons.append(GrassPokemon("Leaf", random.randint(1, World.MAX_POKEMON_ATK),
                                                  random.randint(1, World.MAX_POKEMON_DF), x, y, self.facade))

    def draw(self):


        for pokemon in self.pokemons:
            pokemon.draw()

    def update(self):
        self.background_offset = (self.background_offset + 1) % 40
        for pokemon in self.pokemons:
            pokemon.update()

    def catch_pokemon(self, pos):
        for pokemon in self.pokemons:
            pokemon_rect = pygame.Rect(pokemon.x, pokemon.y, 100, 100)
            if pokemon_rect.collidepoint(pos):
                self.pokemons.remove(pokemon)
                # Эффект при ловле покемона
                for i in range(10):
                    self.facade.particle_effects.append({
                        'x': pokemon.x + 50,
                        'y': pokemon.y + 50,
                        'vx': random.uniform(-5, 5),
                        'vy': random.uniform(-5, 5),
                        'color': COLORS['special_effect'],
                        'life': 30
                    })
                return pokemon
        return None


SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60  # Увеличили FPS для плавности


class PygameFacade:
    def __init__(self, screen_size):
        pygame.init()
        self.screen = pygame.display.set_mode(screen_size)
        self.clock = pygame.time.Clock()
        self.flag_player = True
        self.particle_effects = []  # Система частиц
        self.selection_glow = 0

    def draw_circle(self, x, y, color, radius):
        pygame.draw.circle(self.screen, color, (x, y), radius)

    def draw_rectangle(self, x, y, width, height, color):
        pygame.draw.rect(self.screen, color, pygame.Rect(x, y, width, height))

    def update_screen(self):
        pygame.display.flip()

    def clear_screen(self):
        self.screen.fill(COLORS['background'])

    def create_rect(self, x, y, width, height):
        return pygame.rect.Rect(x, y, width, height)

    def write_text(self, text, x, y, color=COLORS['text'], font_size=24):
        font = pygame.font.SysFont('arial', font_size)
        t = font.render(text, True, color)
        self.screen.blit(t, (x, y))

    def show_image(self, link, x, y):
        try:
            im = pygame.image.load(link).convert_alpha()
            im = pygame.transform.scale(im, (100, 100))
            self.screen.blit(im, (x, y))
        except:
            # Запасное изображение
            pygame.draw.rect(self.screen, (100, 100, 100), (x, y, 100, 100))
            self.write_text("Pokemon", x + 10, y + 40, (255, 255, 255), 16)

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

    def update_particles(self):
        for particle in self.particle_effects[:]:
            pygame.draw.circle(self.screen, particle['color'],
                               (int(particle['x']), int(particle['y'])), 3)
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particle_effects.remove(particle)


pygame_facade = PygameFacade((SCREEN_WIDTH, SCREEN_HEIGHT))


class Pokemon:
    def __init__(self, name: str, atk: int, df: int, x: int, y: int, facade) -> None:
        self._name = name
        self.max_hp = 100
        self.hp = self.max_hp
        self.atk = atk
        self.df = df
        self.x = x
        self.y = y
        self.vx = random.choice([3, -3, 4, -4, 2, -2])
        self.vy = random.choice([3, -3, 4, -4, 2, -2])
        self.link = "огненный покемон.webp"
        try:
            self.image = pygame.image.load(self.link)
        except:
            self.image = None
        self.rect = pygame.rect.Rect(x, y, 100, 100)

    def __str__(self):
        return self._name

    @property
    def name(self) -> str:
        return self._name

    @property
    def hp(self) -> int:
        return self.__hp

    @hp.setter
    def hp(self, hp: int) -> None:
        self.__hp = max(0, min(hp, self.max_hp))

    @property
    def atk(self) -> int:
        return self.__atk

    @atk.setter
    def atk(self, atk: int) -> None:
        self.__atk = max(1, atk)

    @property
    def df(self) -> int:
        return self.__df

    @df.setter
    def df(self, df: int) -> None:
        self.__df = max(1, df)

    def attack(self, other: "Pokemon") -> None:
        if self.hp > 0 and other.hp > 0:
            damage = max(1, self.atk - other.df)
            other.hp -= damage

    def update(self):
        self.x += self.vx
        self.y += self.vy

        if self.x <= 0 or self.x + 100 >= SCREEN_WIDTH:
            self.vx *= -1
        if self.y <= 0 or self.y + 100 >= SCREEN_HEIGHT:
            self.vy *= -1

    def draw(self):
        # Убраны кружочки вокруг покемонов
        pygame_facade.show_image(self.link, self.x, self.y)

        # Улучшенная полоска здоровья
        health_width = 80
        health_height = 8
        health_x = self.x + 10
        health_y = self.y - 20

        # Фон полоски здоровья
        pygame.draw.rect(pygame_facade.screen, COLORS['health_bar_red'],
                         (health_x, health_y, health_width, health_height))

        # Текущее здоровье
        health_ratio = self.hp / self.max_hp
        pygame.draw.rect(pygame_facade.screen, COLORS['health_bar_green'],
                         (health_x, health_y, health_width * health_ratio, health_height))

        # Статистика
        font = pygame.font.SysFont('arial', 14, bold=True)
        stats_text = f"ATK:{self.atk} DF:{self.df}"
        text_surface = font.render(stats_text, True, COLORS['text'])
        pygame_facade.screen.blit(text_surface, (self.x + 5, self.y - 35))

        # Имя покемона
        name_text = font.render(self.name, True, COLORS['text'])
        pygame_facade.screen.blit(name_text, (self.x + 5, self.y - 50))


class WaterPokemon(Pokemon):
    def __init__(self, name: str, atk: int, df: int, x: int, y: int, facade):
        super().__init__(name, atk, df, x, y, facade)
        self.link = "водный покемон.webp"
        self.max_hp = 120  # У водных больше HP

    def attack(self, other: Pokemon) -> None:
        if isinstance(other, FirePokemon):
            self.atk *= 2  # Урон против огненных
        super().attack(other)


class FirePokemon(Pokemon):
    def __init__(self, name: str, atk: int, df: int, x: int, y: int, facade):
        super().__init__(name, atk, df, x, y, facade)
        self.link = "огненный покемон.webp"
        self.atk += 2  # Огненные имеют повышенную атаку

    def attack(self, other: Pokemon) -> None:
        if isinstance(other, GrassPokemon):
            self.atk *= 2  # Урон против травяных
        super().attack(other)


class GrassPokemon(Pokemon):
    def __init__(self, name: str, atk: int, df: int, x: int, y: int, facade):
        super().__init__(name, atk, df, x, y, facade)
        self.link = "травяной покемон.webp"
        self.df += 2  # Травяные имеют повышенную защиту

    def attack(self, other: Pokemon) -> None:
        if isinstance(other, WaterPokemon):
            self.atk *= 2  # Урон против водных
        super().attack(other)


class ElectricPokemon(Pokemon):
    def __init__(self, name: str, atk: int, df: int, x: int, y: int, facade):
        super().__init__(name, atk, df, x, y, facade)
        self.link = "электрический покемон.webp"
        # Электрические имеют шанс оглушить

    def attack(self, other: Pokemon) -> None:
        if random.random() < 0.3:  # 30% шанс оглушения
            other.df = max(1, other.df - 1)
        super().attack(other)


class Trainer:
    def __init__(self, x, y, facade, name="Trainer"):
        self.wins = 0
        self.box = []
        self.facade = facade
        self.x = x
        self.y = y
        self.name = name

    def draw(self):
        self.facade.screen.blit(pygame.transform.scale(pygame.image.load("trainer.png"), (100, 100)), (self.x, self.y))

        # Информация о тренере
        font = pygame.font.SysFont('arial', 18, bold=True)
        name_text = font.render(self.name, True, COLORS['text'])
        count_text = font.render(f"Pokémons: {len(self.box)}", True, COLORS['text'])
        wins_text = font.render(f"Wins: {self.wins}", True, COLORS['text'])

        self.facade.screen.blit(name_text, (self.x, self.y - 60))
        self.facade.screen.blit(count_text, (self.x, self.y - 85))
        self.facade.screen.blit(wins_text, (self.x, self.y - 110))

    def add(self, pokemon):
        if len(self.box) < 6:  # Максимум 6 покемонов
            self.box.append(pokemon)
            return True
        return False


class SmartTrainer(Trainer):
    def best_team(self, n: int) -> list:
        team = sorted(self.box, key=lambda i: i.atk + i.df, reverse=True)
        return team[:n]


running = True
world = World(12, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, pygame_facade)
player = SmartTrainer(50, 300, pygame_facade, "Player")
bot = SmartTrainer(SCREEN_WIDTH - 150, 300, pygame_facade, "Bot")
battle = Battle(5, 300, 100)

while running:
    pygame_facade.handle_events()
    pygame_facade.clear_screen()

    # Обновление и отрисовка частиц
    pygame_facade.update_particles()

    world.draw()
    world.update()
    player.draw()
    bot.draw()

    # Отображение текущего хода
    turn_color = COLORS['player_team'] if pygame_facade.flag_player else COLORS['bot_team']
    turn_text = "Player's Turn" if pygame_facade.flag_player else "Bot's Turn"
    pygame_facade.write_text(turn_text, SCREEN_WIDTH // 2 - 100, 20, turn_color, 32)

    # Отображение оставшихся покемонов
    pygame_facade.write_text(f"Pokémons left: {len(world.pokemons)}", 10, 10, COLORS['text'], 24)

    if not world.pokemons and len(player.box) >= 5 and len(bot.box) >= 5:
        battle.start(player, bot)

    battle.draw(pygame_facade.screen)
    battle.update()

    pygame_facade.update_screen()
    pygame_facade.clock.tick(FPS)