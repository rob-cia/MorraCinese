import cv2
import mediapipe as mp
"""creo classe : 
    - costruttore : parametri di HANDS 
      oggetto creato : fornisco direttamente i parametri dell'utente: mode, maxHands , ecc.
    - metodi : 
              findHands -> trova le mani + disegna i landMarks se flag DRAW è true"""
class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]

    """FINDHANDS -> trova le mani + disegna i landMarks se flag DRAW è true"""
    def findHands(self, img, draw = True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB) #N.B. : Abilita processo riconoscimento MANI , dobbiamo estrarre le mani
        #print(self.results.multi_hand_landmarks)
        """per ogni punto estraggo info (FOR) , HANDLM = punti rossi sulla mano, cordinate x y z.
        cosi disegnamo i punti sulle mani
        usiamo metodo per disegnare linee collegamento punti -> MPDRAW : scriviamo su immagine BGR.
        troviamo 21 LANDMARKS (punti x y z).
        DOBBIAMO PRENDERE LE INFORMAZIONI DAI LANDMARKS"""
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                """usiamo una funzione landmark che estre info dai landmarks: indice ecc.
                   cosi stampiamo coordinate X Y Z; distinguo ID dal landmark completo
                   - x : val decimale in pixels è moltiplicato per high e weight; 
                   lo sistemiamo per avere significato in PIXELS:
                   H, W, C -> identifichiamo shape img 
                   CX, CY -> ogni pixel
                   successivamente disegnamo un circolo attorno al primo landmark (al pixel che lo riguarda)"""
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img


    """FINDPOSITION -> trova pixels associati a handlandmarks + disegna cerchi se trova LANDMARKS
    dopo aver celto mano dx o sx con HANDNO, creo lista per ordinare i landmarks della mano scelta."""
    def findPosition(self, img, handNo = 0, draw=True):
        self.lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                # print(id, lm)
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                # print(id, cx, cy)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
        return self.lmList