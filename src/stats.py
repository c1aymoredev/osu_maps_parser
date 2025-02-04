"""Module for tracking and displaying download progress."""
import time

class Stats:
    """Tracks statistics about the download process."""
    def __init__(self):
        self.processed_beatmaps = 0
        self.successful_saves = 0
        self.failed_saves = 0
        self.start_time = time.time()
        self.current_date_range = ""
    
    def print_progress(self):
        elapsed_time = time.time() - self.start_time
        print(f"\nCurrent period: {self.current_date_range}")
        print(f"Processed cards: {self.processed_beatmaps}")
        print(f"Saved successfully: {self.successful_saves}")
        print(f"Errors: {self.failed_saves}")
        print(f"Time has passed: {elapsed_time/60:.2f} minutes")