import cv2
import matplotlib.pyplot as plt
import time
import handTrackingModule_TES as htm
from enum import Enum
import random
import copy as cp

#DebugMode = True
DebugMode = False

# VARIABILI GLOBALI -----------------------------------------
wCam, hCam = 1280, 720
tipIds = [4, 8, 12, 16, 20] #polpastrelli
currentGesture = -1 # -1 default, 0 sasso, 1 carta, 2 forbice
gameResult = -1

# CARICAMENTO IMMAGINI --------------------------------------
menuImg = cv2.imread("img/menuImg.png")
menuImg = cv2.resize(menuImg, (1280, 720))

tutorialImg = cv2.imread("img/TutorialLayout.png")
tutorialImg = cv2.resize(tutorialImg, (1280, 720))

resultVittoriaImg = cv2.imread("img/Vittoria.png")
resultVittoriaImg= cv2.resize(resultVittoriaImg, (1280, 720))
resultSconfittaImg = cv2.imread("img/Sconfitta.png")
resultSconfittaImg= cv2.resize(resultSconfittaImg, (1280, 720))
resultPareggioImg = cv2.imread("img/Pareggio.png")
resultPareggioImg= cv2.resize(resultPareggioImg, (1280, 720))
resultMossaNonValidaImg = cv2.imread("img/MossaNonValida.png")
resultMossaNonValidaImg= cv2.resize(resultMossaNonValidaImg, (1280, 720))

cartaImg = cv2.imread("img/cartaa.png")
sassoImg = cv2.imread("img/sassoo.png")
forbiceImg = cv2.imread("img/forbice.png")

# GAME STATE --------------------------------------------------
class State(Enum):
    _Menu = 1
    _Game = 2
    _Result = 3
    _Tutorial = 4

currentState = State._Tutorial

# BoundingBox -------------------------------------------------
startPointButtonStart = (35, 25)
endPointButtonStart = (385, 280)

startPointButtonExit = (80, 370)
endPointButtonExit = (315, 430)

startPointButtonTutorial = (1115, 65)
endPointButtonTutorial = (1208, 155)

startPointButtonContinue = (440, 30)
endPointButtonContinue = (825, 135)

"""FINGERS 4 ELEMENTI INDICE-MEDIO-ANULARE-MIGNOLO
   ID NOCCHE = 5 9 13 17
   LM LIST : [id, cx, cy], ...-> es) [[0, 435, 591], [1, 491, 618], ...]
   TIPID : tipIds = [4, 8, 12, 16, 20] #polpastrelli
   FINGERS : [0,1,0,1] - si aggiorna ad ogni grab_frame() -> 1 su, 0 giù : relativi alle dita = 8, 12, 16, 20"""

def gestureDetection(lmList, img, cap):
    global currentState
    global tTime, cTime, pTime
    global playerChoice, pcChoice, gameResult
    global screenShot

    cState = currentState

    if len(lmList) != 0:
        fingers = []
        # rilevo mano orientata verso l'ALTO (nocca sopra polsa)
        if lmList[9][2] < lmList[0][2]:
            #rilevo dito aperto/chiuso (riempio fingers[])
            for id in range(1, 5):
                if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)

        # rilevo mano orientata verso l'BASSO (nocca sotto polso)
        else:
            #rilevo dito aperto/chiuso (riempio fingers[])
            for id in range(1, 5):
                if lmList[tipIds[id]][2] > lmList[tipIds[id] - 2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)
            #orientation = "basso"

        # CHECK STATE--------quando cambio stato-----------
        if currentState == State._Menu:
            x1, y1 = lmList[tipIds[1]][1:]
            x2, y2 = lmList[tipIds[2]][1:]
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            if fingers[0] and fingers[1]:
                # indice su riquadro rosso=Start
                if cy < endPointButtonStart[1]:
                    if startPointButtonStart[0] < cx < endPointButtonStart[0]:
                        cTime = 0
                        pTime = 0
                        tTime = 0
                        cState = State._Game
                if cy < endPointButtonTutorial[1]:
                    if startPointButtonTutorial[0] < cx < endPointButtonTutorial[0]:
                        cTime = 0
                        pTime = 0
                        tTime = 0
                        cState = State._Tutorial
                if startPointButtonExit[1] < cy < endPointButtonExit[1]:
                    if startPointButtonExit[0] < cx < endPointButtonExit[0]:
                        cTime = 0
                        pTime = 0
                        tTime = 0
                        cap.release()

        elif currentState == State._Game:
            if tTime > 3:
                if DebugMode:
                    print("scatto uno screenshot !")
                screenShot = img

                if fingers[0] == 0 and fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0:
                    currentGesture = 0 # sasso
                elif fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1:
                    currentGesture = 1 # carta
                elif fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0:
                    currentGesture = 2 # forbice
                else:
                    currentGesture = -1

                tTime = 0
                playerChoice = currentGesture
                pcChoice = random.randint(0, 2)
                cTime = 0
                pTime = 0
                tTime = 0

                cState = State._Result
        elif currentState == State._Result:
            if tTime == 0:
                if DebugMode:
                    print("player: ", playerChoice)
                    print("pc: ", pcChoice)
                if playerChoice != -1:
                    if playerChoice == pcChoice:
                        if DebugMode:
                            print("PAREGGIO")
                        gameResult = 0
                    elif playerChoice == 0 and pcChoice == 2 or playerChoice == 1 and pcChoice == 0 or playerChoice == 2 and pcChoice == 1:
                        if DebugMode:
                            print("HAI VINTO")
                        gameResult = 1
                    else:
                        if DebugMode:
                            print("HAI PERSO")
                        gameResult = 2
                else:
                    gameResult = 3

            if tTime > 3:
                cState = State._Menu
                gameResult = -1

        elif currentState == State._Tutorial:
            x1, y1 = lmList[tipIds[1]][1:]
            x2, y2 = lmList[tipIds[2]][1:]
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            if fingers[0] and fingers[1]:
                # indice su riquadro rosso=Start
                if startPointButtonContinue[1] < cy < endPointButtonContinue[1]:
                    if startPointButtonContinue[0] < cx < endPointButtonContinue[0]:
                        cTime = 0
                        pTime = 0
                        tTime = 0
                        cState = State._Menu

        currentState = cState


def grab_frame(cap, detector):
    global tTime, cTime, pTime

    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    frameCopy = cp.copy(frame)

    img = detector.findHands(frame, DebugMode)
    lmList = detector.findPosition(img, 0, DebugMode) #draw=False
    gestureDetection(lmList, img, cap)

    # UPDATE STATE-------------------------------------------------
    if currentState == State._Menu:
        add_immagineMenu(img)
        if len(lmList) != 0:
            x1, y1 = lmList[tipIds[1]][1:]
            x2, y2 = lmList[tipIds[2]][1:]
            cx, cy = (x1+x2) // 2, (y1+y2) // 2
            if abs(x2-x1) <= 90 and abs(y2-y1) <= 110:
                cv2.circle(img, (cx, cy), 40, (0, 255, 0), cv2.FILLED)

        if DebugMode:
            print("Menu State")
            menuDebugVisualization(img)

    elif currentState == State._Game:
        if len(lmList) == 0:
            cTime = 0
            pTime = 0
            tTime = 0

        cTime = time.time()
        if pTime == 0:
            pTime = cTime
        tTime = tTime + (cTime - pTime)
        pTime = cTime

        add_immagineGame(img, tTime)

        if DebugMode:
            print("Game State")

    elif currentState == State._Result:
        if gameResult != -1:
            add_immagineResult(img, gameResult, pcChoice)

            cTime = time.time()
            if pTime == 0:
                pTime = cTime
            tTime = tTime + (cTime - pTime)
            pTime = cTime

        if DebugMode:
            print("Result State")

    elif currentState == State._Tutorial:
        add_immagineTutorial(img, frameCopy)

        if len(lmList) != 0:
            x1, y1 = lmList[tipIds[1]][1:]
            x2, y2 = lmList[tipIds[2]][1:]
            cx, cy = (x1+x2) // 2, (y1+y2) // 2
            if abs(x2-x1) <= 90 and abs(y2-y1) <= 110:
                cv2.circle(img, (cx, cy), 40, (0, 255, 0), cv2.FILLED)

        if DebugMode:
            print("Tutorial State")
            tutorialDebugVisualization(img)

    if len(lmList) == 0:
        add_manoNonRilevata(img)

    return img


def menuDebugVisualization(img):
    cv2.rectangle(img, startPointButtonStart, endPointButtonStart, (0, 0, 255), 5, cv2.LINE_AA)
    cv2.rectangle(img, startPointButtonExit, endPointButtonExit, (0, 0, 255), 5, cv2.LINE_AA)
    cv2.rectangle(img, startPointButtonTutorial, endPointButtonTutorial, (0, 0, 255), 5, cv2.LINE_AA)
    cv2.putText(img, 'START GAME', (450, 160), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 0, 255), 5, cv2.LINE_AA)

def tutorialDebugVisualization(img):
    cv2.rectangle(img, startPointButtonContinue, endPointButtonContinue, (0, 0, 255), 5, cv2.LINE_AA)

def handle_close(event, cap):
    """
    Handle the close event of the Matplotlib window by closing the camera capture
    :param event: the close event
    :param cap: the VideoCapture object to be closed
    """
    cap.release()

def bgr_to_gray(image):
    """
    Convert a BGR image into grayscale
    :param image: the BGR image
    :return: the same image but in grayscale
    """
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def bgr_to_rgb(image):
    """
    Convert a BGR image into grayscale
    :param image: the RGB image
    :return: the same image but in RGB
    """
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def add_immagineGame(img, tTime):
    cv2.circle(img, (640, 360), 180, (0, 255, 0), 15)
    textsize = cv2.getTextSize(str(int(tTime)), cv2.FONT_HERSHEY_DUPLEX, 10, 10)
    textX = int(wCam / 2 - (int(textsize[0][0]) / 2))
    textY = int(hCam / 2 + (int(textsize[0][1]) / 2))
    cv2.putText(img, str(int(3 - tTime + 0.99)), (textX, textY), cv2.FONT_HERSHEY_TRIPLEX, 10, (0, 255, 0), 10)

def add_immagineMenu(frame):
    cv2.addWeighted(frame, 0, menuImg, 1, 0.0, frame)
    return frame

def add_immagineResult(frame, gameResult, pcChoice):
    if gameResult == 0:
        cv2.addWeighted(frame, 0, resultPareggioImg, 1, 0.0, frame)
    elif gameResult == 1:
        cv2.addWeighted(frame, 0, resultVittoriaImg, 1, 0.0, frame)
    elif gameResult == 2:
        cv2.addWeighted(frame, 0, resultSconfittaImg, 1, 0.0, frame)
    elif gameResult == 3:
        cv2.addWeighted(frame, 0, resultMossaNonValidaImg, 1, 0.0, frame)

    if pcChoice == 0:
        pc = sassoImg
    elif pcChoice == 1:
        pc = cartaImg
    elif pcChoice == 2:
        pc = forbiceImg

    if gameResult != 3:
        frame[40:255, 472:795] = cv2.resize(pc, (323, 215))
    frame[455:672, 472:800] = cv2.resize(screenShot, (328, 217))

def add_immagineTutorial(frame, frameCopy):
    cv2.addWeighted(frame, 0, tutorialImg, 1, 0.0, frame)
    frame[0:180, 0:320] = cv2.resize(frameCopy, (320, 180))
    return frame

def add_manoNonRilevata(img):
    textsize = cv2.getTextSize(str("Mano non rilevata"), cv2.FONT_HERSHEY_TRIPLEX, 3, 3)
    textX = int(wCam / 2 - (int(textsize[0][0]) / 2))
    textY = int(hCam - (int(textsize[0][1]) / 2))
    cv2.putText(img, "Mano non rilevata", (textX, textY), cv2.FONT_HERSHEY_TRIPLEX, 3, (226, 43, 138), 3)

def main():

    if DebugMode:
        #FPS
        pTimeFps = 0
        cTimeFps = 0

    # init the camera
    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)

    # enable Matplotlib interactive mode
    plt.ion()

    # create a figure to be updated
    fig = plt.figure()
    fig.canvas.mpl_connect("close_event", lambda event: handle_close(event, cap))

    # prep a variable for the first run
    ax_img = None

    detector = htm.handDetector()

    while cap.isOpened():
        if DebugMode:
            # FPS
            cTimeFps = time.time()
            fps = 1 / (cTimeFps - pTimeFps)
            pTimeFps = cTimeFps
        # get the current frame
        frame = grab_frame(cap, detector)

        if ax_img is None:
            if DebugMode:
                cv2.putText(frame, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

            # convert the current (first) frame in grayscale
            ax_img = plt.imshow(bgr_to_rgb(frame))
            plt.axis("off")  # hide axis, ticks, ...
            if DebugMode:
                plt.title("Morra Cinese Debug")
            else:
                plt.title("Morra Cinese")
            # possibile implementazione FULL-SCREEN:
            #if not DebugMode:
                #figManager = plt.get_current_fig_manager()
                #figManager.full_screen_toggle()
                #figManager.canvas.toolbar.pack_forget()

            # show the plot!
            plt.show()
        else:
            if DebugMode:
                #FPS
                cTimeFps = time.time()
                fps = 1 / (cTimeFps - pTimeFps)
                pTimeFps = cTimeFps
                cv2.putText(frame, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
            # set the current frame as the data to show
            ax_img.set_data(bgr_to_rgb(frame))
            plt.pause(1/30)  # pause: 30 frames per second

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit(0)
