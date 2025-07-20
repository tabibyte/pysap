#!/usr/bin/env python3
"""
Terminal Audio Player - A musikcube/rmpc inspired audio player
"""

import os
import sys
import threading
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
import json

import pygame
from mutagen import File as MutagenFile
from mutagen.id3 import ID3NoHeaderError
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.layout import Layout
from rich.text import Text
from rich.align import Align
import argparse


class AudioMetadata:
    """Class to handle audio file metadata"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.title = None
        self.artist = None
        self.album = None
        self.duration = None
        self.genre = None
        self.year = None
        self._load_metadata()
    
    def _load_metadata(self):
        """Load metadata from audio file"""
        try:
            audio_file = MutagenFile(self.file_path)
            if audio_file is not None:
                self.duration = getattr(audio_file, 'info', {}).length or 0
                
                # Extract common tags
                tags = audio_file.tags or {}
                self.title = self._get_tag(tags, ['TIT2', 'TITLE', '\xa9nam'])
                self.artist = self._get_tag(tags, ['TPE1', 'ARTIST', '\xa9ART'])
                self.album = self._get_tag(tags, ['TALB', 'ALBUM', '\xa9alb'])
                self.genre = self._get_tag(tags, ['TCON', 'GENRE', '\xa9gen'])
                self.year = self._get_tag(tags, ['TDRC', 'DATE', '\xa9day'])
                
        except Exception:
            pass
        
        # Fallback to filename if no title
        if not self.title:
            self.title = Path(self.file_path).stem
    
    def _get_tag(self, tags, tag_keys):
        """Get tag value from multiple possible keys"""
        for key in tag_keys:
            if key in tags:
                value = tags[key]
                if isinstance(value, list) and value:
                    return str(value[0])
                return str(value)
        return None


class AudioPlayer:
    """Audio playback engine using pygame"""
    
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
        self.current_file = None
        self.is_playing = False
        self.is_paused = False
        self.position = 0
        self.duration = 0
        self.volume = 0.7
        pygame.mixer.music.set_volume(self.volume)
    
    def load(self, file_path: str) -> bool:
        """Load an audio file"""
        try:
            pygame.mixer.music.load(file_path)
            self.current_file = file_path
            
            # Get duration from metadata
            metadata = AudioMetadata(file_path)
            self.duration = metadata.duration or 0
            self.position = 0
            return True
        except pygame.error:
            return False
    
    def play(self):
        """Start playback"""
        if self.current_file:
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
    
    def pause(self):
        """Pause playback"""
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_paused = True
    
    def resume(self):
        """Resume playback"""
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
    
    def stop(self):
        """Stop playback"""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        self.position = 0
    
    def set_volume(self, volume: float):
        """Set volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)
    
    def get_volume(self) -> float:
        """Get current volume"""
        return self.volume
    
    def is_busy(self) -> bool:
        """Check if music is playing"""
        return pygame.mixer.music.get_busy()
    
    def update_position(self):
        """Update playback position (called periodically)"""
        if self.is_playing and not self.is_paused and self.is_busy():
            # pygame doesn't provide position, so we approximate
            self.position += 0.1


class Playlist:
    """Manage playlists and track lists"""
    
    def __init__(self):
        self.tracks: List[str] = []
        self.current_index = 0
        self.name = "Default"
    
    def add_track(self, file_path: str):
        """Add a track to the playlist"""
        if file_path not in self.tracks:
            self.tracks.append(file_path)
    
    def remove_track(self, index: int):
        """Remove a track by index"""
        if 0 <= index < len(self.tracks):
            self.tracks.pop(index)
            if self.current_index >= len(self.tracks):
                self.current_index = max(0, len(self.tracks) - 1)
    
    def clear(self):
        """Clear all tracks"""
        self.tracks.clear()
        self.current_index = 0
    
    def get_current_track(self) -> Optional[str]:
        """Get current track path"""
        if 0 <= self.current_index < len(self.tracks):
            return self.tracks[self.current_index]
        return None
    
    def next_track(self) -> Optional[str]:
        """Move to next track"""
        if self.tracks:
            self.current_index = (self.current_index + 1) % len(self.tracks)
            return self.get_current_track()
        return None
    
    def previous_track(self) -> Optional[str]:
        """Move to previous track"""
        if self.tracks:
            self.current_index = (self.current_index - 1) % len(self.tracks)
            return self.get_current_track()
        return None
    
    def set_current_index(self, index: int):
        """Set current track index"""
        if 0 <= index < len(self.tracks):
            self.current_index = index


class FileManager:
    """Handle file system navigation and audio file discovery"""
    
    AUDIO_EXTENSIONS = {'.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac', '.wma'}
    
    def __init__(self, root_path: str = None):
        self.root_path = Path(root_path or os.getcwd())
        self.current_path = self.root_path
    
    def get_directories(self, path: Path = None) -> List[Path]:
        """Get directories in the given path"""
        if path is None:
            path = self.current_path
        
        try:
            dirs = [p for p in path.iterdir() if p.is_dir() and not p.name.startswith('.')]
            return sorted(dirs)
        except (PermissionError, OSError):
            return []
    
    def get_audio_files(self, path: Path = None) -> List[Path]:
        """Get audio files in the given path"""
        if path is None:
            path = self.current_path
        
        try:
            files = [
                p for p in path.iterdir() 
                if p.is_file() and p.suffix.lower() in self.AUDIO_EXTENSIONS
            ]
            return sorted(files)
        except (PermissionError, OSError):
            return []
    
    def navigate_to(self, path: Path):
        """Navigate to a directory"""
        if path.is_dir():
            self.current_path = path
    
    def go_up(self):
        """Go to parent directory"""
        if self.current_path.parent != self.current_path:
            self.current_path = self.current_path.parent


class TerminalUI:
    """Terminal user interface using Rich"""
    
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        self.audio_player = AudioPlayer()
        self.playlist = Playlist()
        self.file_manager = FileManager()
        
        # UI State
        self.selected_dir_index = 0
        self.selected_file_index = 0
        self.active_panel = "directories"  # "directories", "files", "player"
        self.running = True
        
        # Setup layout
        self._setup_layout()
        
        # Start position update thread
        self.position_thread = threading.Thread(target=self._position_updater, daemon=True)
        self.position_thread.start()
    
    def _setup_layout(self):
        """Setup the layout structure"""
        self.layout.split_column(
            Layout(name="main", ratio=4),
            Layout(name="controls", size=8)
        )
        
        self.layout["main"].split_row(
            Layout(name="left", ratio=1),
            Layout(name="right", ratio=2)
        )
        
        self.layout["left"].split_column(
            Layout(name="directories", ratio=1),
            Layout(name="playlists", ratio=1)
        )
        
        self.layout["right"].split_column(
            Layout(name="files", ratio=3),
            Layout(name="player", ratio=1)
        )
    
    def _position_updater(self):
        """Update playback position in background"""
        while self.running:
            if self.audio_player.is_playing and not self.audio_player.is_paused:
                self.audio_player.update_position()
            time.sleep(0.1)
    
    def _render_directories(self) -> Panel:
        """Render directories panel"""
        directories = self.file_manager.get_directories()
        
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Directory", style="cyan")
        
        # Add parent directory option
        if self.file_manager.current_path != self.file_manager.root_path:
            style = "bold yellow" if self.selected_dir_index == 0 and self.active_panel == "directories" else "yellow"
            table.add_row(f"{'>' if self.selected_dir_index == 0 and self.active_panel == 'directories' else ' '} ..", style=style)
            offset = 1
        else:
            offset = 0
        
        for i, directory in enumerate(directories):
            is_selected = (i + offset == self.selected_dir_index and self.active_panel == "directories")
            style = "bold cyan" if is_selected else "cyan"
            prefix = ">" if is_selected else " "
            table.add_row(f"{prefix} {directory.name}", style=style)
        
        current_path = str(self.file_manager.current_path)
        if len(current_path) > 30:
            current_path = "..." + current_path[-27:]
        
        return Panel(
            table,
            title=f"📁 {current_path}",
            border_style="green" if self.active_panel == "directories" else "dim"
        )
    
    def _render_playlists(self) -> Panel:
        """Render playlists panel"""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Playlist", style="magenta")
        
        table.add_row("🎵 Current Queue", style="magenta")
        table.add_row(f"   {len(self.playlist.tracks)} tracks", style="dim magenta")
        
        return Panel(
            table,
            title="📋 Playlists",
            border_style="magenta"
        )
    
    def _render_files(self) -> Panel:
        """Render files panel"""
        audio_files = self.file_manager.get_audio_files()
        
        table = Table(show_header=True, box=None, padding=(0, 1))
        table.add_column("", width=2)
        table.add_column("Title", style="white")
        table.add_column("Artist", style="dim white")
        table.add_column("Duration", style="dim white", justify="right")
        
        for i, file_path in enumerate(audio_files):
            metadata = AudioMetadata(str(file_path))
            is_selected = (i == self.selected_file_index and self.active_panel == "files")
            is_current = (str(file_path) == self.audio_player.current_file)
            
            # Determine row style and prefix
            if is_current:
                prefix = "🎵" if self.audio_player.is_playing else "⏸️"
                style = "bold green"
            elif is_selected:
                prefix = ">"
                style = "bold white"
            else:
                prefix = " "
                style = "white"
            
            # Format duration
            duration_str = ""
            if metadata.duration:
                minutes = int(metadata.duration // 60)
                seconds = int(metadata.duration % 60)
                duration_str = f"{minutes}:{seconds:02d}"
            
            table.add_row(
                prefix,
                metadata.title or file_path.name,
                metadata.artist or "",
                duration_str,
                style=style
            )
        
        return Panel(
            table,
            title=f"🎵 Files ({len(audio_files)})",
            border_style="blue" if self.active_panel == "files" else "dim"
        )
    
    def _render_player(self) -> Panel:
        """Render player controls panel"""
        if not self.audio_player.current_file:
            return Panel(
                Align.center("No track loaded"),
                title="🎵 Player",
                border_style="yellow"
            )
        
        metadata = AudioMetadata(self.audio_player.current_file)
        
        # Track info
        track_info = []
        track_info.append(f"🎵 {metadata.title or 'Unknown'}")
        if metadata.artist:
            track_info.append(f"👤 {metadata.artist}")
        if metadata.album:
            track_info.append(f"💿 {metadata.album}")
        
        # Progress bar
        if self.audio_player.duration > 0:
            progress = self.audio_player.position / self.audio_player.duration
            progress = max(0, min(1, progress))
        else:
            progress = 0
        
        # Time display
        current_time = f"{int(self.audio_player.position // 60)}:{int(self.audio_player.position % 60):02d}"
        total_time = f"{int(self.audio_player.duration // 60)}:{int(self.audio_player.duration % 60):02d}"
        
        # Status
        if self.audio_player.is_playing:
            status = "▶️ Playing" if not self.audio_player.is_paused else "⏸️ Paused"
        else:
            status = "⏹️ Stopped"
        
        # Volume
        volume_bars = int(self.audio_player.volume * 10)
        volume_display = "🔊 " + "█" * volume_bars + "░" * (10 - volume_bars)
        
        content = "\n".join(track_info + [
            "",
            f"{status} | {current_time} / {total_time}",
            f"{'█' * int(progress * 40)}{'░' * (40 - int(progress * 40))}",
            "",
            volume_display
        ])
        
        return Panel(
            content,
            title="🎵 Now Playing",
            border_style="yellow" if self.active_panel == "player" else "dim"
        )
    
    def _render_controls(self) -> Panel:
        """Render control instructions"""
        controls = [
            "Tab: Switch panels | ↑↓: Navigate | Enter: Select/Play | Space: Play/Pause",
            "n: Next track | p: Previous track | +/-: Volume | q: Quit | a: Add to queue"
        ]
        
        return Panel(
            "\n".join(controls),
            title="⌨️ Controls",
            border_style="dim"
        )
    
    def render(self):
        """Render the complete UI"""
        self.layout["directories"].update(self._render_directories())
        self.layout["playlists"].update(self._render_playlists())
        self.layout["files"].update(self._render_files())
        self.layout["player"].update(self._render_player())
        self.layout["controls"].update(self._render_controls())
        
        self.console.clear()
        self.console.print(self.layout)


def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description="Terminal Audio Player")
    parser.add_argument("--path", "-p", default=".", help="Starting directory path")
    args = parser.parse_args()
    
    ui = TerminalUI()
    ui.file_manager = FileManager(args.path)
    
    try:
        import keyboard
        
        def on_key_event(event):
            if event.event_type == keyboard.KEY_DOWN:
                handle_key(ui, event.name)
        
        keyboard.hook(on_key_event)
        
        while ui.running:
            ui.render()
            time.sleep(0.1)
            
    except ImportError:
        # Fallback for systems without keyboard module
        print("Keyboard module not available. Use Ctrl+C to exit.")
        while ui.running:
            ui.render()
            time.sleep(1)
    
    except KeyboardInterrupt:
        ui.running = False
        ui.audio_player.stop()
        print("\nGoodbye!")


def handle_key(ui: TerminalUI, key: str):
    """Handle keyboard input"""
    if key == 'q':
        ui.running = False
        return
    
    # Panel switching
    if key == 'tab':
        panels = ["directories", "files", "player"]
        current_index = panels.index(ui.active_panel)
        ui.active_panel = panels[(current_index + 1) % len(panels)]
        return
    
    # Navigation
    if key == 'up':
        if ui.active_panel == "directories":
            max_dirs = len(ui.file_manager.get_directories())
            if ui.file_manager.current_path != ui.file_manager.root_path:
                max_dirs += 1  # Include ".." option
            ui.selected_dir_index = max(0, ui.selected_dir_index - 1)
        elif ui.active_panel == "files":
            max_files = len(ui.file_manager.get_audio_files())
            ui.selected_file_index = max(0, ui.selected_file_index - 1)
    
    elif key == 'down':
        if ui.active_panel == "directories":
            max_dirs = len(ui.file_manager.get_directories())
            if ui.file_manager.current_path != ui.file_manager.root_path:
                max_dirs += 1  # Include ".." option
            ui.selected_dir_index = min(max_dirs - 1, ui.selected_dir_index + 1)
        elif ui.active_panel == "files":
            max_files = len(ui.file_manager.get_audio_files())
            ui.selected_file_index = min(max_files - 1, ui.selected_file_index + 1)
    
    # Selection/Enter
    elif key == 'enter':
        if ui.active_panel == "directories":
            directories = ui.file_manager.get_directories()
            
            # Handle ".." (parent directory)
            offset = 1 if ui.file_manager.current_path != ui.file_manager.root_path else 0
            if offset and ui.selected_dir_index == 0:
                ui.file_manager.go_up()
                ui.selected_dir_index = 0
            elif ui.selected_dir_index - offset < len(directories):
                selected_dir = directories[ui.selected_dir_index - offset]
                ui.file_manager.navigate_to(selected_dir)
                ui.selected_dir_index = 0
                ui.selected_file_index = 0
        
        elif ui.active_panel == "files":
            audio_files = ui.file_manager.get_audio_files()
            if audio_files and ui.selected_file_index < len(audio_files):
                selected_file = audio_files[ui.selected_file_index]
                if ui.audio_player.load(str(selected_file)):
                    ui.audio_player.play()
    
    # Playback controls
    elif key == 'space':
        if ui.audio_player.is_playing:
            if ui.audio_player.is_paused:
                ui.audio_player.resume()
            else:
                ui.audio_player.pause()
        elif ui.audio_player.current_file:
            ui.audio_player.play()
    
    elif key == 'n':
        # Next track (if in playlist)
        next_track = ui.playlist.next_track()
        if next_track and ui.audio_player.load(next_track):
            ui.audio_player.play()
    
    elif key == 'p':
        # Previous track (if in playlist)
        prev_track = ui.playlist.previous_track()
        if prev_track and ui.audio_player.load(prev_track):
            ui.audio_player.play()
    
    # Volume controls
    elif key == 'plus' or key == '=':
        ui.audio_player.set_volume(ui.audio_player.get_volume() + 0.1)
    
    elif key == 'minus':
        ui.audio_player.set_volume(ui.audio_player.get_volume() - 0.1)
    
    # Add to queue
    elif key == 'a':
        if ui.active_panel == "files":
            audio_files = ui.file_manager.get_audio_files()
            if audio_files and ui.selected_file_index < len(audio_files):
                selected_file = audio_files[ui.selected_file_index]
                ui.playlist.add_track(str(selected_file))


if __name__ == "__main__":
    main()