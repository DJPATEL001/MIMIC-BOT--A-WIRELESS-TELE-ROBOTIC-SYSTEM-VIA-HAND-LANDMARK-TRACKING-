prev_command = ""
import cv2
import mediapipe as mp
import serial
import time

try:
    ser = serial.Serial('COM8', 115200, write_timeout=0.1)  # change COM port if needed
    time.sleep(2)
except serial.SerialException as e:
    print(f"Warning: Could not open serial port 'COM8'. Running without serial connection. Error: {e}")
    ser = None

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)
mp_draw = mp.solutions.drawing_utils

# Finger tip landmark IDs
finger_tips = [4, 8, 12, 16, 20]

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)
frame_count = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            lm_list = []
            h, w, _ = frame.shape

            for id, lm in enumerate(handLms.landmark):
                lm_list.append((int(lm.x * w), int(lm.y * h)))

            fingers = []

            # Thumb (special case)
            if lm_list[4][0] < lm_list[3][0]:
                fingers.append(1)
            else:
                fingers.append(0)

            # Other fingers
            for tip in finger_tips[1:]:
                if lm_list[tip][1] < lm_list[tip - 2][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)
            # Convert finger states to servo angles
            servo_angles = []

            for state in fingers:
                if state == 1:
                    servo_angles.append(90)   # Finger OPEN
                else:
                    servo_angles.append(0)    # Finger CLOSED
             # ---- WRIST (6th SERVO) SIMULATION ----
            # Using palm tilt (left / center / right)

            wrist_angle = 90  # default (straight)

            # Landmark 5 = index finger base
            # Landmark 17 = little finger base
            if lm_list[5][0] - lm_list[17][0] > 40:
                wrist_angle = 135   # Hand tilted RIGHT
            elif lm_list[17][0] - lm_list[5][0] > 40:
                wrist_angle = 45    # Hand tilted LEFT
            else:
                wrist_angle = 90    # Hand straight
           # ---- FINAL COMMAND STRING (Laptop → ESP32) ----
            command = (
                f"T:{servo_angles[0]},"
                f"I:{servo_angles[1]},"
                f"M:{servo_angles[2]},"
                f"R:{servo_angles[3]},"
                f"L:{servo_angles[4]},"
                f"W:{wrist_angle}"
            )

            print(command)

        frame_count += 1

        if frame_count % 3 == 0:
            if command != prev_command:
                if ser is not None:
                    try:
                        ser.write((command + "\n").encode())
                        prev_command = command
                    except:
                        pass
                else:
                    prev_command = command

        finger_names = ["Thumb", "Index", "Middle", "Ring", "Little"]
        for i in range(5):
           cv2.putText(frame,
                        f"{finger_names[i]}: {servo_angles[i]} deg",
                        (10, 30 + i * 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (255, 0, 0),
                        2)
           cv2.putText(frame,
                        f"Wrist: {wrist_angle} deg",
                        (10, 200),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.9,
                        (0, 0, 255),
                        2)
           cv2.putText(frame,
                        command,
                        (10, 240),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 255, 255),
                        2)

        mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Finger Status Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
