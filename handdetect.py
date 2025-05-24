
import cv2
import mediapipe as mp
import threading
import time

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

class HandController:
    def __init__(self):
        self.current_max_handle = 8
        self.hands = mp_hands.Hands(
            max_num_hands=8,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )

    def detect_hand_orientation(self, landmarks):
        return landmarks[4].x < landmarks[20].x  # True = Avuç içi

    def detect_finger_states(self, landmarks):
        fingers = []
        # Başparmak (x ekseni)
        if landmarks[4].x < landmarks[3].x:
            fingers.append("Açık")
        else:
            fingers.append("Kapalı")

        # Diğer parmaklar (y ekseni)
        finger_tips = [8, 12, 16, 20]
        finger_pips = [6, 10, 14, 18]

        for tip, pip in zip(finger_tips, finger_pips):
            if landmarks[tip].y < landmarks[pip].y:
                fingers.append("Açık")
            else:
                fingers.append("Kapalı")
        return fingers

    def is_hand_up(self, hand_landmarks):
        wrist_y = hand_landmarks[0].y  # Bileğin 'y' koordinatını al
        fingertip_ys = [hand_landmarks[i].y for i in [8, 12, 16, 20]]  
        return all(finger_y < wrist_y for finger_y in fingertip_ys)

    def process_frame(self, frame):
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = self.hands.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        return results, image

    def get_right_hand_count(self, results):
        right_hand_count = 0
        if results.multi_handedness:
            for hand_info in results.multi_handedness:
                label = hand_info.classification[0].label
                if label == "Right":
                    right_hand_count += 1
        return right_hand_count

    def analyze_hands(self, frame):
        results, image = self.process_frame(frame)
        right_hands_up = 0
        hand_orientations = []

        if results.multi_hand_landmarks and results.multi_handedness:
            for i, handedness in enumerate(results.multi_handedness): #burayı değiştirdin
                label = handedness.classification[0].label  # "Right" or "Left"
                hand_landmarks = results.multi_hand_landmarks[i]

                if label == "Right" and self.is_hand_up(hand_landmarks.landmark):
                    right_hands_up += 1
                    is_palm = self.detect_hand_orientation(hand_landmarks.landmark)
                    hand_orientations.append({
                        "hand": label,
                        "palm": is_palm
                    })

                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        return right_hands_up, hand_orientations, image


class CameraHandler:
    def __init__(self):
        self.cap = None
        self.thread = None
        self.running = False
        self.frame = None
        self.status = False
        #self.FPS = 1 / 30  # 30 FPS
        self.lock = threading.Lock()  # Frame erişimi için kilit
        self.turn_on_camera()

    def turn_on_camera(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Kamera açılamadı.")
            return False
        print("Kamera açıldı.")
        self.running = True
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()
        return True

    def _update(self):
        while self.running:
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                with self.lock:
                    self.status = ret
                    self.frame = frame
            #time.sleep(self.FPS)

    def read_frame(self):
        with self.lock:
            return self.status, self.frame.copy() if self.frame is not None else None

    def close_camera(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

    def show_frame(self, window_name="Kamera"):
        status, frame = self.read_frame()
        if status and frame is not None:
            cv2.imshow(window_name, frame)
            key = cv2.waitKey(1) & 0xFF
            return key
        return None


class HandGestureTracker(threading.Thread):
    def __init__(self):
        super().__init__()
        self.hand_controller = HandController()
        self.cam = CameraHandler()
        self.frame = None
        self.lock = threading.Lock()  # Frame güncelleme için kilit
        self.running = False
        self.results = None
        self.paused = False
        self.right_hands_up_count = 0
        self.hand_orientations = []
        self.processed_image = None
    
    def run(self):
        while self.running:
        # Kameradan okuma yapan kısmı devre dışı bırak
        # status, frame = self.cam.read_frame()
        # if not status or frame is None:
        #     continue

            frame = None
            with self.lock:
                if self.frame is not None:
                    frame = self.frame.copy()

            if frame is None:
                time.sleep(0.05)
                continue

            if self.paused:
                time.sleep(0.1)
                continue

            right_hands_up, hand_orientations, image = self.hand_controller.analyze_hands(frame)

            with self.lock:
                self.right_hands_up_count = right_hands_up
                self.hand_orientations = hand_orientations
                self.results = (right_hands_up, hand_orientations)
                self.processed_image = image

            time.sleep(0.05)
    
    def set_current_hand_count(self, count):
        with self.lock:
            self.hand_controller.current_max_handle = count


    '''def run(self):
        while self.running:
            status, frame = self.cam.read_frame()
            if not status or frame is None:
                continue

            self.update_frame(frame=frame)
            
            if self.paused:
                time.sleep(0.1)
                continue

            frame = None
            with self.lock:
                if self.frame is not None:
                    frame = self.frame.copy()

            if frame is not None:
                right_hands_up, hand_orientations, image = self.hand_controller.analyze_hands(frame)
                with self.lock:
                    self.right_hands_up_count = right_hands_up
                    self.hand_orientations = hand_orientations
                    self.results = (right_hands_up, hand_orientations)
                    self.processed_image = image

            time.sleep(0.05)  # CPU'yu çok yormamak için kısa uyku'''

    def update_frame(self, frame):
        with self.lock:
            self.frame = frame.copy() if frame is not None else None

    def get_result(self):
        with self.lock:
            return self.results

    def get_processed_image(self):
        with self.lock:
            return self.processed_image

    def pause_processing(self):
        self.paused = True

    def resume_processing(self):
        self.paused = False

    def start_processing(self):
        self.running = True
        self.start()

    def stop_processing(self):
        self.running = False
        self.join()

    def get_right_hands_up_count(self):
        with self.lock:
            return self.right_hands_up_count

    def get_hand_orientations(self):
        with self.lock:
            return self.hand_orientations


