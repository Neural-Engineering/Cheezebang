import pygame
import sys
import random
from time import sleep
import os

# ------------------------------------------------------------------------------------------------------------
BLACK = (0, 0, 0)
padWidth = 960  # 1700     # 게임화면 가로크기
padHeight = 540  # 1000    # 게임화면 세로크기

# 고양이 이미지
catImage = ['./resources/cat1.png', './resources/cat2.png', './resources/cat3.png', './resources/cat4.png',
            './resources/cat5.png', './resources/cat6.png', './resources/cat7.png', './resources/cat8.png',
            './resources/cat9.png', './resources/cat10.png', './resources/cat11.png', './resources/cat12.png',
            './resources/cat13.png']

# 고양이 맞았을 때 효과음
catSound = [
    './resources/cat1.mp3',
    './resources/cat2.mp3']

# 가장 최근에 생성된 파일 불러오기
mavedir = "C:\MAVE_RawData"
file_list = os.listdir(mavedir)
last_file = file_list[-1]  # 가장 최근의 파일 경로
print('file name: ', last_file)
rawfile = open(mavedir + "/" + last_file + "/" + "Rawdata.txt", "r")
fft_file = open(mavedir + "/" + last_file + "/" + "Fp1_FFT.txt", "r")

# 화면 비율 설정한것에 맞게 이미지 사이즈 조절용
setloc = padWidth // 8
catXloc = [setloc * 3, setloc * 4, setloc * 5]  # 3칸

# 등록된 사용자
username = ['SONG', 'AHN', 'SOO', 'MINJI', 'YANU']  # 송희,병선,수민,민지,연우 순서
user_num = 0  # init user #SONG

# 순서대로 개인별 ERP, reference 대비 12Hz 증가 기준, 17Hz 증가 기준 # 순서대로 송희,병선,수민,민지,연우
ref_list = [[0.00007, 4.37213E-13, 4.82271E-13],  # 송희
            [0.00004, 5.07691E-13, 4.03242E-13],  # 병선
            [0.000035, 4.37213E-13, 4.82271E-13],  # 수민
            [0.00003, 3.57691E-13, 3.43642E-13],  # 민지
            [0.000035, 4.82633E-13, 4.66241E-13]]  # 연우

# 12, 17hz reference를 위한 전역변수
r_12 = -1
r_17 = -1

# ------------------------------------------------------------------------------------------------------------
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


# ------------------------------------------------------------------------------------------------------------
def initGame():
    global gameScreen, clock, background, mouse, cheese, life_on, life_off, explosion, cheeseSound, gameOverSound, padWidth, padHeight, intro, prolog_, user_num
    pygame.init()
    gameScreen = pygame.display.set_mode((padWidth, padHeight))
    pygame.display.set_caption("CheezeBang!")  # 게임 이름
    icon = pygame.image.load('./resources/icon.png')  # 게임아이콘
    pygame.display.set_icon(icon)  # 게임 위에 뜨는 아이콘
    background = pygame.image.load("./resources/background.png")  # 배경 그림
    background = pygame.transform.scale(background, (padWidth, padHeight))
    mouse = pygame.image.load("./resources/mouse.png")  # 쥐 그림
    mouse = pygame.transform.scale(mouse, (padWidth // 19, padWidth // 14))
    cheese = pygame.image.load("./resources/Cheese.png")  # 치즈(공격) 그림
    cheese = pygame.transform.scale(cheese, (padWidth // 20, padWidth // 20))
    explosion = pygame.image.load("./resources/explosion.png")  # 폭발 그림
    explosion = pygame.transform.scale(explosion, (padWidth // 6, padWidth // 7))
    intro = pygame.image.load("./resources/intro.jpg")  # 배경 그림
    intro = pygame.transform.scale(intro, (padWidth, padHeight))
    prolog_ = pygame.image.load("./resources/prolog.jpg")  # 배경 그림
    prolog_ = pygame.transform.scale(prolog_, (padWidth, padHeight))
    gameOverSound = pygame.mixer.Sound('./resources/gameover.wav')  # 게임 오버 사운드
    life_on = pygame.image.load("./resources/life_on.png")  # 빨간 하트
    life_off = pygame.image.load("./resources/life_off.png")  # 빈 하트
    clock = pygame.time.Clock()


# ------------------------------------------------------------------------------------------------------------
# 고양이를 맞춘 개수 계산
def writeScore(count):
    global gameScreen
    font = pygame.font.Font("./resources/neodgm_pro.ttf", 20)
    text = font.render('해치운 고양이 : ' + str(count), True, (255, 255, 255))
    gameScreen.blit(text, (setloc * 0.3, padHeight / 6))


# ------------------------------------------------------------------------------------------------------------
# 고양이가 화면 아래로 통과한 개수
def writePassed(count):
    global gameScreen
    font = pygame.font.Font("./resources/neodgm_pro.ttf", 20)
    text = font.render('놓친 고양이 : ' + str(count), True, (255, 0, 0))
    gameScreen.blit(text, (setloc * 0.3, padHeight / 6 + 30))


# ------------------------------------------------------------------------------------------------------------
# 게임 메세지 출력 (졌을 때)
def writeMessage(text):
    global gameScreen, gameOverSound
    textFont = pygame.font.Font("./resources/neodgm_pro.ttf", 80)
    text = textFont.render(text, True, (255, 0, 0))
    textpos = text.get_rect()
    textpos.center = (padWidth / 2, padHeight / 2)
    gameScreen.blit(text, textpos)
    pygame.display.update()
    pygame.mixer.music.stop()  # 배경 음악 정지
    gameOverSound.play()  # 게임 오버 사운드 재생
    sleep(2)


# ------------------------------------------------------------------------------------------------------------
# 쥐가 고양이와 충돌했을 떄 메세지 출력
def crash():
    global gameScreen
    writeMessage("쥐가 잡혔습니다...x,x")


# ------------------------------------------------------------------------------------------------------------
# 게임 오버 메세지 보이기
def gameOver():
    global gameScreen
    writeMessage("게임 오버!")


# ------------------------------------------------------------------------------------------------------------
# 게임에 등장하는 객체를 드로잉
def drawObject(obj, x, y):
    global gameScreen
    gameScreen.blit(obj, (x, y))


# ------------------------------------------------------------------------------------------------------------
def prolog():
    global gameScreen, clock, intro, prolog_, shiftDown, user_num, r_12, r_17
    runGame = False
    state = 0
    input_blink = 0  # 사용자 이름 깜빡이며 입력창
    hello_blink = 0  # Hello 문구 일정 시간 띄우기

    # 뇌파 데이터 수집문구 띄우기
    font = pygame.font.Font("./resources/neodgm_pro.ttf", 40)
    font_small = pygame.font.Font("./resources/neodgm_pro.ttf", 30)

    # 기다리기 용
    count_fft = 0
    pygame.mixer.music.load('./resources/평화로운음악.mp3')  # intro 음악
    pygame.mixer.music.play(-1)  # 배경 음악 재생

    list_12 = []  # 주파수 12 받는곳, 40~60
    list_17 = []  # 주파수 17 받는곳, 40~60

    # 사용자를 입력하세요
    textBox = TextBox()
    textBox.rect.center = [padWidth / 2, padHeight - 50]
    shiftDown = False
    while not runGame:
        if state == 0:
            drawObject(intro, 0, 0)
            input_blink += 1
            if 0 < input_blink % 80 < 40:
                gameScreen.blit(textBox.image, textBox.rect)
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pass
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
                            print(textBox.text.upper())  # 사용자 이름 출력
                            pass
                            state = 1

        elif state == 1:  # 사용자 이름 깜빡이기
            drawObject(intro, 0, 0)
            hello_blink += 1
            inputname = textBox.text.upper()  # 입력된 이름

            if inputname in username:  # 사용자 목록에 이름 존재
                user_num = username.index(inputname)  # 사용자 번호 반환
                nametext = font.render(f'HELLO {inputname}!', True, (255, 0, 0))
                # 가운데정렬
                name_rect = nametext.get_rect()
                name_rect.center = [padWidth / 2, padHeight - 50]
                if 0 < hello_blink % 30 < 15:
                    gameScreen.blit(nametext, name_rect)
            else:
                nametext = font_small.render('등록되지 않은 사용자!', True, (255, 0, 0))
                # 가운데정렬
                name_rect = nametext.get_rect()
                name_rect.center = [padWidth / 2, padHeight - 70]
                gameScreen.blit(nametext, name_rect)

                nametext2 = font_small.render('송희의 기준으로 게임을 시작합니다', True, (255, 0, 0))
                # 가운데정렬
                name_rect2 = nametext2.get_rect()
                name_rect2.center = [padWidth / 2, padHeight - 30]
                gameScreen.blit(nametext2, name_rect2)

            if hello_blink > 90:
                booksound = pygame.mixer.Sound('./resources/책넘기는소리.wav')
                sleep(0.02)
                booksound.play()  # 책 넘기는 소리 재생
                state = 2

        elif state == 2:  # 이름 입력한 상태
            datatxt = font_small.render('중립 뇌파 데이터를 수집중입니다 (%d/60)' % count_fft, True, (255, 0, 0))
            datatxt2 = font_small.render('중립 뇌파 데이터를 수집중입니다 (%d/60).' % count_fft, True, (255, 0, 0))
            datatxt3 = font_small.render('중립 뇌파 데이터를 수집중입니다 (%d/60)..' % count_fft, True, (255, 0, 0))
            datatxt4 = font_small.render('중립 뇌파 데이터를 수집중입니다 (%d/60)...' % count_fft, True, (255, 0, 0))
            datatxt_list = [datatxt, datatxt2, datatxt3, datatxt4]

            # 글자 출력
            drawObject(prolog_, 0, 0)  # 프롤로그 이미지
            gameScreen.blit(datatxt_list[count_fft % 4], (padWidth / 5, padHeight - 50))

            # fft reference 받아오기
            try:
                line = fft_file.readline()
                if line:
                    count_fft += 1
                    print(count_fft)
                    split_line = line.split('\t')  # tab으로 분리

                    if 40 < count_fft <= 60:  # 이 구역만 배열에 저장 -> referene
                        split_line = list(map(float, split_line[1:]))  # 문자열배열 int형으로 변환,맨 앞(시간)제외
                        _12hz = sum(split_line[5 * 11:5 * 13])  # 12hz /// 구역 넓게 11~12.80
                        _17hz = sum(split_line[5 * 16:5 * 18])  # 17hz /// 구역 넓게 16~17.80
                        list_12.append(_12hz)
                        list_17.append(_17hz)

            except:
                pass

            if count_fft == 60:
                r_12 = sum(list_12) / len(list_12)
                r_17 = sum(list_17) / len(list_17)
                print(r_12, r_17)  # 12hz, 17hz 기준 출력
                pygame.mixer.music.stop()  # 배경음악 중지
                break  # 게임 화면으로 전환

        pygame.display.update()  # 게임화면을 다시그림
        clock.tick(60)


# ------------------------------------------------------------------------------------------------------------
def runGame():
    global gameScreen, clock, background, mouse, cheese, life_on, life_off, explosion, cheeseSound, user_num, r_12, r_17

    pygame.mixer.music.load('./resources/music.wav')  # 배경 음악
    pygame.mixer.music.play(-1)  # 배경 음악 재생

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
    catSize = cat.get_rect().size  # 고양이 크기
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
    color = [(0, 0, 0), (255, 255, 255), (255, 255, 0), (0, 0, 255)]  # 검, 흰, 노, 파
    SSVEP_count = 0
    ERP_count = 0
    SSVEP_color12 = color[0]
    SSVEP_color17 = color[0]

    life = [life_on, life_on, life_on]  # 하트 초기화
    bomb = 3
    ssvep_state = 0  # ssvep 상태 관리
    '''gb
    ssvep_state 0: 초기상태, 집중하지 않은 상태
    ssvep_state 1: 12hz에 집중한 상태
    ssvep_state 2: 17hz에 집중한 상태
    ssvep_state 3: 12hz, 17hz 모두에 기준치 이상으로 상승한 상태
    * 만약 ssvep_state 3에서 12, 17 모두에 erp 피크가 뜰 경우 17로 이동한다(거의 모든 경우 12, 17 모두가 기준치 이상으로 상승할 경우 17을 볼때가 많았음)
    '''

    erp_state_12 = 0  # erp 왼쪽(12hz 뜨는 부분) 체크 관리
    erp_state_17 = 0  # erp 왼쪽(12hz 뜨는 부분) 체크 관리
    '''
    erp_state 0: erp 체크 안하는중
    erp_state 1: ssvep 상승한 후 erp 자극 시작(처음 발생)
    erp_state 2: 자극 처음 발생으로부터 0.5초 지난 상태 (0.3~0.5 구간 보니까 여기까지만 확인)
    erp_state 3: 이동
    '''

    keep_state = 0  # 12,17 둘다 올랐을 경우, 왼쪽 오른쪽 erp 둘다 비교하기 위함
    '''
    keep_state 0: init
    keep_state 1: 좌측 ERP가 먼저 나옴
    keep_state 2: 우측 ERP가 먼저 나옴
    keep_state 3: 좌측 ERP 자극이 먼저 나왔고, 좌측 p300 상승함
    keep_state 4: 우측 ERP 자극이 먼저 나왔고, 우측 p300 상승함
    keep_state 5: 왼쪽으로 이동
    keep_state 6: 오른쪽으로 이동
    '''

    while not onGame:
        # ssvep 부르기 - 중립 측정 이후 바로 넘어가서 이전거 날릴 필요 없음
        line = fft_file.readline()
        if line:  # fft 파일 생성되었으면
            ssvep_state = 0  # 새로운 fft 파일이 생성되기 전까지는 상태가 유지된다.
            split_line = line.split('\t')
            split_line = list(map(float, split_line[1:]))  # 문자열배열 int형으로 변환,맨 앞(시간)제외
            _12hz = sum(split_line[5 * 11:5 * 13])  # 12hz /// 구역 넓게 11~12.80
            _17hz = sum(split_line[5 * 16:5 * 18])  # 17hz /// 구역 넓게 16~17.80

            if r_12 + ref_list[user_num][1] <= _12hz:
                ssvep_state = 1

            if r_17 + ref_list[user_num][2] <= _17hz:
                if ssvep_state == 1:
                    ssvep_state = 3  # 둘다 기준치 이상 올라감
                else:
                    ssvep_state = 2

        # erp 불러옴
        '''
        12 보거나 17 보는 경우에만 erp (1,2,3) 12hz 볼 경우:1,3 17hz 볼 경우:2,3
        ERP는 1초에 최대 256개 생기며, FFT 파일은 반드시 1초 이상(실험 결과 최소 1.1초~6초)걸리므로 좌/우의 ERP 자극이 시작하는 구간이 반드시 이 안에 존재함
        12hz: ERP_count%60==0일때 자극 처음 생성
        17hz: ERP_count%30==0 and ERP_count%60!=0일때 자극 처음 생성
        '''
        # --------------- 12만 올랐던 상태
        if ssvep_state == 1 and erp_state_12 == 0 and ERP_count % 60 == 0:  # 12만 오름, 12 체크중일 때 아닌 상태, 자극 시작임
            try:
                rawfile.readlines(-1)  # 값 날리기
            except:
                pass
            erp_state_12 = 1

        elif erp_state_12 == 1 and ERP_count % 30 == 0 and ERP_count % 60 != 0:  # 12hz자극이 시작하고 0.5초 지남
            try:
                linelist = rawfile.readlines(-1)
                split_fp1 = []
                for i in linelist:  # fp1신호만 불러오기
                    split_fp1.append(float(i.split('\t')[1]))

                lenlist = len(split_fp1)  # list 길이
                split_time = split_fp1[int(lenlist * 0.4):]  # 0.3~0.5초 구간

                if max(split_time) > ref_list[user_num][0]:  # ERP 기준 넘음
                    erp_state_12 = 3  # 이동하는 상태
                else:
                    erp_state_12 = 0  # 집중 안함
            except:
                pass


        # --------------- 17만 올랐던 상태
        elif ssvep_state == 2 and erp_state_17 == 0 and ERP_count % 30 == 0 and ERP_count % 60 != 0:  # 17만 오름, 17 체크중일 때 아닌 상태, 자극 시작임
            try:
                rawfile.readlines(-1)  # 값 날리기
            except:
                pass
            erp_state_17 = 1

        elif erp_state_17 == 1 and ERP_count % 60 == 0:  # 17hz자극이 시작하고 0.5초 지남
            try:
                linelist = rawfile.readlines(-1)
                split_fp1 = []
                for i in linelist:  # fp1신호만 불러오기
                    split_fp1.append(float(i.split('\t')[1]))

                lenlist = len(split_fp1)  # list 길이
                split_time = split_fp1[int(lenlist * 0.4):]  # 0.3~0.5초 구간

                if max(split_time) > ref_list[user_num][0]:  # ERP 기준 넘음
                    erp_state_17 = 3  # 이동하는 상태
                else:
                    erp_state_17 = 0  # 집중 안함
            except:
                pass


        # --------------- 12, 17 모두 오른 상태
        elif ssvep_state == 3 and ERP_count % 30 == 0:
            try:
                rawfile.readlines(-1)  # 값 날리기
            except:
                pass
            erp_state_12 = 1
            erp_state_17 = 1

        elif erp_state_12 == 1 and erp_state_17 == 1 and ERP_count % 30 == 0:
            if ERP_count % 60 == 0:  # 우측 자극 시작 후 0.5초임
                if keep_state == 0:
                    keep_state = 2  # 17 자극이 12자극보다 먼저 나왔음
                try:
                    linelist = rawfile.readlines(-1)
                    split_fp1 = []
                    for i in linelist:  # fp1신호만 불러오기
                        split_fp1.append(float(i.split('\t')[1]))

                    lenlist = len(split_fp1)  # list 길이
                    split_time = split_fp1[int(lenlist * 0.4):]  # 0.3~0.5초 구간

                    if max(split_time) > ref_list[user_num][0]:  # ERP 기준 넘음
                        if keep_state == 2:  # 우측 ERP 자극이 먼저 나온 상태이면
                            keep_state = 4  # 우측 ERP 상승한상태, 좌측은 아직 검사X
                        elif keep_state == 1:  # 좌측 자극 먼저 나왔지만 좌측은 상승하지 않음
                            keep_state = 6  # 오른쪽으로 이동
                        elif keep_state == 3:  # 좌측자극 먼저 나왔고 좌측 ERP 상승한 상태
                            keep_state = 6  # 좌/우 모두 ERP 나온 경우 오른쪽으로 이동
                    else:
                        if keep_state==1: #좌측 자극 먼저 검사했을때 상승 안되었었는데, 우측 자극에서도 상승 X
                            keep_state==0
                except:
                    pass


            else: #좌측 자극 시작 후 0.5초임
                if keep_state == 0:
                    keep_state = 1  # 좌측 자극이 우측 자극보다 먼저 나왔음
                try:
                    linelist = rawfile.readlines(-1)
                    split_fp1 = []
                    for i in linelist:  # fp1신호만 불러오기
                        split_fp1.append(float(i.split('\t')[1]))

                    lenlist = len(split_fp1)  # list 길이
                    split_time = split_fp1[int(lenlist * 0.4):]  # 0.3~0.5초 구간

                    if max(split_time) > ref_list[user_num][0]:  # ERP 기준 넘음
                        if keep_state == 1:  # 좌측 자극 먼저 나온 상태이면
                            keep_state = 3  # 좌측 ERP 상승한상태, 우측은 아직 검사X
                        elif keep_state == 2:  # 우측자극 먼저 나왔지만 우측은 상승하지 않음
                            keep_state = 5  # 오른쪽으로 이동
                        elif keep_state == 4:  # 우측자극 먼저 나왔고 우측 ERP 상승한 상태
                            keep_state = 6  # 좌/우 모두 ERP 나온 경우 오른쪽으로 이동

                    else:
                        if keep_state==2: #우측 자극 먼저 검사했을때 상승 안되었었는데, 좌측 자극에서도 상승 X
                            keep_state==0
                except:
                    pass

        # 이동
        inputkey = 0  # 두칸씩 움직일때 있어서 방지용
        if (erp_state_12 == 3 or keep_state == 5) and inputkey == 0:  # 쥐 왼쪽으로 이동
            mouseX = -setloc  # 180
            inputkey += 1
            erp_state_12 = 0
            keep_state = 0

        elif (erp_state_17 == 3 or keep_state == 6) and inputkey == 0:  # 쥐 오른쪽으로 이동
            mouseX = setloc  # 180
            inputkey += 1
            erp_state_17 = 0
            keep_state = 0

        drawObject(background, 0, 0)  # 배경 화면 그리기

        # 쥐 위치 재조정
        if inputkey == 1:
            x += mouseX
        if x < setloc * 3 - mouseWidth / 2:
            x = setloc * 3 - mouseWidth / 2
        elif x > setloc * 5 - mouseWidth / 2:
            x = setloc * 5 - mouseWidth / 2

        # 쥐가 고양이와 충돌했는지 체크
        if y < catY + catHeight:
            if (x < catX < x + mouseWidth) or \
                    (catX + catWidth > x and catX + catX + catWidth < x + mouseWidth):
                crash()

        if ERP_count == 0:  # 초기 자동발사
            cheeseXY.append([x, y])

        # 치즈 발사 화면에 그리기
        if len(cheeseXY) != 0:
            for i, bxy in enumerate(cheeseXY):  # 치즈에 대해 반복함(자동발사)
                bxy[1] -= 30  # 총알(치즈)의 y 좌표 -30 (위로 이동)
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

                if bxy[1] <= 0:  # 치즈가 화면 밖을 벗어나면
                    try:
                        cheeseXY.remove(bxy)  # 치즈 제거
                        cheeseX = x
                        cheeseY = y + mouseHeight
                        cheeseXY.append([cheeseX, cheeseY])
                    except:
                        pass

        if shotCount >= 20:  # 고양이 20마리 이상 때리면
            pygame.mixer.music.stop()  # 배경 음악 정지
            return 0  # 종료

        if len(cheeseXY) != 0:
            for bx, by in cheeseXY:
                drawObject(cheese, bx, by)

        drawObject(mouse, x, y)  # 쥐를 게임 회면의 (x, y) 좌표에 그리기

        writeScore(shotCount)
        catY += catSpeed  # 고양이가 아래로 움직임

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
        if 3 >= catPassed >= 1:  # 고양이 3개 놓치면 게임오버
            life[catPassed - 1] = life_off

        if catPassed == 3:  # 고양이 3개 놓치면 게임오버
            gameOver()
            return -1  # 게임오버

        # 놓친 고양이 수 표시
        life[0] = pygame.transform.scale(life[0], (35, 30))
        life[1] = pygame.transform.scale(life[1], (35, 30))
        life[2] = pygame.transform.scale(life[2], (35, 30))
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
        if bomb < 3:
            drawObject(explosion, bombX - padWidth // 24, bombY)
            bomb += 1

        # -------------------------------------------
        # SSVEP 자극 띄우기 12
        if SSVEP_count % 5 == 0 and SSVEP_count % 10 != 0:
            SSVEP_color12 = color[0]  # 검
        elif SSVEP_count % 10 == 0:  # 5에는 아니고 10만
            SSVEP_color12 = color[1]  # 흰
        pygame.draw.rect(gameScreen, SSVEP_color12,
                         [int(setloc * 0.5), int(padHeight - setloc * 1.5), int(setloc * 1.5),
                          int(setloc * 1.5)])  # SSVEP 12 그리기

        # SSVEP 자극 띄우기 17
        if SSVEP_count % 4 == 0 and SSVEP_count % 7 != 0:
            SSVEP_color17 = color[0]
        elif SSVEP_count % 7 == 0:  # 5에는 아니고 10만
            SSVEP_color17 = color[1]
        pygame.draw.rect(gameScreen, SSVEP_color17,
                         [int(padWidth - setloc * 2), int(padHeight - setloc * 1.5), int(setloc * 1.5),
                          int(setloc * 1.5)])  # SSVEP 12 그리기

        # ERP 띄우기
        if 0 <= ERP_count % 60 < 30:  # 번갈아가면서 깜빡임
            # ERP 띄우기 왼쪽 삼각형
            if SSVEP_color12 == color[0]:  # 검은색이면
                ERP_color_L = color[2]  # 노란색
            else:  # 흰색이면
                ERP_color_L = color[3]  # 파란색
            pygame.draw.polygon(gameScreen, ERP_color_L, [[setloc * 1.625 * 0.6, padHeight - setloc * 1.25 * 0.6],
                                                          [setloc * 2.375 * 0.6, padHeight - setloc * 0.75 * 0.6],
                                                          [setloc * 2.375 * 0.6, padHeight - setloc * 1.75 * 0.6]])

        elif 30 <= ERP_count % 60 < 60:  # 번갈아가면서 깜빡임
            # ERP 띄우기 오른쪽 삼각형
            if SSVEP_color17 == color[0]:  # 검은색이면
                ERP_color_R = color[2]  # 노란색
            else:  # 흰색이면
                ERP_color_R = color[3]  # 파란색
            pygame.draw.polygon(gameScreen, ERP_color_R,
                                [[padWidth - setloc * 1.625 * 0.6, padHeight - setloc * 1.25 * 0.6],
                                 [padWidth - setloc * 2.375 * 0.6, padHeight - setloc * 0.75 * 0.6],
                                 [padWidth - setloc * 2.375 * 0.6, padHeight - setloc * 1.75 * 0.6]])

        SSVEP_count += 1
        ERP_count += 1

        pygame.display.update()  # 게임화면을 다시그림
        clock.tick(60)  # 게임화면의 초당 프레임수를 60으로 설정


# ------------------------------------------------------------------------------------------------------------
def gameOverImage():
    finishGame = False
    gameover = pygame.image.load("./resources/lose.png")  # 배경 그림
    gameover = pygame.transform.scale(gameover, (padWidth, padHeight))
    drawObject(gameover, 0, 0)
    oversound = pygame.mixer.Sound('./resources/실패_효과음.mp3')
    oversound.play()  # 책 넘기는 소리 재생
    while not finishGame:
        pygame.display.update()  # 게임화면을 다시그림
        clock.tick(60)

        font_small = pygame.font.Font("./resources/neodgm_pro.ttf", 30)
        announcement1 = font_small.render('<enter>를 누르면 게임을 다시 시작합니다', True, (255, 0, 0))
        announcement2= font_small.render('<space>를 누르면 게임을 종료합니다', True, (255, 0, 0))
        # 가운데정렬
        rect1 = announcement1.get_rect()
        rect1.center = [padWidth / 2, padHeight - 65]
        gameScreen.blit(announcement1, rect1)
        rect2 = announcement2.get_rect()
        rect2.center = [padWidth / 2, padHeight - 35]
        gameScreen.blit(announcement2, rect2)


        for event in pygame.event.get():
            if event.type in [pygame.KEYDOWN]:
                if event.key == pygame.K_SPACE:
                    pygame.quit()  # space 누르면 pygame 종료
                    sys.exit()

                elif event.key == 13:  # 엔터 누르면 중립측정 단계 없이 다시 게임 시작
                    playGame()


# ------------------------------------------------------------------------------------------------------------
def winImage():
    finishGame = False
    winimg = pygame.image.load("./resources/win.png")  # 배경 그림
    winimg = pygame.transform.scale(winimg, (padWidth, padHeight))
    drawObject(winimg, 0, 0)
    winsound = pygame.mixer.Sound('./resources/이겼을때효과음_볼륨up.mp3')
    winsound.play()  # 책 넘기는 소리 재생
    while not finishGame:
        pygame.display.update()  # 게임화면을 다시그림
        clock.tick(60)

        font_small = pygame.font.Font("./resources/neodgm_pro.ttf", 30)
        announcement1 = font_small.render('<enter>를 누르면 게임을 다시 시작합니다', True, (255, 0, 0))
        announcement2= font_small.render('<space>를 누르면 게임을 종료합니다', True, (255, 0, 0))
        # 가운데정렬
        rect1 = announcement1.get_rect()
        rect1.center = [padWidth / 2, padHeight - 65]
        gameScreen.blit(announcement1, rect1)
        rect2 = announcement2.get_rect()
        rect2.center = [padWidth / 2, padHeight - 35]
        gameScreen.blit(announcement2, rect2)


        for event in pygame.event.get():
            if event.type in [pygame.KEYDOWN]:
                if event.key == pygame.K_SPACE:
                    pygame.quit()  # space 누르면 pygame 종료
                    sys.exit()

                elif event.key == 13:  # 엔터 누르면 중립측정 단계 없이 다시 게임 시작
                    winsound.stop()
                    playGame()


# ------------------------------------------------------------------------------------------------------------
def playGame():
    finish = runGame()

    if finish == -1:  # 게임오버되면
        gameOverImage()

    else:  # 10마리 퇴치
        winImage()

    return


# 실행
initGame()
prolog()
playGame()
