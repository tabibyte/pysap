#!/usr/bin/env python3
"""
Demo script to test the audio player with sample directory structure
"""

import os
import tempfile
from pathlib import Path

def create_demo_structure():
    """Create a demo directory structure for testing"""
    # Create temporary directory for demo
    demo_dir = Path(tempfile.gettempdir()) / "audio_player_demo"
    demo_dir.mkdir(exist_ok=True)
    
    # Create some sample directories
    music_dir = demo_dir / "Music"
    music_dir.mkdir(exist_ok=True)
    
    rock_dir = music_dir / "Rock"
    jazz_dir = music_dir / "Jazz"
    electronic_dir = music_dir / "Electronic"
    
    for genre_dir in [rock_dir, jazz_dir, electronic_dir]:
        genre_dir.mkdir(exist_ok=True)
        
        # Create some dummy audio files (empty files for demo)
        for i in range(3):
            dummy_file = genre_dir / f"track_{i+1}.mp3"
            dummy_file.touch()
    
    print(f"Demo structure created at: {demo_dir}")
    print(f"Run the player with: python main.py --path {demo_dir}")
    
    return demo_dir

if __name__ == "__main__":
    create_demo_structure()
