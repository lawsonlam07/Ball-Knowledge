import cv2
import numpy as np

from data.Coord import Coord

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

    def _apply_parallax(self, x_val: float, height_factor: float) -> float:
        """Internal helper to pull coordinates back toward the net based on height."""
        # 1.25m is the max shift for a ball at peak height near the net
        correction = height_factor * 1.25

        # Net is at 11.885.
        # If far (x < 11.885), pull closer by adding.
        # If near (x > 11.885), pull further by subtracting.
        return x_val + correction if x_val < 11.885 else x_val - correction

    def unskew_coords(self, points: list[list[float]], height_factors: list[float] = None):
        # 1. Raw Transform
        pts_array = np.array(points, dtype="float32").reshape(-1, 1, 2)
        transformed = cv2.perspectiveTransform(pts_array, self.matrix).reshape(-1, 2)

        # 2. Apply fix to all points if height factors are provided
        if height_factors is not None:
            for i in range(len(transformed)):
                h = height_factors[i] if i < len(height_factors) else 0.0
                transformed[i][0] = self._apply_parallax(transformed[i][0], h)

        return transformed  # Returns list[list[float]] (as a numpy array)

    def unskew_coords_to_coords(self, points: list[float], height_factor: float = 0.0):
        # Use the first method to get the base transform (with the fix)
        # We pass the point as [points] and the height as [height_factor]
        res = self.unskew_coords([points], height_factors=[height_factor])[0]

        return Coord(float(res[0]), float(res[1]))


frame = FrameUnskew([[0, 0], [0, 1], [1, 1], [1, 0]])
print(frame.unskew_coords([[0.5, 0]]))