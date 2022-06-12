import cv2
import mediapipe as mp
import time
import numpy as np


##############################################################################################
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

#Detects whether a finger is up or down
thumb = False
indexFinger = False
middleFinger = False
ringFinger = False
pinkyFinger = False

#Start values to draw a line from
Xstart = 0
Ystart = 0

#Creates a canvas to draw on
blank_image = np. zeros(shape=[480, 640, 3], dtype=np. uint8)
##############################################################################################




# For webcam input:
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.7)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)


while cap.isOpened():
  success, image = cap.read()
  if not success:
    break
  start_time = time.time()

  # Flip the image horizontally for a later selfie-view display, and convert
  # the BGR image to RGB.
  image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

  # To improve performance, optionally mark the image as not writeable to
  # pass by reference.
  image.flags.writeable = False
  results = hands.process(image)

  # Draw the hand annotations on the image.
  image.flags.writeable = True
  image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
  

  if results.multi_hand_landmarks:
    #Finds the X and Y coordinates of any point on the hand
    ###################################################################################################
    # TODO: reduce function declaration redundancies.
    def find_all(a_str, sub):
      start = 0
      while True:
          start = a_str.find(sub, start)
          if start == -1: return
          yield start
          start += len(sub) # use start += 1 to find overlapping matches

    def X(num):
      for hand_landmarks in results.multi_hand_landmarks:
        s = str(hand_landmarks)
        arr = list(find_all(s, 'x'))
        return float(s[arr[num]+3:arr[num]+10])

    def Y(num):
      for hand_landmarks in results.multi_hand_landmarks:
        s = str(hand_landmarks)
        arr = list(find_all(s, ' y:'))
        return float(s[arr[num]+4:arr[num]+11])

    def Z(num):
      for hand_landmarks in results.multi_hand_landmarks:
        s = str(hand_landmarks)
        arr = list(find_all(s, ' z:'))
        # TODO: Check if this is right. I assumed it was like this based on the two functions above.
        #  So far I think it is working.
        return float(s[arr[num]+5:arr[num]+12])
    ###################################################################################################

    #Detects weather a finger is up or down
    ###################################################################################################
    # TODO: Redundant detects of thumb, ring finger, pinky.

    centerPoint = Y(2) # TODO: Redundant
    if Y(4)<Y(17):
      thumb = True
    else:
      thumb = False

    # Detects if index finger is pointing upwards.
    centerPoint = Y(6)
    if Y(7)<centerPoint and Y(8)<centerPoint:
      indexFinger = True
    else:
      indexFinger = False

    centerPoint = Y(10)
    if Y(11)<centerPoint and Y(12)<centerPoint:
      middleFinger = True
    else:
      middleFinger = False

    centerPoint = Y(14)
    if Y(15)<centerPoint and Y(16)<centerPoint:
      ringFinger = True
    else:
      ringFinger = False

    centerPoint = Y(18)
    if Y(19)<centerPoint and Y(20)<centerPoint:
      pinkyFinger = True
    else:
      pinkyFinger = False
    ###################################################################################################

    #Drawing
    ###################################################################################################
    # TODO: better to define dimensions before creating image.
    height, width, _ = image.shape
    #TODO: change colour
    draw_color = (0, 0, 255) # Red
    wait_color = (255, 0, 255) # Magenta
    CURSOR_THICKNESS = 15

    if indexFinger and not middleFinger:

      #Draws the cursor on the screen
      cv2.circle(image, (int(X(8) * width), int(Y(8) * height)), CURSOR_THICKNESS, draw_color, cv2.FILLED)
      # TODO: line gets too thick suddenly making a 'blob'
      line_thickness = round(Z(8) * 100)
      if Xstart == 0 and Ystart == 0:
        cv2.circle(blank_image, (int(X(8) * width), int(Y(8) * height)), int(line_thickness/2), draw_color, cv2.FILLED)
      else:
        #Draws a line from the start point to the end point
        cv2.line(blank_image, (int(X(8) * width), int(Y(8) * height)),(Xstart,Ystart), draw_color, line_thickness, cv2.FILLED)
      
      #Sets the start point to the current point
      Xstart = int(X(8) * width)
      Ystart = int(Y(8) * height)

      print("Draw")
    else:
      cv2.circle(image, (int(X(8) * width), int(Y(8) * height)), CURSOR_THICKNESS, wait_color, cv2.FILLED)

      Xstart = 0
      Ystart = 0
      
      print("Middle Finger")
    ###################################################################################################

    
    #Drawing the landmarks on the image
    ###################################################################################################
    # for hand_landmarks in results.multi_hand_landmarks:
    #   mp_drawing.draw_landmarks(
    #       image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    ###################################################################################################

  #Puts the fps on the image
  ###################################################################################################
  #cv2.putText(image, "FPS: " + str(round(1.0 / (time.time() - start_time), 0)), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
  ###################################################################################################

  # Combine the original image with the overlay image. (Honestly this is magic.)
  ###################################################################################################
  GrayImage = cv2.cvtColor(blank_image, cv2.COLOR_RGB2GRAY)
  _, invertedImage = cv2.threshold(GrayImage, 0, 255, cv2.THRESH_BINARY_INV)
  invertedImage = cv2.cvtColor(invertedImage, cv2.COLOR_GRAY2RGB)
  image = cv2.bitwise_and(image, invertedImage)
  image = cv2.bitwise_or(image, blank_image)
  ###################################################################################################

  # Display the image.
  ####################################################################################################
  cv2.imshow('Hello', image)
  cv2.imshow('Blank', blank_image)
  #######################################################################################################

  if cv2.waitKey(5) & 0xFF == 27:
    break
hands.close()
cap.release()

