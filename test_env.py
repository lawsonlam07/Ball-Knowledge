import cv2
import torch
import supervision as sv
from ultralytics import YOLO

print(f"OpenCV Version: {cv2.__version__}")
print(f"CUDA Available: {torch.cuda.is_available()}")
print(f"Supervision Version: {sv.__version__}")
print("Environment is ready!")
