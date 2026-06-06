import numpy as np
import csv

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

    if len(values) == 0:
        return None

    arr = np.array(values)

    return [
        np.mean(arr),
        np.std(arr),
        np.max(arr),
        np.min(arr)
    ]


def process_file(file_path, max_lines=None):

    with open(file_path, "r", errors="ignore") as f:
        lines = f.readlines()

    if max_lines:
        lines = lines[:max_lines]

    chunks = []

    for i in range(0, len(lines), WINDOW_SIZE):

        chunk = lines[i:i + WINDOW_SIZE]

        if len(chunk) < WINDOW_SIZE:
            continue

        features = extract_features(chunk)

        if features:
            chunks.append(features)

    return chunks


pairs = [

    ("idle_com3.txt", "idle_com4.txt", 0),

    ("walk_com3.txt", "walk_com4.txt", 1),

    ("sit_com3.txt", "sit_com4.txt", 2)

]

dataset = []

for file1, file2, label in pairs:

    with open(file1) as f1:
        len1 = len(f1.readlines())

    with open(file2) as f2:
        len2 = len(f2.readlines())

    min_lines = min(len1, len2)

    print(f"\nProcessing {file1} & {file2}")
    print(f"Using {min_lines} rows")

    chunks1 = process_file(
        file1,
        max_lines=min_lines
    )

    chunks2 = process_file(
        file2,
        max_lines=min_lines
    )

    min_chunks = min(
        len(chunks1),
        len(chunks2)
    )

    print(
        f"Generated {min_chunks} samples"
    )

    for i in range(min_chunks):

        combined = (
            chunks1[i] +
            chunks2[i] +
            [label]
        )

        dataset.append(combined)

with open(
    "dataset_combined.csv",
    "w",
    newline=""
) as f:

    writer = csv.writer(f)

    writer.writerows(dataset)

print("\n================================")
print("dataset_combined.csv created")
print("Total samples:", len(dataset))
print("================================")