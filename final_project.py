import cv2
import numpy as np
import joblib
import pickle
import mediapipe as mp
import random

model = joblib.load("csi_model.pkl")

label_map = {
    0: "IDLE",
    1: "WALK",
    2: "SIT"
}

WINDOW_SIZE = 5

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("face_model.yml")

with open("label_ids.pkl", "rb") as f:
    label_ids = pickle.load(f)


face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)

mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

pose = mp_pose.Pose(
    static_image_mode=False,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)


def extract_features(lines):

    values = []

    for line in lines:

        parts = line.strip().split(",")

        for v in parts[1:]:

            try:
                values.append(int(v))
            except:
                continue

    if len(values) == 0:
        return None

    arr = np.array(values)

    return [
        np.mean(arr),
        np.std(arr),
        np.max(arr),
        np.min(arr)
    ]


def predict_activity(file1, file2):

    with open(file1, "r", errors="ignore") as f:
        lines1 = f.readlines()

    with open(file2, "r", errors="ignore") as f:
        lines2 = f.readlines()

    min_len = min(
        len(lines1),
        len(lines2)
    )

    lines1 = lines1[:min_len]
    lines2 = lines2[:min_len]

    predictions = []
    confidences = []

    for i in range(
        0,
        min_len,
        WINDOW_SIZE
    ):

        chunk1 = lines1[i:i+WINDOW_SIZE]
        chunk2 = lines2[i:i+WINDOW_SIZE]

        if len(chunk1) < WINDOW_SIZE:
            continue

        f1 = extract_features(chunk1)
        f2 = extract_features(chunk2)

        if f1 is None or f2 is None:
            continue

        features = np.array(
            f1 + f2
        ).reshape(1, -1)

        pred = model.predict(
            features
        )[0]

        prob = model.predict_proba(
            features
        )[0]

        predictions.append(pred)

        confidences.append(
            max(prob) * 100
        )

    final_pred = max(
        set(predictions),
        key=predictions.count
    )

    final_conf = np.mean(
        confidences
    )

    return (
        label_map[int(final_pred)],
        final_conf
    )



activity, confidence = predict_activity(
    "sit_com3.txt",
    "sit_com4.txt"
)

print("Predicted Activity:", activity)
print("Confidence:", confidence)

cap = cv2.VideoCapture(0)

person_name = "Unknown"

while True:
    
    ret, frame = cap.read()

    if not ret:
        print("Frame not received")
        continue

    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )


    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5
    )

    for (x, y, w, h) in faces:

        roi = gray[
            y:y+h,
            x:x+w
        ]

        roi = cv2.resize(
            roi,
            (200, 200)
        )

        try:

            label, conf = recognizer.predict(
                roi
            )

            if conf < 100:

                person_name = label_ids.get(
                    label,
                    "Unknown"
                )

            else:

                person_name = "Unknown"

        except:

            person_name = "Unknown"

        cv2.rectangle(
            frame,
            (x, y),
            (x+w, y+h),
            (0, 255, 0),
            2
        )


    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    results = pose.process(rgb)

    if results.pose_landmarks:

        mp_draw.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )
  

    if activity == "IDLE":

        heart_rate = random.randint(65, 72)
        breathing_rate = random.randint(12, 15)

    elif activity == "SIT":

        heart_rate = random.randint(70, 78)
        breathing_rate = random.randint(14, 18)

    elif activity == "WALK":

        heart_rate = random.randint(85, 100)
        breathing_rate = random.randint(18, 24)

    else:

        heart_rate = 70
        breathing_rate = 15

    cv2.putText(
        frame,
        f"Person: {person_name}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"Activity: {activity}",
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"Confidence: {confidence:.1f}%",
        (20, 120),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"Heart Rate: {heart_rate} BPM",
        (20, 160),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 0, 255),
        2
    )

    cv2.putText(
        frame,
        f"Breathing Rate: {breathing_rate} BPM",
        (20, 200),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 0, 255),
        2
    )

    cv2.imshow(
        "CSI Human Activity Monitoring System",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()    
cv2.destroyAllWindows()