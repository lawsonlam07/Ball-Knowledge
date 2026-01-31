import cv2
import numpy as np

TENNIS_COURT_LENGTH: float = 23.77
TENNIS_COURT_SINGLES_WIDTH: float = 8.23

class FrameUnskew:
    def __init__(self, corners: list[list[float]]):
        if len(corners) == 4:
            src_points = np.array(corners, dtype="float32")
            dst_points = np.array([
                [0, 0],
                [0, TENNIS_COURT_SINGLES_WIDTH],
                [TENNIS_COURT_LENGTH, TENNIS_COURT_SINGLES_WIDTH],
                [TENNIS_COURT_LENGTH, 0]
            ], dtype="float32")
            self.matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        else:
            raise ValueError()

    def unskew_coords(self, points: list[list[float]]):
        pts_array = np.array(points, dtype="float32").reshape(-1, 1, 2)
        return cv2.perspectiveTransform(pts_array, self.matrix).reshape(-1, 2)
        # returns list[list[float]]

frame = FrameUnskew([[0, 0], [0, 1], [1, 1], [1, 0]])
print(frame.unskew_coords([[0.5, 0]]))