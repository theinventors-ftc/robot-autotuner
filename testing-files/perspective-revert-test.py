import cv2 as cv
import numpy as np
from pupil_apriltags import Detector

cap = cv.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

tagsDetected = None
tags = []
detector = Detector(
        families="tag36h11",
        nthreads=1,
        quad_decimate=1.0,
        quad_sigma=0.0,
        refine_edges=1,
        decode_sharpening=0.25,
        debug=0
    )

def detectApriltags(input):
        global tags
        grayscaleImage = cv.cvtColor(input, cv.COLOR_BGR2GRAY)
        tagsDetected = detector.detect(grayscaleImage)

        tempTags = []

        for tag in tagsDetected:
            tempTags.append(tag)

            ptA, ptB, ptC, ptD = tag.corners;

            ptB = (int(ptB[0]), int(ptB[1]))
            ptC = (int(ptC[0]), int(ptC[1]))
            ptD = (int(ptD[0]), int(ptD[1]))
            ptA = (int(ptA[0]), int(ptA[1]))

            cv.line(input, ptA, ptB, (255, 0, 0), 2)
            cv.line(input, ptB, ptC, (255, 0, 0), 2)
            cv.line(input, ptC, ptD, (255, 0, 0), 2)
            cv.line(input, ptD, ptA, (255, 0, 0), 2)

            cv.putText(input, str(tag.tag_id), (ptB[0] + 10, ptB[1] + 15), cv.FONT_HERSHEY_SIMPLEX, 
                   1, (255, 0, 0), 2, cv.LINE_AA)
        
        tags = tempTags

def perspectiveRevert(frame, april1, april2, april3, april4):
    rows, cols, ch = frame.shape

    pts1 = np.float32([april1, april2, april3, april4])
    pts2 = np.float32([[120,120],[int(rows*1.89629629)-120,120],[120, rows-120],[int(rows*1.89629629)-120,rows-120]])

    matrix = cv.getPerspectiveTransform(pts1, pts2)
    result = cv.warpPerspective(frame, matrix, (int(rows*1.89629629), rows))

    return result

while True:
    _, frame = cap.read()

    # Detecting Apriltags
    detectApriltags(frame)
    
    if len(tags) >= 4:
         reverted = perspectiveRevert(frame, tags[0].center, tags[1].center, tags[2].center, tags[3].center)
         cv.imshow("Reverted View", reverted)

    cv.imshow("Raw View", frame) 

    if cv.waitKey(5) & 0xFF == 27:
        break
    
cap.release()
cv.destroyAllWindows()
