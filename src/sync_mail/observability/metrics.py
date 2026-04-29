import time
from collections import deque
from datetime import timedelta
from typing import Optional

class ThroughputCalculator:
    """
    Calculates moving average throughput (rows/sec).
    Uses a sliding window of recent batches to smooth out fluctuations.
    """
    def __init__(self, window_size: int = 30):
        self.window_size = window_size
        self.history = deque(maxlen=window_size)
        self.start_time = time.monotonic()
        self.total_rows = 0

    def record(self, rows: int):
        """
        Records a completed batch.
        """
        now = time.monotonic()
        self.history.append((rows, now))
        self.total_rows += rows

    def current_rate(self) -> float:
        """
        Calculates rows per second based on the sliding window.
        """
        if len(self.history) < 2:
            return 0.0
            
        rows_in_window = sum(item[0] for item in self.history)
        time_start = self.history[0][1]
        time_end = self.history[-1][1]
        
        duration = time_end - time_start
        if duration <= 0:
            return 0.0
            
        return rows_in_window / duration

    def average_rate(self) -> float:
        """
        Calculates rows per second since the start of the job.
        """
        duration = time.monotonic() - self.start_time
        if duration <= 0:
            return 0.0
        return self.total_rows / duration

def compute_eta(remaining_rows: int, throughput: float) -> Optional[timedelta]:
    """
    Computes Estimated Time of Arrival based on remaining rows and throughput.
    """
    if throughput <= 0:
        return None
        
    seconds = remaining_rows / throughput
    return timedelta(seconds=int(seconds))
