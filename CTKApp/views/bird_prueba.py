from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from datetime import datetime

# Load and initialize the BirdNET-Analyzer models.
analyzer = Analyzer()

recording = Recording(
    analyzer,
    "test\Sweet Bird Sound - Morning Sound Effect  Garden Bird copy 2.mp3",
    min_conf=0.25,
)
recording.analyze()
print(recording.detections)

