import random #Создаем разные по длине трубы
import sys
import pygame
from pygame.locals import *


window_width = 600
window_height = 499


#Здесь делается размер окна
window = pygame.display.set_mode((window_width, window_height))   
elevation = window_height * 0.8
game_images = {}
framepersecond = 32

#Здесь прописываются переменные для картинок
pipeimage = 'images\\pipe.png'
background_image = 'images\\background.jpg'
birdplayer_image = 'images\\bird.png'
sealevel_image = 'images\\base.jfif'

# Функция в котором создаются трубы, устанавливает рандомный размер
def createPipe():
    offset = window_height/3
    pipeHeight = game_images['pipeimage'][0].get_height()
      
    # Генерируем рандомные размеры труб
    y2 = offset + random.randrange(
      0, int(window_height - game_images['sea_level'].get_height() - 1.2 * offset))  
    pipeX = window_width + 10
    y1 = pipeHeight - y2 + offset
    pipe = [
        
        # Верхняя турба
        {'x': pipeX, 'y': -y1},
        
          # Нижняя труба
        {'x': pipeX, 'y': y2}  
    ]
    return pipe

# Ставим условия конца игры
def isGameOver(horizontal, vertical, up_pipes, down_pipes):
    # Птичка ушла в воду
    if vertical > elevation - 25 or vertical < 0: 
        return True
  
    # Птичка задела верхнюю трубу
    for pipe in up_pipes:    
        pipeHeight = game_images['pipeimage'][0].get_height()
        if(vertical < pipeHeight + pipe['y'] 
           and abs(horizontal - pipe['x']) < game_images['pipeimage'][0].get_width()):
            return True

    # Птичка задела нижнюю трубу
    for pipe in down_pipes:
        if (vertical + game_images['flappybird'].get_height() > pipe['y'])  and abs(horizontal - pipe['x']) < game_images['pipeimage'][0].get_width():
            return True
    # Условия не тригнули? Продолжаем игру
    return False


# Здесь прописывается механики и создаются трубы
def flappygame():
    your_score = 0
    horizontal = int(window_width/5)
    vertical = int(window_width/2)
    ground = 0
    mytempheight = 100
  
    # Генерация труб на экране
    first_pipe = createPipe()
    second_pipe = createPipe()
  
    # Список содержит нижние трубы
    down_pipes = [
        {'x': window_width+300-mytempheight,
         'y': first_pipe[1]['y']},
        {'x': window_width+300-mytempheight+(window_width/2),
         'y': second_pipe[1]['y']},
    ]
  
    # Список верхних труб
    up_pipes = [
        {'x': window_width+300-mytempheight,
         'y': first_pipe[0]['y']},
        {'x': window_width+200-mytempheight+(window_width/2),
         'y': second_pipe[0]['y']},
    ]
  
    pipeVelX = -4 #pipe velocity along x
  
    bird_velocity_y = -9  # Скорость птицы
    bird_Max_Vel_Y = 10   
    bird_Min_Vel_Y = -8
    birdAccY = 1
      
     # Скорость после взмаха(пробела)
    bird_flap_velocity = -8
      
    # It is true only when the bird is flapping
    bird_flapped = False  
    while True:
         
        # Создаём событие после нажатия пробела (плюс событие закрытие игры)
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if vertical > 0:
                    bird_velocity_y = bird_flap_velocity
                    bird_flapped = True
  
        # Проверяем что птица, возможно, погибла в функции game_over
        game_over = isGameOver(horizontal, vertical, up_pipes, down_pipes)
        if game_over:
            print(f"Your your_score is {your_score}")
            return
  
        # Записываем очки
        playerMidPos = horizontal + game_images['flappybird'].get_width()/2
        for pipe in up_pipes:
            pipeMidPos = pipe['x'] + game_images['pipeimage'][0].get_width()/2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                your_score += 1
  
        if bird_velocity_y < bird_Max_Vel_Y and not bird_flapped:
            bird_velocity_y += birdAccY
  
        if bird_flapped:
            bird_flapped = False
        playerHeight = game_images['flappybird'].get_height()
        vertical = vertical + min(bird_velocity_y, elevation - vertical - playerHeight)
  
        # Передвигаем трубы влево
        for upperPipe, lowerPipe in zip(up_pipes, down_pipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX
  
        # Добавляем новую трубы как только она задевает левую часть экрана
        if 0 < up_pipes[0]['x'] < 5:
            newpipe = createPipe()
            up_pipes.append(newpipe[0])
            down_pipes.append(newpipe[1])
  
        # Если труба за пределом экрана, удаляем
        if up_pipes[0]['x'] < -game_images['pipeimage'][0].get_width():
            up_pipes.pop(0)
            down_pipes.pop(0)
  
        # Добавим картинки в саму игру используя blit
        window.blit(game_images['background'], (0, 0))
        for upperPipe, lowerPipe in zip(up_pipes, down_pipes):
            window.blit(game_images['pipeimage'][0],
                        (upperPipe['x'], upperPipe['y']))
            window.blit(game_images['pipeimage'][1],
                        (lowerPipe['x'], lowerPipe['y']))
  
        window.blit(game_images['sea_level'], (ground, elevation))
        window.blit(game_images['flappybird'], (horizontal, vertical))
          
        # Получаем очки.
        numbers = [int(x) for x in list(str(your_score))]
        width = 0
          
        # Указываем ширину цифры(картинки) в зависимости от окна
        for num in numbers:
            width += game_images['scoreimages'][num].get_width()
        Xoffset = (window_width - width)/1.1
          
        # Отрисовываем цифры
        for num in numbers:
            window.blit(game_images['scoreimages'][num], (Xoffset, window_width*0.02))
            Xoffset += game_images['scoreimages'][num].get_width()
              
        # Обнавляем игру
        pygame.display.update()
        framepersecond_clock.tick(framepersecond)



# Запускам игру
if __name__ == "__main__":          
      
    # Запуск модулей pygames
    pygame.init()  
    framepersecond_clock = pygame.time.Clock()
      
    # Здесь пишем название игры в окне
    pygame.display.set_caption('Flappy Bird Game')      
  
    # Устанавливаем картинки для игры
    # Картинки для отображения очков
    game_images['scoreimages'] = (
        pygame.image.load('images\\0.png').convert_alpha(),
        pygame.image.load('images\\1.png').convert_alpha(),
        pygame.image.load('images\\2.png').convert_alpha(),
        pygame.image.load('images\\3.png').convert_alpha(),
        pygame.image.load('images\\4.png').convert_alpha(),
        pygame.image.load('images\\5.png').convert_alpha(),
        pygame.image.load('images\\6.png').convert_alpha(),
        pygame.image.load('images\\7.png').convert_alpha(),
        pygame.image.load('images\\8.png').convert_alpha(),
        pygame.image.load('images\\9.png').convert_alpha()
    )
    # Остальные картинки
    game_images['flappybird'] = pygame.image.load(birdplayer_image).convert_alpha()                  
    game_images['sea_level'] = pygame.image.load(sealevel_image).convert_alpha()
    game_images['background'] = pygame.image.load(background_image).convert_alpha()
    game_images['pipeimage'] = (pygame.transform.rotate(pygame.image.load(pipeimage)
                                                        .convert_alpha(),
                                                        180),
                                pygame.image.load(pipeimage).convert_alpha())
  
    print("WELCOME TO THE FLAPPY BIRD GAME")
    print("Press space or enter to start the game")
    
   #Здесь главое меню
    while True:
  
        # Ставим на позицию птичку
        horizontal = int(window_width/5)
        vertical = int((window_height - game_images['flappybird'].get_height())/2)

        # Выравнивание моря
        ground = 0

        while True:
            for event in pygame.event.get():
                
                # Ставим условие под действие игрока
                # Если пользователь нажимает на крестик или жмет esc игра закрывается
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                      
                    # Выход из программы
                    sys.exit()   
  
                # Игра начинается когда игрок нажимает пробел или вверх.
                elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                    flappygame()
                  
                # Если игрок ничего не нажимает, ничего не происходит
                else:
                    window.blit(game_images['background'], (0, 0))
                    window.blit(game_images['flappybird'], (horizontal, vertical))
                    window.blit(game_images['sea_level'], (ground, elevation))
                      
                    # Экран делает ресeт
                    pygame.display.update()        
                      
                    # Установка количиства фреймов в секунду.
                    framepersecond_clock.tick(framepersecond)
    