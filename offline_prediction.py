import joblib
import numpy as np

model = joblib.load("csi_model.pkl")

label_map = {
    0: "IDLE",
    1: "WALK",
    2: "SIT"
}

WINDOW_SIZE = 5


def extract_features(lines):

    values = []

    for line in lines:

        parts = line.strip().split(",")

        for v in parts[1:]:

            try:
                values.append(int(v))
            except:
                continue

    arr = np.array(values)

    return [
        np.mean(arr),
        np.std(arr),
        np.max(arr),
        np.min(arr)
    ]


def process_pair(file1, file2):

    with open(file1) as f:
        lines1 = f.readlines()

    with open(file2) as f:
        lines2 = f.readlines()

    min_lines = min(
        len(lines1),
        len(lines2)
    )

    lines1 = lines1[:min_lines]
    lines2 = lines2[:min_lines]

    for i in range(
        0,
        min_lines,
        WINDOW_SIZE
    ):

        c1 = lines1[i:i+WINDOW_SIZE]
        c2 = lines2[i:i+WINDOW_SIZE]

        if len(c1) < WINDOW_SIZE:
            continue

        f1 = extract_features(c1)
        f2 = extract_features(c2)

        features = np.array(
            f1 + f2
        ).reshape(1,-1)

        pred = model.predict(
            features
        )[0]

        probs = model.predict_proba(
            features
        )[0]

        conf = max(probs)*100

        print(
            "Prediction:",
            label_map[int(pred)],
            "| Confidence:",
            round(conf,2)
        )


process_pair(
    "walk_com3.txt",
    "walk_com4.txt"
)