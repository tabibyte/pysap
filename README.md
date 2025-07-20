# Terminal Audio Player

A musikcube/rmpc inspired terminal-based audio player written in Python.

## Features

- **Three-panel layout**: Directory browser, file list, and player controls
- **Audio format support**: MP3, WAV, OGG, FLAC, M4A, AAC, WMA
- **Metadata display**: Shows title, artist, album, duration
- **Playlist management**: Add tracks to queue, navigate between tracks
- **Volume control**: Adjustable volume with visual indicator
- **Progress tracking**: Real-time playback position and progress bar
- **Keyboard navigation**: Intuitive keyboard controls

## Installation

1. Install Python 3.7+ and pip
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the audio player:
```bash
python main.py
```

Or specify a starting directory:
```bash
python main.py --path /path/to/music
```

## Layout

```
┌─────────────────┬───────────────────────────────────┐
│   Directories   │              Files                │
│                 │                                   │
│ > Music         │ > Song 1.mp3    Artist   3:45    │
│   Downloads     │   Song 2.mp3    Artist   4:12    │
│   ...           │   Song 3.mp3    Artist   2:58    │
├─────────────────┼───────────────────────────────────┤
│   Playlists     │           Now Playing             │
│                 │                                   │
│ 🎵 Current Queue│ 🎵 Current Song Title            │
│   5 tracks      │ 👤 Artist Name                   │
│                 │ 💿 Album Name                    │
│                 │ ▶️ Playing | 1:23 / 3:45         │
│                 │ ████████████████░░░░░░░░░░░░      │
│                 │ 🔊 ████████░░                    │
└─────────────────┴───────────────────────────────────┘
│                   Controls                          │
│ Tab: Switch panels | ↑↓: Navigate | Enter: Play    │
│ Space: Pause/Resume | n: Next | p: Previous | q: Quit│
└─────────────────────────────────────────────────────┘
```

## Keyboard Controls

### General
- `Tab`: Switch between panels (directories → files → player)
- `↑/↓`: Navigate up/down in current panel
- `Enter`: Select directory or play file
- `q`: Quit application

### Playback
- `Space`: Play/pause current track
- `n`: Next track in playlist
- `p`: Previous track in playlist
- `+/=`: Increase volume
- `-`: Decrease volume

### Playlist
- `a`: Add selected file to playlist queue

## Requirements

- Python 3.7+
- pygame (for audio playback)
- rich (for terminal UI)
- mutagen (for metadata extraction)
- keyboard (for key handling)
- pillow (for image processing)
- textual (for enhanced UI components)

## Notes

- The application requires appropriate permissions to access audio files
- On some systems, you may need to run with administrator privileges for global key capture
- Supported audio formats depend on pygame's capabilities on your system

## Troubleshooting

If you encounter issues:

1. **No audio playback**: Check if pygame can access your audio system
2. **Permission errors**: Run with appropriate file system permissions
3. **Key handling issues**: Some systems may require running as administrator for global key capture

## Future Enhancements

- Album art display
- Custom playlists
- Equalizer
- Search functionality
- Theme customization
- Last.fm integration
