from cvzone.HandTrackingModule import HandDetector
import cv2
import autopy
import numpy as np
import time
import pyautogui

#TO Ignore Warnings:

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import logging
logging.getLogger('absl').setLevel(logging.ERROR)


wCam, hCam = 640, 480

frameR = 50

smoothening = 4

plocX, plocY = 0, 0
clocX, clocY = 0, 0

cap = cv2.VideoCapture(0)
cap.set(3,wCam)
cap.set(4,hCam)


detector = HandDetector(maxHands=1, detectionCon=0.8)

wScr, hScr = autopy.screen.size()


lastClick = 0
clickDelay = 0.25

while True:
    success, img = cap.read()
    hands, img = detector.findHands(img)

    if hands:
        hand = hands[0]
        lmList = hand["lmList"]
        fingers = detector.fingersUp(hand)

        x1, y1 = lmList[8][0], lmList[8][1]      # Index
        xM, yM = lmList[12][0], lmList[12][1]    # Middle
        xT, yT = lmList[4][0], lmList[4][1]      # Thumb
        xP, yP = lmList[20][0], lmList[20][1]    # Pinky

        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),
                      (255, 0, 255), 2)

        print(fingers)

        # -------------------  MOVE MODE  -------------------
        if fingers[1] == 1 and fingers[2] == 0:
            # Convert coordinates inside frame
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

            # Smooth the values
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            autopy.mouse.move(wScr - clocX, clocY)

            plocX, plocY = clocX, clocY

        # ------------------- LEFT CLICK (Pinch) -------------------
        if fingers[1] == 1 and fingers[2] == 1:
            p1 = (lmList[8][0], lmList[8][1])
            p2 = (lmList[12][0], lmList[12][1])

            length, info, img = detector.findDistance(p1, p2, img)
            if length < 40 and (time.time() - lastClick) > clickDelay:
                autopy.mouse.click()
                lastClick = time.time()

        # ------------------- RIGHT CLICK -------------------
        # Thumb + Middle pinch
        if fingers[0] == 1 and fingers[2] == 1 and fingers[1] == 0:
            p1 = (xT, yT)
            p2 = (xM, yM)
            length, info, img = detector.findDistance(p1, p2, img)

            if length < 40 and (time.time() - lastClick) > clickDelay:
                autopy.mouse.click(button=autopy.mouse.Button.RIGHT)
                lastClick = time.time()

        # ------------------- SCROLLING (PINKY) -------------------
        if fingers[4] == 1:  # Pinky up
            dy = yP - (hCam // 2)

            if dy < -40:
                pyautogui.scroll(50)      # scroll up
            elif dy > 40:
                pyautogui.scroll(-50)     # scroll down


    cv2.imshow("Virtual Mouse", img)
    cv2.waitKey(1)