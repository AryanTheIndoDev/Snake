import pygame as pg
import json
from random import randint
from os.path import join

pg.init()

Width: int = 525
Height: int = 525
bg_color: str = "#000000"
block_size: int = 25
lost: bool = False
moves_per_sec = 6
score = 0

with open("game_data.json", "r") as file:
    data = json.load(file)

highscore = data["high_score"]

screen = pg.display.set_mode((Width, Height))
pg.display.set_caption("Snake")
clock = pg.time.Clock()

eat_sound = pg.Sound(join("assets", "eat.mp3"))
eat1_sound = pg.Sound(join("assets", "eat-.mp3"))
lose_sound = pg.Sound(join("assets", "lose.mp3"))
move1_sound = pg.Sound(join("assets", "move1.mp3"))
move2_sound = pg.Sound(join("assets", "move2.mp3"))
move3_sound = pg.Sound(join("assets", "move3.mp3"))
move4_sound = pg.Sound(join("assets", "move4.mp3"))

font = pg.font.SysFont("Iceland", 60)
font_color = "Green"

gameover_surf = pg.surface.Surface((Width, Height))

dialog_box = pg.surface.Surface((Width, Height))
dialog_box.fill("Black")
dialog_box_rect = dialog_box.get_rect()
dialog_box_rect.topleft = (0, 0)

retry_button = pg.surface.Surface((Width, 75))
retry_button.fill("gray1")
retry_button_rect = retry_button.get_rect()
retry_button_rect.topleft = (0, 450)

class Player(pg.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.growth: bool = False
        self.headx: int = x
        self.heady: int = y
        self.head_direction: int = 4
        self.beginning_length: int = 3
        self.changing_direction: bool = False
        self.body: list[list] = []
        for i in range(self.beginning_length):
            self.body.append([x - i * block_size, y])
            
    def draw(self):
        for y in self.body:
            if self.body.index(y) == 0:
                pg.draw.rect(screen, "Green", (y[0], y[1], block_size, block_size))
                pg.draw.rect(screen, "Black", (y[0] + 8, y[1] + 8, block_size - 16, block_size - 16))
            elif self.body.index(y) == len(self.body) - 1:
                pg.draw.rect(screen, "#008141", (y[0] + 1, y[1] + 1, block_size - 2, block_size - 2))
            else:
                pg.draw.rect(screen, "Green", (y[0] + 1, y[1] + 1, block_size - 2, block_size - 2))

    def update(self):
        self.changing_direction = False
        if not self.growth:
            self.body.pop(-1)
        else:
            self.growth: bool = False

        x = self.body[0][0]
        y = self.body[0][1]

        if self.head_direction == 1:
            y -= block_size
        if self.head_direction == 2:
            x -= block_size
        if self.head_direction == 3:
            y += block_size
        if self.head_direction == 4:
            x += block_size
        
        if [x, y] in self.body:
            global lost
            lost = True
        elif 0 <= x <= 500 and 0 <= y <= 500:
            self.body.insert(0, [x, y])
        else:
            lost = True
        global highscore
        if lost == True:
            lose_sound.play()
            if score > int(highscore):
                save_file = {"high_score": str(score)}
                highscore = score
                with open("game_data.json", "w") as f:
                    json.dump(save_file, f)

class Food(pg.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.starting_pos = (x,y)
        self.pos = (x, y)

    def draw(self):
        pg.draw.rect(screen, "Red", (self.pos[0] + 5, self.pos[1] + 5, block_size - 10, block_size - 10))
    
    def update(self):
        if list(self.pos) == snake.body[0]:
            global score
            score += 1
            snake.growth = True
            eat = randint(0, 1)
            if eat == 0:
                eat_sound.play()
            else:
                eat1_sound.play()
            while True:
                pos = (randint(0, 20) * block_size, randint(0, 20) * block_size)
                if list(pos) not in snake.body:
                    self.pos = pos
                    break
                else:
                    continue

def drawgrid():

    for x in range(0, Width, block_size):
        for y in range(0, Height, block_size):
            block = pg.Rect(x, y, block_size, block_size)
            pg.draw.rect(screen, "#1F1F1F", block, 1)

def gameover():
    global font_color
    global score
    screen.fill("black")

    mouse_pos = pg.mouse.get_pos()
    lmb_clicked = pg.mouse.get_just_pressed()[0]

    if score != 1:
        score_text = font.render(f"You ate {score} tomatoes", False, "Green")
    else:
            score_text = font.render(f"You ate {score} tomato", False, "Green")   
    score_text_rect = score_text.get_rect()
    highscore_text = font.render(f"High Score: {highscore}", False, "Green")
    highscore_text_rect = highscore_text.get_rect()
    retry_text = font.render("Retry", False, font_color)
    retry_text_rect = retry_text.get_rect()

    score_text_rect.center = (263, 175)
    highscore_text_rect.center = (263, 263)
    retry_text_rect.center = (263, 488)

    if retry_button_rect.collidepoint(mouse_pos):
        retry_button.fill("Green")
        font_color = "gray1"
        if lmb_clicked:
            global lost
            lost = False
            score = 0
            snake.body = []
            for i in range(snake.beginning_length):
                snake.body.append([snake.headx - i * block_size, snake.heady])
            tomato.pos = tomato.starting_pos
            snake.head_direction = 4
    else:
        retry_button.fill("gray1")
        font_color = "Green"

    gameover_surf.blit(dialog_box, dialog_box_rect)
    gameover_surf.blit(score_text, score_text_rect)
    gameover_surf.blit(highscore_text, highscore_text_rect)
    gameover_surf.blit(retry_button, retry_button_rect)
    gameover_surf.blit(retry_text, retry_text_rect)

    screen.blit(gameover_surf)

def game():

    running = True
    tick: int = 0
    while running:
        if not lost:
            tick += 1
            for event in pg.event.get():
                global moves_per_sec
                if event.type == pg.QUIT:
                    running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_w or event.key == pg.K_UP:
                        if snake.head_direction not in [3, 1] and snake.changing_direction == False:
                            snake.changing_direction = True
                            snake.head_direction = 1
                            move1_sound.play()

                    if event.key == pg.K_a or event.key == pg.K_LEFT:
                        if snake.head_direction not in [4, 2] and snake.changing_direction == False:
                            snake.changing_direction = True
                            snake.head_direction = 2
                            move2_sound.play()

                    if event.key == pg.K_s or event.key == pg.K_DOWN:
                        if snake.head_direction not in [1, 3] and snake.changing_direction == False:
                            snake.changing_direction = True
                            snake.head_direction = 3
                            move3_sound.play()

                    if event.key == pg.K_d or event.key == pg.K_RIGHT:
                        if snake.head_direction not in [2, 4] and snake.changing_direction == False:
                            snake.changing_direction = True
                            snake.head_direction = 4
                            move4_sound.play()

            screen.fill("Black")
            key = pg.key.get_pressed()
            if key[pg.K_SPACE]:
                moves_per_sec = 15
            else:
                moves_per_sec = 6
            drawgrid()
            snake.draw()
            tomato.draw()
            if tick >= 60 / moves_per_sec:
                snake.update()
                tomato.update()
                tick = 0
        else:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
            gameover()

        pg.display.flip()
        clock.tick(60)

snake = Player(200, 250)
tomato = Food(400, 250)

game()
pg.quit()