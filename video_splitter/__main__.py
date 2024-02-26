from pathlib import Path
from .splitter import main

if __name__ == "__main__":
    video_file = Path(input("Drag video file here: ").strip().replace(r"\ ", " "))
    config_file = Path(input("Drag config file here: ").strip().replace(r"\ ", " "))
    main(video_file, config_file)
