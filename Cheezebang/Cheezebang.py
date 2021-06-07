import pygame
import sys
import random
from time import sleep
import os
import subprocess

#------------------------------------------------------------------------------------------------------------
BLACK = (0, 0, 0)
padWidth = 960 #1700     # 게임화면 가로크기
padHeight = 540 #1000    # 게임화면 세로크기

catImage=['./resources/cat1.png','./resources/cat2.png','./resources/cat3.png','./resources/cat4.png',
          './resources/cat5.png','./resources/cat6.png','./resources/cat7.png','./resources/cat8.png',
          './resources/cat9.png','./resources/cat10.png','./resources/cat11.png','./resources/cat12.png',
          './resources/cat13.png']

catSound = [
    './resources/cat1.mp3',
    './resources/cat2.mp3']

mavedir="C:\MAVE_RawData"
file_list=os.listdir(mavedir)
last_file=file_list[-1] #가장 최근의 파일 경로
print('file name: ',last_file)
rawfile=open(mavedir+"/"+last_file+"/"+"Rawdata.txt","r")
fft_file=open(mavedir+"/"+last_file+"/"+"Fp1_FFT.txt","r")

setloc=padWidth//8
catXloc=[setloc*3,setloc*4,setloc*5] #3칸

username=['SONG','AHN'] #나머지도 이름 넣기~ , 아직 송희,병선 기준만 있음
user_num=0 #init user #SONG
ref_list=[[0.0003,4.37213E-13,4.82271E-13],[0.0003,5.07691E-13,4.03242E-13]] # 순서대로 ERP, 12Hz, 17Hz #순서대로 송희,병선,+추가..

#------------------------------------------------------------------------------------------------------------
# 이름 입력받기용 #https://www.python2.net/questions-2013.htm
validChars = "`1234567890-=qwertyuiop[]\\asdfghjkl;'zxcvbnm,./"
shiftChars = '~!@#$%^&*()_+QWERTYUIOP{}|ASDFGHJKL:"ZXCVBNM<>?'
class TextBox(pygame.sprite.Sprite):
  def __init__(self):
    pygame.sprite.Sprite.__init__(self)
    self.text = ""
    self.font = pygame.font.Font("./resources/neodgm_pro.ttf", 40)
    self.image = self.font.render("Enter your name", False, [255, 0, 0])
    self.rect = self.image.get_rect()
  def add_chr(self, char):
    global shiftDown
    if char in validChars and not shiftDown:
        self.text += char
    elif char in validChars and shiftDown:
        self.text += shiftChars[validChars.index(char)]
    self.update()
  def update(self):
    old_rect_pos = self.rect.center
    self.image = self.font.render(self.text, False, [255, 0, 0])
    self.rect = self.image.get_rect()
    self.rect.center = old_rect_pos

#------------------------------------------------------------------------------------------------------------
def initGame():
    global gamePad, clock, background, mouse, cheese, life_on, life_off, explosion, cheeseSound, gameOverSound, padWidth,padHeight, intro, prolog_,user_num
    pygame.init()
    gamePad = pygame.display.set_mode((padWidth, padHeight))
    pygame.display.set_caption("CheezeBang!") # 게임 이름
    icon = pygame.image.load('./resources/icon.png') #게임아이콘
    pygame.display.set_icon(icon) #게임 위에 뜨는 아이콘
    background = pygame.image.load("./resources/background.png")      # 배경 그림
    background = pygame.transform.scale(background, (padWidth, padHeight))
    mouse = pygame.image.load("./resources/mouse.png")            # 쥐 그림
    mouse = pygame.transform.scale(mouse, (padWidth//19, padWidth//14))
    cheese = pygame.image.load("./resources/Cheese.png")            # 치즈(공격) 그림
    cheese = pygame.transform.scale(cheese, (padWidth // 20, padWidth // 20))
    explosion = pygame.image.load("./resources/explosion.png")        # 폭발 그림
    explosion = pygame.transform.scale(explosion, (padWidth // 6, padWidth // 7))
    intro = pygame.image.load("./resources/intro.jpg")      # 배경 그림
    intro = pygame.transform.scale(intro, (padWidth, padHeight))
    prolog_ = pygame.image.load("./resources/prolog.jpg")      # 배경 그림
    prolog_ = pygame.transform.scale(prolog_, (padWidth, padHeight))
    gameOverSound = pygame.mixer.Sound('./resources/gameover.wav')    # 게임 오버 사운드
    life_on = pygame.image.load("./resources/life_on.png")          # 빨간 하트
    life_off = pygame.image.load("./resources/life_off.png")        # 빈 하트
    clock = pygame.time.Clock()

#------------------------------------------------------------------------------------------------------------
# 고양이를 맞춘 개수 계산
def writeScore(count):
    global gamePad
    font = pygame.font.Font("./resources/neodgm_pro.ttf", 20)
    text = font.render('해치운 고양이 : ' + str(count), True, (255, 255, 255))
    gamePad.blit(text, (setloc * 0.3, padHeight / 6))

#------------------------------------------------------------------------------------------------------------
# 고양이가 화면 아래로 통과한 개수
def writePassed(count):
    global gamePad
    font = pygame.font.Font("./resources/neodgm_pro.ttf", 20)
    text = font.render('놓친 고양이 : ' + str(count), True, (255, 0, 0))
    gamePad.blit(text, (setloc * 0.3, padHeight / 6 + 30))

#------------------------------------------------------------------------------------------------------------
# 게임 메세지 출력
def writeMessage(text):
    global gamePad, gameOverSound
    textFont = pygame.font.Font("./resources/neodgm_pro.ttf", 80)
    text = textFont.render(text, True, (255, 0, 0))
    textpos = text.get_rect()
    textpos.center = (padWidth / 2, padHeight / 2)
    gamePad.blit(text, textpos)
    pygame.display.update()
    pygame.mixer.music.stop()   # 배경 음악 정지
    gameOverSound.play()        # 게임 오버 사운드 재생
    sleep(2)
    #pygame.mixer.music.play(-1) # 배경 음악 재생
    #runGame()

#------------------------------------------------------------------------------------------------------------
# 쥐가 고양이와 충돌했을 떄 메세지 출력
def crash():
    global gamePad
    writeMessage("쥐가 잡혔습니다...x,x")

#------------------------------------------------------------------------------------------------------------
# 게임 오버 메세지 보이기
def gameOver():
    global gamePad
    writeMessage("게임 오버!")

#------------------------------------------------------------------------------------------------------------
# 게임에 등장하는 객체를 드로잉
def drawObject(obj, x, y):
    global gamePad
    gamePad.blit(obj, (x, y))

#------------------------------------------------------------------------------------------------------------
def prolog():
    global gamePad, clock, intro, prolog_,shiftDown,user_num
    runGame=False
    state=0
    input_blink=0 #사용자 이름 깜빡이며..
    hello_blink=0
    #뇌파 데이터 수집문구 띄우기
    font = pygame.font.Font("./resources/neodgm_pro.ttf", 40)
    font_small = pygame.font.Font("./resources/neodgm_pro.ttf", 30)

    # 기다리기 용
    count_fft = 0
    list_12 = []  # 주파수 12 받는곳, 40~60
    list_15 = []  # 주파수 15 받는곳, 40~60
    ref_12 = -1
    ref_15 = -1
    pygame.mixer.music.load('./resources/평화로운음악.mp3') # intro 음악
    pygame.mixer.music.play(-1) # 배경 음악 재생


    # 사용자를 입력하세요
    textBox=TextBox()
    textBox.rect.center=[padWidth/2,padHeight-50]
    shiftDown = False
    while not runGame:
        if state==0:
            drawObject(intro, 0, 0)
            input_blink+=1
            if 0<input_blink%80<40:
                gamePad.blit(textBox.image, textBox.rect)
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                if e.type == pygame.KEYUP:
                    if e.key in [pygame.K_RSHIFT, pygame.K_LSHIFT]:
                        shiftDown = False
                if e.type == pygame.KEYDOWN:
                    textBox.add_chr(pygame.key.name(e.key))
                    if e.key == pygame.K_SPACE:
                        textBox.text += " "
                        textBox.update()
                    if e.key in [pygame.K_RSHIFT, pygame.K_LSHIFT]:
                        shiftDown = True
                    if e.key == pygame.K_BACKSPACE:
                        textBox.text = textBox.text[:-1]
                        textBox.update()
                    if e.key == pygame.K_RETURN:
                        if len(textBox.text) > 0:
                            print(textBox.text.upper()) #사용자 이름 출력
                            running = False
                            state = 1

        elif state==1: #사용자 이름 깜빡이기
            drawObject(intro, 0, 0)
            hello_blink+=1
            inputname=textBox.text.upper() #입력된 이름

            if inputname in username: #사용자 목록에 이름 존재
                user_num=username.index(inputname) #사용자 번호 반환
                nametext = font.render(f'HELLO {inputname}!', True, (255, 0, 0))
                #가운데정렬
                name_rect=nametext.get_rect()
                name_rect.center = [padWidth / 2, padHeight - 50]
                if 0<hello_blink%30<15:
                    gamePad.blit(nametext, name_rect)
            else:
                nametext = font_small.render('등록되지 않은 사용자!', True, (255, 0, 0))
                #가운데정렬
                name_rect=nametext.get_rect()
                name_rect.center = [padWidth / 2, padHeight - 70]
                gamePad.blit(nametext, name_rect)

                nametext2 = font_small.render('송희의 기준으로 게임을 시작합니다', True, (255, 0, 0))
                #가운데정렬
                name_rect2=nametext2.get_rect()
                name_rect2.center = [padWidth / 2, padHeight - 30]
                gamePad.blit(nametext2, name_rect2)

            if hello_blink>90:
                pygame.mixer.music.stop()  # 배경음악 중지
                booksound = pygame.mixer.Sound('./resources/책넘기는소리.wav')
                sleep(0.02)
                booksound.play()  # 책 넘기는 소리 재생
                state=2

        elif state==2: #space 키 한번 누른 상태 #입력한 상태
            datatxt = font_small.render('중립 뇌파 데이터를 수집중입니다 (%d/60)' %count_fft, True, (255, 0, 0))
            datatxt2 = font_small.render('중립 뇌파 데이터를 수집중입니다 (%d/60).' %count_fft, True, (255, 0, 0))
            datatxt3 = font_small.render('중립 뇌파 데이터를 수집중입니다 (%d/60)..' %count_fft, True, (255, 0, 0))
            datatxt4 = font_small.render('중립 뇌파 데이터를 수집중입니다 (%d/60)...'%count_fft, True, (255, 0, 0))
            datatxt_list = [datatxt, datatxt2, datatxt3, datatxt4]

            #글자 출력
            drawObject(prolog_, 0, 0)  # 프롤로그 이미지
            gamePad.blit(datatxt_list[count_fft%4], (padWidth / 5, padHeight - 50))
            #fft reference 받아오기
            try:
                line = fft_file.readline()
                if line:
                    count_fft += 1
                    print(count_fft)
                    splitline = line.split('\t')  # tab으로 분리

                    if 40 < count_fft <= 60:  # 이 구역만 배열에 저장 -> referene
                        splitline=list(map(float,splitline[1:])) #문자열배열 int형으로 변환,맨 앞(시간)제외
                        _12hz=sum(splitline[30*11:30*13]) #12.00~12.97: 30*12:30*13 /// 구역 넓게 11~12.97
                        _15hz=sum(splitline[30*14:30*16]) #17.00~17.97: 30*17:30*18 /// 구역 넓게 14~15.97
                        list_12.append(_12hz)
                        list_15.append(_15hz)

            except:
                pass

            if count_fft==60:
                break #게임 화면으로 전환

        pygame.display.update()  # 게임화면을 다시그림
        clock.tick(60)

#------------------------------------------------------------------------------------------------------------
def runGame():
    global gamePad, clock, background, mouse, cheese, life_on, life_off, explosion, cheeseSound,user_num

    pygame.mixer.music.load('./resources/music.wav')                  # 배경 음악
    pygame.mixer.music.play(-1)             # 배경 음악 재생

    # 쥐가 고양이한테 닿았을 경우 True
    isShot = False
    shotCount = 0
    catPassed = 0

    # 쥐 크기
    mouseSize = mouse.get_rect().size
    mouseWidth = mouseSize[0]
    mouseHeight = mouseSize[1]

    # 쥐 초기 위치 (x, y)
    x = padWidth * 0.5 - mouseWidth * 0.5
    y = padHeight * 0.9
    mouseX = 0

    # 치즈 위치 좌표 리스트
    cheeseXY = []

    # 고양이 랜덤 생성
    cat = pygame.image.load(random.choice(catImage))
    cat = pygame.transform.scale(cat, (padWidth // 12, padWidth // 9))
    catSize = cat.get_rect().size     # 고양이 크기
    catWidth = catSize[0]
    catHeight = catSize[1]
    destorySound = pygame.mixer.Sound(random.choice(catSound))


    # 고양이 초기 위치 설정
    catrandom = random.choice(catXloc)
    catX = catrandom - catWidth / 2
    catY = 0
    catSpeed = 1
    onGame = False

    # 자극 띄우기 위한 시간 추적 객체 #ref https://runebook.dev/ko/docs/pygame/ref/time
    color=[(0,0,0),(255,255,255),(255,255,0),(0,0,255)] #검, 흰,노, 파 #논문을 찾아서 노란색으로 해도 될듯..? 아니면 시각 피로도와 연관지어도 될것가틈
    SSVEP_count=0
    ERP_count=0
    SSVEP_color12= color[0]
    SSVEP_color15=color[0]

    life = [life_on, life_on, life_on] # 하트 초기화
    bomb = 3

    while not onGame:
        # 자극 띄우기 위한 시간 추적 객체 #ref https://runebook.dev/ko/docs/pygame/ref/time
        SSVEP_clock = pygame.time.get_ticks()
        ERP_clock = pygame.time.get_ticks()
        checkmax = -1
        try:
            if ERP_count%30==0:
                linelist=rawfile.readlines(-1)
                split_fp1=[]
                for i in linelist: #fp1신호만 불러오기
                    split_fp1.append(i.split('\t')[1])

                checkmax=float(max(split_fp1))
                print(checkmax)

        except:
            pass

        inputkey = 0
        checkstate = 0  # 안보는 상태

        if ERP_count % 60 == 30:  # 좌측 #0~30이니까 0일때 움직이는걸 30에서 체크
            if checkmax > ref_list[user_num][0]: #0: ERP
                checkstate = 1
        elif ERP_count % 60 == 0:  # 우측
            if checkmax > ref_list[user_num][0]: #0: ERP
                checkstate = 2
        if checkstate == 1 or checkstate == 2:
            print(checkstate, '------------------------------------------')
        for event in pygame.event.get():
            if event.type in [pygame.QUIT]:
                pygame.quit()
                sys.exit()
            if event.type in [pygame.KEYDOWN]:
                if (event.key == pygame.K_LEFT and inputkey == 0):  # 쥐 왼쪽으로 이동
                    mouseX = -setloc  # 180
                    inputkey += 1

                elif (event.key == pygame.K_RIGHT and inputkey == 0):  # 쥐 오른쪽으로 이동
                    mouseX = setloc  # 180
                    inputkey += 1
                elif event.key == pygame.K_SPACE:  # 치즈 발사
                    cheeseX = x  # + mouseWidth / 2
                    cheeseY = y + mouseHeight
                    cheeseXY.append([cheeseX, cheeseY])

            if event.type in [pygame.KEYUP] and inputkey == 1:  # 방향키를 떄면 쥐를 멈춤
                mouseX = 0
                inputkey = 0

        if checkstate:
            if (checkstate == 1 and inputkey == 0):  # 쥐 왼쪽으로 이동
                mouseX = -setloc  # 180
                inputkey += 1

            elif (checkstate == 2 and inputkey == 0):  # 쥐 오른쪽으로 이동
                mouseX = setloc  # 180
                inputkey += 1

        drawObject(background, 0, 0)    # 배경 화면 그리기

        # 쥐 위치 재조정
        if inputkey==1:
            x += mouseX
        if x < setloc*3 - mouseWidth / 2:
            x = setloc*3 - mouseWidth / 2
        elif x > setloc*5 - mouseWidth / 2 :
            x = setloc*5 - mouseWidth / 2

        # 쥐가 고양이와 충돌했는지 체크
        if y < catY + catHeight:
            if (x < catX < x + mouseWidth) or \
                    (catX + catWidth > x and catX + catX + catWidth < x + mouseWidth):
                crash()


        if ERP_count==0: #초기 자동발사
            cheeseXY.append([x, y])

        # 치즈 발사 화면에 그리기
        if len(cheeseXY) != 0:
            for i, bxy in enumerate(cheeseXY): # 치즈에 대해 반복함(자동발사)
                bxy[1] -= 30                    # 총알(치즈)의 y 좌표 -30 (위로 이동)
                cheeseXY[i][1] = bxy[1]

                # 치즈가 고양이를 맞추었을 경우
                if bxy[1] < catY:
                    if catX < bxy[0] < catX + catWidth:
                        cheeseXY.remove(bxy)
                        isShot = True
                        shotCount += 1
                        cheeseX = x
                        cheeseY = y + mouseHeight
                        cheeseXY.append([cheeseX, cheeseY])

                if bxy[1] <= 0:                 # 치즈가 화면 밖을 벗어나면
                    try:
                        cheeseXY.remove(bxy)   # 치즈 제거
                        cheeseX = x
                        cheeseY = y + mouseHeight
                        cheeseXY.append([cheeseX, cheeseY])
                    except:
                        pass

        if shotCount>=10: #고양이 10마리 이상 때리면
            pygame.mixer.music.stop()  # 배경 음악 정지
            return 0 #종료

        if len(cheeseXY) != 0:
            for bx, by in cheeseXY:
                drawObject(cheese, bx, by)

        drawObject(mouse, x, y)  # 쥐를 게임 회면의 (x, y) 좌표에 그리기

        writeScore(shotCount)
        catY += catSpeed # 고양이가 아래로 움직임

        # 고양이가 쥐랑 닿은 경우
        if catY > padHeight:
            # 새로운 고양이 (랜덤)
            cat = pygame.image.load(random.choice(catImage))
            cat = pygame.transform.scale(cat, (padWidth // 12, padWidth // 9))
            catSize = cat.get_rect().size
            catWidth = catSize[0]
            catHeight = catSize[1]
            catrandom = random.choice(catXloc)
            catX = catrandom - catWidth / 2
            catY = 0
            catPassed += 1
        if 3 >= catPassed >= 1: # 고양이 3개 놓치면 게임오버
            life[catPassed - 1] = life_off

        if catPassed == 3: # 고양이 3개 놓치면 게임오버
            gameOver()
            return -1 #:게임오버

        # 놓친 고양이 수 표시
        life[0] = pygame.transform.scale(life[0], (35 , 30))
        life[1] = pygame.transform.scale(life[1], (35 , 30))
        life[2] = pygame.transform.scale(life[2], (35 , 30))
        lifeX = int(setloc * 0.3)
        lifeY = padHeight / 6 + 30
        drawObject(life[0], lifeX + 90, lifeY)
        drawObject(life[1], lifeX + 45, lifeY)
        drawObject(life[2], lifeX, lifeY)


        # 고양이를 맞춘 경우
        if isShot:
            # 고양이 사라짐
            bomb = 0
            bombX = catX
            bombY = catY
            destorySound.play()  # 고양이 사라지는 사운드 재생
            # 새로운 고양이 (랜덤)
            cat = pygame.image.load(random.choice(catImage))
            cat = pygame.transform.scale(cat, (padWidth // 12, padWidth // 9))
            catSize = cat.get_rect().size
            catWidth = catSize[0]
            catHeight = catSize[1]
            catrandom = random.choice(catXloc)
            catX = catrandom - catWidth / 2
            catY = 0
            destorySound = pygame.mixer.Sound(random.choice(catSound))

            isShot = False

            # 고양이 맞추면 속도 증가
            catSpeed += 0.02
            if catSpeed >= 10:
                catSpeed = 10

        drawObject(cat, catX, catY)  # 고양이 그리기
        if bomb < 3 :
            drawObject(explosion, bombX-padWidth//24, bombY)
            bomb += 1

        #-------------------------------------------
        #SSVEP 자극 띄우기 12 --> 5*12 -> 12frame
        if SSVEP_count%5==0 and SSVEP_count%10!=0:
            SSVEP_color12=color[0] #검
        elif SSVEP_count%10==0: #5에는 아니고 10만
            SSVEP_color12 =color[1] #흰
        pygame.draw.rect(gamePad, SSVEP_color12, [0, padHeight-setloc*2.5, setloc*2.5, setloc*2.5]) #SSVEP 12 그리기

        #SSVEP 자극 띄우기 15 --> 4*15 -> 15frame
        if SSVEP_count%4==0 and SSVEP_count%8!=0:
            SSVEP_color15=color[0]
        elif SSVEP_count%8==0: #5에는 아니고 10만
            SSVEP_color15 =color[1]
        pygame.draw.rect(gamePad, SSVEP_color15, [padWidth-setloc*2.5, padHeight-setloc*2.5, setloc*2.5, setloc*2.5]) #SSVEP 12 그리기

        #ERP 띄우기 5-> 12*5 ->5frame.. 너무빠른것같은데 1frame으로바꿔봄 6->30, 12-60 으로 했음
        if 0<=ERP_count%60<30: #번갈아가면서 깜빡임
            ##ERP 띄우기 왼쪽 삼각형
            if SSVEP_color12==color[0]: #검은색이면
                ERP_color_L=color[2] #노란색
            else: #흰색이면
                ERP_color_L=color[3] #파란색
            pygame.draw.polygon(gamePad, ERP_color_L, [[setloc*0.75, padHeight-setloc*1.25], [setloc*1.5, padHeight-setloc*0.75], [setloc*1.5, padHeight-setloc*1.75]])
        elif 30<=ERP_count%60<60: #번갈아가면서 깜빡임
            ##ERP 띄우기 오른쪽 삼각형
            if SSVEP_color15==color[0]: #검은색이면
                ERP_color_R=color[2] #노란색
            else: #흰색이면
                ERP_color_R=color[3] #파란색
            pygame.draw.polygon(gamePad, ERP_color_R, [[padWidth-setloc*0.75, padHeight-setloc*1.25], [padWidth-setloc*1.5, padHeight-setloc*0.75], [padWidth-setloc*1.5, padHeight-setloc*1.75]])


        #중앙에 십자가 띄우기?(봐서 추가하겠음)

        SSVEP_count+=1
        ERP_count+=1

        pygame.display.update()  # 게임화면을 다시그림
        clock.tick(60)                  # 게임화면의 초당 프레임수를 60으로 설정

#------------------------------------------------------------------------------------------------------------
def gameOverImage():
    finishGame=False
    gameover = pygame.image.load("./resources/lose.png")  # 배경 그림
    gameover = pygame.transform.scale(gameover, (padWidth, padHeight))
    drawObject(gameover, 0, 0)
    oversound = pygame.mixer.Sound('./resources/실패_효과음.mp3')
    oversound.play()  # 책 넘기는 소리 재생
    while not finishGame:
        pygame.display.update()  # 게임화면을 다시그림
        clock.tick(60)

        for event in pygame.event.get():
            if event.type in [pygame.KEYDOWN]:
                if event.key == pygame.K_SPACE:
                    pygame.quit()  # space 누르면 pygame 종료
                    sys.exit()

                elif event.key == 13:  # 엔터 누르면 중립측정 단계 없이 다시 게임 시작
                    playGame()


#------------------------------------------------------------------------------------------------------------
def winImage():
    finishGame = False
    winImage = pygame.image.load("./resources/win.png")  # 배경 그림
    winImage = pygame.transform.scale(winImage, (padWidth, padHeight))
    drawObject(winImage, 0, 0)
    winsound = pygame.mixer.Sound('./resources/이겼을때효과음_볼륨up.mp3')
    winsound.play()  # 책 넘기는 소리 재생
    while not finishGame:
        pygame.display.update()  # 게임화면을 다시그림
        clock.tick(60)

        for event in pygame.event.get():
            if event.type in [pygame.KEYDOWN]:
                if event.key == pygame.K_SPACE:
                    pygame.quit()  # space 누르면 pygame 종료
                    sys.exit()

                elif event.key == 13: #엔터 누르면 중립측정 단계 없이 다시 게임 시작
                    winsound.stop()
                    playGame()


#------------------------------------------------------------------------------------------------------------
def playGame():
    finish = runGame()

    if finish == -1:  # 게임오버되면
        gameOverImage()

    else:  # 10마리 퇴치
        winImage()

    return

#실행
initGame()
prolog()
playGame()
