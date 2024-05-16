from flask import Flask, render_template, Response, jsonify
import cv2
import numpy as np
import math
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier

app = Flask(__name__)

detector = HandDetector(maxHands=1)
offset = 20
imgSize = 300
classifier = Classifier("E:\Euphelity_pvt_ltd\ML\Web\keras_model.h5", "E:\Euphelity_pvt_ltd\ML\Web\labels.txt")

labels = ["A", "Again", "B", "Bathroom", "C", "Cat", "D", "Dog", "Done", "E", "Eat", "F", "Father", "Fine", "G", "Go to", "H", "Hello", "Help", "How", "I", "J", "K", "L", "Learn", "Like", "M", "Milk", "More", "Mother", "N", "Name", "No", "O", "P", "Please", "Q", "R", "S", "See", "Sign", "T", "Thank you", "U", "V", "W", "Want", "What", "X", "Y", "Yes", "You", "You later", "Z"]

def process_frame(frame):
    imgOutput = frame.copy()
    hands, _ = detector.findHands(frame)
    detected_text = ""
    if hands:
        hand = hands[0]
        x, y, w, h = hand['bbox']

        imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255

        imgCrop = frame[y - offset:y + h + offset, x - offset:x + w + offset]
        imgCropShape = imgCrop.shape

        aspectRatio = h / w

        if aspectRatio > 1:
            k = imgSize / h
            wCal = math.ceil(k * w)
            imgResize = cv2.resize(imgCrop, (wCal, imgSize))
            imgResizeShape = imgResize.shape
            wGap = math.ceil((imgSize - wCal) / 2)
            imgWhite[:, wGap: wCal + wGap] = imgResize
            prediction, index = classifier.getPrediction(imgWhite, draw=False)

        else:
            k = imgSize / w
            hCal = math.ceil(k * h)
            imgResize = cv2.resize(imgCrop, (imgSize, hCal))
            imgResizeShape = imgResize.shape
            hGap = math.ceil((imgSize - hCal) / 2)
            imgWhite[hGap: hCal + hGap, :] = imgResize
            prediction, index = classifier.getPrediction(imgWhite, draw=False)

        detected_text = labels[index]
        cv2.rectangle(imgOutput, (x - offset, y - offset - 70), (x - offset + 400, y - offset + 60 - 50), (0, 255, 0), cv2.FILLED)
        cv2.putText(imgOutput, detected_text, (x, y - 30), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 0), 2)
        cv2.rectangle(imgOutput, (x - offset, y - offset), (x + w + offset, y + h + offset), (0, 255, 0), 4)

    ret, jpeg = cv2.imencode('.jpg', imgOutput)
    return jpeg.tobytes(), detected_text

@app.route('/')
def index():
    return render_template('index.html')

def gen():
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        frame_bytes, detected_text = process_frame(frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        yield (f'data: {detected_text}\n\n').encode()

@app.route('/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detected_text')
def detected_text():
    _, detected_text = process_frame(None)
    return jsonify(detected_text=detected_text)

if __name__ == '__main__':
    app.run(debug=True)
