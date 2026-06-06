import cv2
import pickle

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("face_model.yml")

with open("label_ids.pkl", "rb") as f:
    label_ids = pickle.load(f)

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    if not ret:
        break

    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    faces = face_cascade.detectMultiScale(
        gray,
        1.1,
        5
    )

    for (x,y,w,h) in faces:

        roi = gray[y:y+h, x:x+w]

        roi = cv2.resize(
            roi,
            (200,200)
        )

        label, confidence = recognizer.predict(
            roi
        )

        name = label_ids.get(
            label,
            "Unknown"
        )

        cv2.rectangle(
            frame,
            (x,y),
            (x+w,y+h),
            (0,255,0),
            2
        )

        cv2.putText(
            frame,
            f"{name}",
            (x,y-10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0,255,0),
            2
        )

    cv2.imshow(
        "Face Recognition",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()