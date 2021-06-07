from time import sleep
import os
import pygame

BLACK = (0, 0, 0)
padWidth = 960 #1700     # 게임화면 가로크기
padHeight = 540 #1000    # 게임화면 세로크기

mavedir="C:\MAVE_RawData"
file_list=os.listdir(mavedir)
last_file=file_list[-1] #가장 최근의 파일 경로
print('file name: ',last_file)
rawfile=open(mavedir+"/"+last_file+"/"+"Rawdata.txt","r")
fft_file=open(mavedir+"/"+last_file+"/"+"Fp1_FFT.txt","r")

setloc=padWidth//8

def initGame():
    global gamePad, clock, background, padWidth,padHeight
    pygame.init()
    gamePad = pygame.display.set_mode((padWidth, padHeight))
    pygame.display.set_caption("PyShooting")                        # 게임 이름

    clock = pygame.time.Clock()

def drawObject(obj, x, y):
    global gamePad
    gamePad.blit(obj, (x, y))

def runGame():
    global gamePad, clock, background

    onGame = False

    color=[(0,0,0),(255,255,255),(255,255,0),(0,0,255)] #검, 흰,노, 파 #논문을 찾아서 노란색으로 해도 될듯..? 아니면 시각 피로도와 연관지어도 될것가틈
    SSVEP_count=0
    ERP_count=0
    SSVEP_color12= color[0]
    SSVEP_color15=color[0]


    while not onGame:
        print(SSVEP_count)
        pygame.draw.rect(gamePad, BLACK, [0,0, padWidth,padHeight]) #검은화면
        # 자극 띄우기 위한 시간 추적 객체 #ref https://runebook.dev/ko/docs/pygame/ref/time
        SSVEP_clock = pygame.time.get_ticks()
        ERP_clock = pygame.time.get_ticks()

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

        font = pygame.font.Font("./resources/neodgm_pro.ttf", 20)
        text = font.render(str(ERP_count), True, (255, 255, 255))
        gamePad.blit(text, (setloc * 0.3, padHeight / 6 + 30))

        #-------------------------------------------
        #SSVEP 자극 띄우기 12 --> 5*12 -> 12frame
        if SSVEP_count%5==0 and SSVEP_count%10!=0:
            SSVEP_color12=color[0] #검
        elif SSVEP_count%10==0: #5에는 아니고 10만
            SSVEP_color12 =color[1] #흰
        #pygame.draw.rect(gamePad, SSVEP_color12, [0, padHeight-setloc*2.5, setloc*2.5, setloc*2.5]) #SSVEP 12 그리기
        pygame.draw.rect(gamePad, (0,0,0),
                         [0, padHeight - setloc * 2.5, setloc * 2.5, setloc * 2.5])  # SSVEP 12 그리기

        #SSVEP 자극 띄우기 15 --> 4*15 -> 15frame
        if SSVEP_count%4==0 and SSVEP_count%8!=0:
            SSVEP_color15=color[0]
        elif SSVEP_count%8==0: #5에는 아니고 10만
            SSVEP_color15 =color[1]
        #pygame.draw.rect(gamePad, SSVEP_color15, [padWidth-setloc*2.5, padHeight-setloc*2.5, setloc*2.5, setloc*2.5]) #SSVEP 12 그리기
        pygame.draw.rect(gamePad, (0,0,0), [padWidth - setloc * 2.5, padHeight - setloc * 2.5, setloc * 2.5,
                                                  setloc * 2.5])  # SSVEP 12 그리기

        #ERP 띄우기 5-> 12*5 ->5frame.. 너무빠른것같은데 1frame으로바꿔봄 6->30, 12-60 으로 했음
        if 0<=ERP_count%60<30: #번갈아가면서 깜빡임
            ##ERP 띄우기 왼쪽 삼각형
            if SSVEP_color12==color[0]: #검은색이면
                ERP_color_L=color[2] #노란색
            else: #흰색이면
                ERP_color_L = color[2]  # 노란색
                #ERP_color_L=color[3] #파란색
            pygame.draw.polygon(gamePad, ERP_color_L, [[setloc*0.75, padHeight-setloc*1.25], [setloc*1.5, padHeight-setloc*0.75], [setloc*1.5, padHeight-setloc*1.75]])
        elif 30<=ERP_count%60<60: #번갈아가면서 깜빡임
            ##ERP 띄우기 오른쪽 삼각형
            if SSVEP_color15==color[0]: #검은색이면
                ERP_color_R=color[2] #노란색
            else: #흰색이면
                ERP_color_L = color[2]  # 노란색
                #ERP_color_R=color[3] #파란색
            pygame.draw.polygon(gamePad, ERP_color_R, [[padWidth-setloc*0.75, padHeight-setloc*1.25], [padWidth-setloc*1.5, padHeight-setloc*0.75], [padWidth-setloc*1.5, padHeight-setloc*1.75]])


        #중앙에 십자가 띄우기?(봐서 추가하겠음)

        SSVEP_count+=1
        ERP_count+=1



        pygame.display.update()  # 게임화면을 다시그림
        clock.tick(60)                  # 게임화면의 초당 프레임수를 60으로 설정
    pygame.quit()                       # pygame 종료

initGame()
runGame()