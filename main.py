import pygame
from random import randint
import sounddevice as sd
import numpy as np
pygame.init()

YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)

window_size = 1200, 800
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("flappy bird voice")
clock = pygame.time.Clock()

fs = 16000
block = 256
mic_level = 0.0


class Bird():
    def __init__(self, x, y, w, h, color):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.y_vel = 0.0
        self.gravity = 0.6
        self.THRESH = 0.01
        self.IMPULSE = -8.0

    def show(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.w, self.h))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

class Pipes():
    def __init__(self, x, y, w, h, color):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color

    def show(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.w, self.h))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

def generate_pipes(count, pipe_width=140, gap=280, min_height=50, max_height=440, distance=650):
    pipes = []
    start_x = window_size[0]
    for i in range(count):
        height = randint(min_height, max_height)
        top_pipe = Pipes(start_x, 0, pipe_width, height, GREEN)
        bottom_pipe = Pipes(start_x, height + gap, pipe_width, window_size[1] - (height + gap), GREEN)
        pipes.extend([top_pipe, bottom_pipe])
        start_x += distance
    return pipes

def audio_callback(indata, frames, time, status):
    global mic_level
    if status:
        return
    rms = np.sqrt(np.mean(indata**2))
    mic_level = 0.85 * mic_level + 0.15 * rms

bird = Bird(100, 100, 50, 50, YELLOW)

pipes = generate_pipes(150)

wait = 40
lose = False
game = True

with sd.InputStream(callback=audio_callback, channels=1, samplerate=fs, blocksize=block):
    while game:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game = False

        screen.fill(CYAN)        
        bird.show(screen)
        bird_rect = bird.get_rect()

        if bird.y < 0 or bird.y + bird.h > window_size[1]:
            print("Game Over")
            game = False 

        if len(pipes) < 8:
            pipes += generate_pipes(150)
            if pipes.x <= -100:
                pipes.remove(pipe)

        for pipe in pipes[:]:
            pipe.x -= 10
            pipe.show(screen)

            if bird_rect.colliderect(pipe.get_rect()):
                print("Game Over")
                game = False

            if pipe.x + pipe.w < 0:
                pipes.remove(pipe)

        if lose and wait > 1:
            for pipe in pipes:
                pipe.x += 8
            wait -= 1
        else:
            lose = False
            wait = 40

        if mic_level > bird.THRESH:
            bird.y_vel = bird.IMPULSE
        bird.y_vel += bird.gravity
        bird.y += bird.y_vel

        pygame.display.flip()
        clock.tick(60)

pygame.quit()