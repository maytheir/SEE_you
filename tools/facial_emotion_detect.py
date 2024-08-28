import torch
import cv2
import numpy as np
from models.common import DetectMultiBackend
from utils.general import non_max_suppression
import pathlib
import threading
pathlib.PosixPath = pathlib.WindowsPath
import json
import os

class FER:

    def __init__(self):
        json_path = os.path.dirname( os.path.abspath( __file__ ) )
        json_path = os.path.dirname(json_path)
        with open(os.path.join(json_path, ("params.json")), 'r') as fp :
            params = json.load(fp)

        params = params["yolo"]
        user_yolov5_pt_file = params["yolov5_model_path"]
        self.current_emotion = ""

        self.camera_active = True
        self.weights = user_yolov5_pt_file
        self.device = 'cpu'
        self.model = DetectMultiBackend(self.weights, device=self.device)  # 수정된 변수명
        self.stride = self.model.stride
        self.names = self.model.names
        self.pt = self.model.pt

    # Function to detect emotion from the face image
    def detect_emotion(self, img, img_size=416):
        # Preprocess image
        img0, img = self.preprocess_image(img, img_size)

        # Model inference
        pred = self.model(img, augment=False, visualize=False)

        # NMS (Non-Maximum Suppression)
        conf_thres = 0.25
        iou_thres = 0.45
        pred = non_max_suppression(pred, conf_thres, iou_thres, max_det=1000)

        # Process results
        results = []
        for i, det in enumerate(pred):
            if len(det):
                det[:, :4] = self.scale_coords(img.shape[2:], det[:, :4], img0.shape).round()
                for *xyxy, conf, cls in det:
                    results.append({
                        'bbox': xyxy,
                        'confidence': conf.item(),
                        'class': self.names[int(cls)]
                    })

        if results:
            return results[0]['class']  # Return the class of the first detected emotion
        else:
            return "No Emotion Detected"

    def scale_coords(self, img1_shape, coords, img0_shape, ratio_pad=None):
        if ratio_pad is None:
            gain = min(img1_shape[0] / img0_shape[0], img1_shape[1] / img0_shape[1])
            pad = (img1_shape[1] - img0_shape[1] * gain) / 2, (img1_shape[0] - img0_shape[0] * gain) / 2
        else:
            gain = ratio_pad[0][0]
            pad = ratio_pad[1]

        coords[:, [0, 2]] -= pad[0]
        coords[:, [1, 3]] -= pad[1]
        coords[:, :4] /= gain
        coords[:, :4].clamp_(0, max(img0_shape[:2]))  # 최대값을 img0_shape의 height, width로 지정
        return coords

    # 이미지 전처리 함수
    def preprocess_image(self, img, img_size=416):
        img0 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # OpenCV 이미지를 RGB 형식으로 변환
        img = cv2.resize(img0, (img_size, img_size))  # 이미지를 416x416 크기로 리사이즈
        img = img.transpose((2, 0, 1))  # HWC에서 CHW로 변환
        img = np.ascontiguousarray(img)  # 연속된 배열로 변환
        img = torch.from_numpy(img).to(self.device)  # numpy 배열을 텐서로 변환하고 지정된 장치로 이동
        img = img.float()  # 텐서를 float 형식으로 변환
        img /= 255.0  # 0~255에서 0.0~1.0으로 정규화
        if img.ndimension() == 3:
            img = img.unsqueeze(0)  # 배치 차원을 추가
        return img0, img
    
    def detect_faces_from_webcam(self, cascade_path='models/haarcascade_frontalface_default.xml'):
        face_cascade = cv2.CascadeClassifier(cascade_path)
        cap = cv2.VideoCapture(0)

        emotion_count = {}

        while self.camera_active:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                face = frame[y:y+h, x:x+w]
                emotion_class = self.detect_emotion(face)

                if emotion_class in emotion_count:
                    emotion_count[emotion_class] += 1
                else:
                    emotion_count[emotion_class] = 1
                
        cap.release()

        # 가장 많이 감지된 감정 값을 설정
        if emotion_count:
            self.current_emotion = max(emotion_count, key=emotion_count.get)
            # os.environ['current_emotion'] = current_emotion
    
    def start_camera(self):
        self.camera_active = True
        self.camera_thread = threading.Thread(target=self.detect_faces_from_webcam)
        self.camera_thread.start()

    def stop_camera(self):
        self.camera_active = False
        if self.camera_thread:
            self.camera_thread.join()

        return self.current_emotion