import pygame
import cv2
import random
import math
import time

from pygame import mixer
from cvzone.HandTrackingModule import HandDetector


time_limit = 30  # 30 seconds


cap = cv2.VideoCapture(0)

detector = HandDetector(detectionCon=0.5, maxHands=1)

# Initialize pygame
pygame.init()
displayresolutionX, displayresolutionY = 1280, 720

# Create a screen
screen = pygame.display.set_mode((displayresolutionX, displayresolutionY))

# Icon and Title
pygame.display.set_caption("SPACE_DEFENDER")
icon = pygame.image.load('icon.png')
pygame.display.set_icon(icon)

# Background
background = pygame.image.load('bg.jpg')

# Music
mixer.music.load('background.wav')
mixer.music.play(-1)
bullet_sound = mixer.Sound('bullet.wav')
explosion_sound = mixer.Sound('explosion.wav')

# Score Text
score_value = 0
game_over = False
font = pygame.font.Font('freesansbold.ttf', 32)
textX, textY = 10, 10


def showScore(X, Y):
    score = font.render('Score: ' + str(score_value), True, (255, 255, 255))
    screen.blit(score, (X, Y))


# Enemy
num_of_enemies = 6
enemyImg = []
enemyX, enemyY = [], []
enemyX_change = []
enemySpeed = []
enemyY_change = 32
for enemy in range(num_of_enemies):
    enemyImg.append(pygame.image.load('enemy.png'))
    enemyX.append(random.randint(0, displayresolutionX - 32))
    enemyY.append(random.randint(0, displayresolutionY * 0.5))
    enemySpeed.append(random.randint(5, 10) / 10.0)
    enemyX_change.append(enemySpeed[enemy])

# Player
playerImg = pygame.image.load('spaceship.png')
playerX, playerY = displayresolutionX / 2 - 32, displayresolutionY - 64
playerX_change = 0
playerY_change = 0
playerSpeed = 5

# Bullet
# Ready State:
bulletImg = pygame.image.load('bullet.png')
bulletX, bulletY = playerX, playerY
bulletY_change = 50
bulletState = 'ready'


def player(X, Y):
    screen.blit(playerImg, (X, Y))


def enemy(X, Y, i):
    screen.blit(enemyImg[i], (X, Y))


def fireBullet(X, Y):
    global bulletState
    bulletState = 'fire'
    screen.blit(bulletImg, (X + 16, Y + 10))
    bullet_sound.play()


def isCollision(enemyX, enemyY, bulletX, bulletY):
    if bulletState != 'fire':
        return False
    distance = math.sqrt((enemyX - bulletX) ** 2 + (enemyY - bulletY) ** 2)
    if distance < 30:
        return True
    return False


game_over_font = pygame.font.Font('freesansbold.ttf', 64)
game_over_text = game_over_font.render("GAME OVER", True, (255, 255, 255))


def gameOver():
    for j in range(num_of_enemies):
        enemyY[j] = 1000
    playerX = 1000
    

 

# Game Loop
running = True
start_time = time.time()  # Initialize the start time at the beginning of the game loop
while running:
    elapsed_time = time.time() - start_time
    if elapsed_time > time_limit:
        game_over = True
    
    screen.fill((20, 20, 20))  # dark grey screen in RGB values
    screen.blit(background, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)

    hands, frame = detector.findHands(frame)

    if not hands:
        print("No hands found")
    else:
        hands1 = hands[0]
        fingers = detector.fingersUp(hands1)
        fingers_count = fingers.count(1)
        print(fingers_count)

        # Hand gesture control
        if fingers_count == 4:
            playerY_change = -playerSpeed
        elif fingers_count == 5:
            playerY_change = playerSpeed
        elif fingers_count == 1:
            playerX_change = playerSpeed
        elif fingers_count == 2:
            playerX_change = -playerSpeed
        
                        
        else:
            playerY_change = 0
            playerX_change = 0

        # Additional gesture for shooting
         
      
    fireBullet(playerX, playerY)   
    playerX += playerX_change
    if playerX > displayresolutionX - 64:
        playerX = displayresolutionX - 64
    if playerX < 0:
        playerX = 0

    playerY += playerY_change
    if playerY > displayresolutionY - 64:
        playerY = displayresolutionY - 64
    if playerY < 0:
        playerY = 0

    for i in range(num_of_enemies):
        # Game Over
        def gameOver():
         for j in range(num_of_enemies):
           enemyY[j] = 1000
           playerX = 1000

        
        if abs(enemyY[i] - playerY) < 70 and abs(enemyX[i] - playerX) < 70:
            gameOver()
            game_over = True
        enemyX[i] += enemyX_change[i]
        if enemyX[i] > displayresolutionX - 64:
            enemyX_change[i] = -enemySpeed[i]
            enemyY[i] += enemyY_change
        if enemyX[i] < 0:
            enemyX_change[i] = enemySpeed[i]
            enemyY[i] += enemyY_change
            

        # Collision
        collision = isCollision(enemyX[i], enemyY[i], bulletX, bulletY)
        if collision:
            bulletState = 'ready'
            score_value += 1
            explosion_sound.play()
            
        if collision:
                
             
            enemyX[i], enemyY[i] = random.randint(0, displayresolutionX - 64), 0
        enemy(enemyX[i], enemyY[i], i)
        

    # Bullet Movement
    if bulletY < -32:
        bulletState = 'ready'
    if bulletState == 'ready':
        bulletX, bulletY = playerX, playerY
    if bulletState == 'fire':
        fireBullet(bulletX, bulletY)
        bulletY -= bulletY_change

    if game_over:
        screen.blit(game_over_text, ((displayresolutionX / 2) * 0.7, (displayresolutionY / 2) * 0.8))
    player(playerX, playerY)
    showScore(textX, textY)
    pygame.display.update()

# Release resources
cap.release()
cv2.destroyAllWindows()
pygame.quit()
