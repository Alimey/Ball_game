import math
from random import randint
from random import choice

import pygame


FPS = 30

RED = 0xFF0000
BLACK = (0, 0, 0)
GREY = 0x7D7D7D

g = 2

WIDTH = 1600
HEIGHT = 800
FLOOR = 550


class Ball:
    def __init__(self, screen: pygame.Surface, x=40, y=FLOOR-50):
        """ Конструктор класса ball

        Args:
        x - начальное положение мяча по горизонтали
        y - начальное положение мяча по вертикали
        """
        self.screen = screen
        self.x = x
        self.y = y
        self.r = 10
        self.vx = 0
        self.vy = 0
        self.color = GREY
        self.live = 30
        self.__Wall = ''

    def __where_is_ball(self):
        """ Столкновение шара со стенкой

        Проверяет, сталкивается ли шар со стенкой. Если да - меняет
        значение атрибута __Wall в соответствие с конкретной стенкой
        """
        
        up_border = self.y - self.r 
        down_border = self.y + self.r 
        left_border = self.x - self.r 
        right_border = self.x + self.r 

        if up_border <= 0:
            self.__Wall = 'u'
        if down_border >= FLOOR:
            self.__Wall = 'd'
        if left_border <= 0:
            self.__Wall = 'l'
        if right_border >= WIDTH:
            self.__Wall = 'r'

    def speed(self):
        """Изменение скорости шара за кадр

        Изменяет скорость шара в соответствие с сопротивлением среды и ускорением свободного падения
        """
        resist_wind = 0.05
        a_x = -self.vx*resist_wind
        a_y = -self.vy*resist_wind + g

        self.vx += a_x
        self.vy += a_y

    def is_stopped(self):
        """Остановка шара

        Проверяет, остановился ли шар по значению его полной скорости и его координатам
        Возвращает True или False
        """
        v_kv = self.vx**2 + self.vy**2

        if (v_kv <= 81) and (self.y >= FLOOR - self.r):
            return True
        else:
            return False

    def make_stop(self):
        """Заставить шар остановиться

        Обнуляет скорость остановившегося шара
        """
        if self.is_stopped():
            self.vx = 0
            self.vy = 0
            self.y = FLOOR - self.r

    def move(self):
        """Переместить мяч по прошествии единицы времени.

        Метод описывает перемещение мяча за один кадр перерисовки. То есть, обновляет значения
        self.x и self.y с учетом скоростей self.vx и self.vy, силы гравитации, действующей на мяч,
        и стен по краям окна (размер окна 800х600).
        """
        self.__where_is_ball()
        resist_wall = 1

        if (self.__Wall == 'u'):
            self.vy = -self.vy - resist_wall
            self.y = self.r 
        if (self.__Wall == 'd'):
            self.vy = -self.vy + resist_wall
            self.y = FLOOR - self.r 
        if (self.__Wall == 'r'):
            self.vx = -self.vx + resist_wall
            self.x = WIDTH - self.r 
        if (self.__Wall == 'l'):
            self.vx = -self.vx - resist_wall
            self.x = self.r 
        
        self.x += self.vx
        self.y += self.vy + g/2
        self.speed()
        self.__Wall = ''
            
            

    def draw(self):
        pygame.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r
        )
        pygame.draw.circle(
            self.screen,
            'black',
            (self.x, self.y),
            self.r,
            width = 2
        )

    def hittest(self, obj):
        """Функция проверяет сталкивалкивается ли данный обьект с целью, описываемой в обьекте obj.

        Args:
            obj: Обьект, с которым проверяется столкновение.
        Returns:
            Возвращает True в случае столкновения мяча и цели. В противном случае возвращает False.
        """
        l_kv = (obj.x-self.x)**2 + (obj.y-self.y)**2
        if l_kv <= (self.r + obj.r)**2:
            return True
        else:
            return False



class Gun:
    def __init__(self, screen):
        self.screen = screen
        self.f2_power = 30
        self.f2_on = 0
        self.an = 1
        self.color = GREY
        self.parameters = [16, 49]

    def fire2_start(self, event):
        self.f2_on = 1

    def fire2_end(self, event):
        """Выстрел мячом.

        Происходит при отпускании кнопки мыши.
        Начальные значения компонент скорости мяча vx и vy зависят от положения мыши.
        """
        global balls, bullet
        bullet += 1
        new_ball = Ball(self.screen)
        if event.pos[0]-new_ball.x == 0:
            self.an = math.pi/2
        else:
            self.an = math.atan((-event.pos[1]+new_ball.y)/(event.pos[0]-new_ball.x))
            
        new_ball.vx = self.f2_power * math.cos(self.an)
        new_ball.vy = -self.f2_power * math.sin(self.an)
        balls.append(new_ball)
        self.f2_on = 0
        self.f2_power = 30

    def targetting(self, event):
        """Прицеливание. Зависит от положения мыши."""
        if event:
            if event.pos[0]-35 == 0:
                self.an = math.pi/2
            else:
                self.an = math.atan((-event.pos[1]+FLOOR) / (event.pos[0]-35))
        if self.f2_on:
            self.color = RED
        else:
            self.color = GREY

    def control_parameters(self):
        """Контроль размеров пушки"""
        if (self.parameters[1] < 100) and self.f2_on:
            self.parameters[1] += 0.5
        elif not self.f2_on:
            self.parameters[1] = 49
        
    def power_up(self):
        self.control_parameters()
        if self.f2_on:
            if self.f2_power < 100:
                self.f2_power += 1
            self.color = RED
        else:
            self.color = GREY

    def draw(self):
        a = self.parameters[1]
        b = self.parameters[0]
        x0 = 35
        y0 = FLOOR
        r = 10
        pygame.draw.polygon(
            self.screen,
            self.color,
            [(x0, y0),
             (x0-b*math.sin(self.an),y0-b*math.cos(self.an)),
             (x0-b*math.sin(self.an)+a*math.cos(self.an),y0-a*math.sin(self.an)-b*math.cos(self.an)),
             (x0+a*math.cos(self.an),y0-a*math.sin(self.an))
             ]
            )
        pygame.draw.polygon(
            self.screen,
            BLACK,
            [(x0, y0),
             (x0-b*math.sin(self.an),y0-b*math.cos(self.an)),
             (x0-b*math.sin(self.an)+a*math.cos(self.an),y0-a*math.sin(self.an)-b*math.cos(self.an)),
             (x0+a*math.cos(self.an),y0-a*math.sin(self.an))
             ],
             2
            )
        pygame.draw.circle(
            self.screen,
            BLACK,
            (x0, y0),
            r,
            2
            )
        pygame.draw.circle(
            self.screen,
            BLACK,
            (x0, y0),
            4,
            )


class Target:
    def __init__(self, screen: pygame.Surface):
        self.points = 0
        self.screen = screen
        self.new_target()
        self.v = 5
        self.an = 0
        self.R = 30

    def new_target(self):
        """ Инициализация новой цели. """
        r = self.r = randint(10, 30)
        x = self.x = randint(600, WIDTH - 100 - r)
        y = self.y = randint(r + 100, FLOOR - r)
        self.live = 1
        self.thrown_bullets = 0
        color = self.color = RED
        self.destroyed = False

    def congratulations(self):
        """ Выводит число потраченных выстрелов после попадания в цель """
        f = pygame.font.Font(None, 36)
        figure = f.render(
            'Вы уничтожили цель за ' +
            str(self.thrown_bullets) +
            ' выстрелов', True, 'black'
            )
        screen.blit(figure, [WIDTH/3, HEIGHT/3])

    def hit(self, points=1):
        """Попадание шарика в цель."""
        self.points += points

    def draw(self):
        pygame.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r
        )
        pygame.draw.circle(
            self.screen,
            'black',
            (self.x, self.y),
            self.r,
            width = 2
        )

    def destroy(self):
        """ Уничтожить цель после попадания """
        pygame.draw.circle(
            self.screen,
            'white',
            (self.x, self.y),
            self.r
        )
        self.destroyed = True

    def control_an(self):
        """ Контролировать изменение направления движения """
        self.an += self.v/self.R

    def move(self):
        """Перемещение цели.

        Метод описывает перемещение цели за 1 кадр.
        """
        self.x += self.v*math.cos(self.an)
        self.y += -self.v*math.sin(self.an)

        self.control_an()
        

class Background:
    def make_background(screen):
        LIGHT_BLUE = pygame.Color('#ACF8FF')
        GREEN = pygame.Color('#129a33')

        screen.fill(LIGHT_BLUE)
        pygame.draw.polygon(
            screen,
            GREEN,
            [(0, FLOOR), (WIDTH, FLOOR), (WIDTH, HEIGHT), (0, HEIGHT)]
            )
        

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
bullet = 0
balls = []

clock = pygame.time.Clock()
gun = Gun(screen)
target = Target(screen)
finished = False
time_restart = 0
waiting_for_target = 0

while not finished:
    Background.make_background(screen)
    gun.draw()

    moment = pygame.time.get_ticks()
    if moment <= time_restart:
        target.congratulations()
        waiting_for_target = 1
    elif waiting_for_target == 1:
        target.new_target()
        waiting_for_target = 0

    if not target.destroyed:
        target.draw()

    f = pygame.font.Font(None, 48)
    figure = f.render(str(target.points), True, 'black')
    screen.blit(figure, [20, 20])
    
    for b in balls:
        b.draw()
    pygame.display.update()

    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            gun.fire2_start(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            gun.fire2_end(event)
            target.thrown_bullets += 1
        elif event.type == pygame.MOUSEMOTION:
            gun.targetting(event)

    for b in balls:
        if b.hittest(target) and target.live:
            target.live = 0
            target.hit()
            
            time_hit = pygame.time.get_ticks()
            time_restart = time_hit + 2000

            target.destroy()
        if b.is_stopped():
            b.make_stop()
        else:
            b.move()
    target.move()
    gun.power_up()

pygame.quit()
