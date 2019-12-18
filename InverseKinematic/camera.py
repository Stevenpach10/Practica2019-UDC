import cv2
import matplotlib.pyplot as plt
import time
camera = cv2.VideoCapture(0)
return_value, image = camera.read()
cv2.imshow('image',image)
cv2.waitKey(1000)
cv2.destroyAllWindows()
del(camera)

