import cv2
import os
import numpy as np
import pickle

dataset_path = "dataset_faces"

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)

faces = []
labels = []

label_ids = {}
current_id = 0

for person_name in os.listdir(dataset_path):

    person_folder = os.path.join(
        dataset_path,
        person_name
    )

    if not os.path.isdir(person_folder):
        continue

    label_ids[current_id] = person_name

    print(f"\nProcessing: {person_name}")

    image_count = 0

    for img_name in os.listdir(person_folder):

        img_path = os.path.join(
            person_folder,
            img_name
        )

        img = cv2.imread(img_path)

        if img is None:
            continue

        gray = cv2.cvtColor(
            img,
            cv2.COLOR_BGR2GRAY
        )

        detected_faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5
        )

        for (x, y, w, h) in detected_faces:

            roi = gray[
                y:y+h,
                x:x+w
            ]

            roi = cv2.resize(
                roi,
                (200, 200)
            )

            faces.append(roi)

            labels.append(current_id)

            image_count += 1

    print(
        f"Faces Found: {image_count}"
    )

    current_id += 1


print("\nTraining Model...")

recognizer = cv2.face.LBPHFaceRecognizer_create()

recognizer.train(
    faces,
    np.array(labels)
)

recognizer.save(
    "face_model.yml"
)

with open(
    "label_ids.pkl",
    "wb"
) as f:

    pickle.dump(
        label_ids,
        f
    )

print("\n======================")
print("Training Complete")
print("face_model.yml saved")
print("label_ids.pkl saved")
print("======================")