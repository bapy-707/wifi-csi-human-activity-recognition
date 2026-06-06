# Human Activity Recognition using ESP32 CSI

## Overview

This project uses ESP32 Channel State Information (CSI) and Machine Learning to recognize human activities such as:

- Idle
- Walk
- Sit

The system integrates:

- CSI-based Activity Recognition
- XGBoost Classification
- Face Recognition (LBPH)
- Skeleton Detection (MediaPipe)
- Person Identification
- Estimated Heart Rate and Breathing Rate

## Workflow

ESP32 CSI Data
→ Feature Extraction
→ XGBoost Model
→ Activity Prediction

Camera Input
→ Face Recognition
→ Person Identification

Camera Input
→ Skeleton Detection

Final Output:
- Person Name
- Activity
- Confidence
- Heart Rate
- Breathing Rate