from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Static

class pysap(App):
    CSS_PATH = "styles.tcss"
    
    def __init__(self):
        super().__init__()
        self.current_directory = "C:\\vault"
        
    def compose(self) -> ComposeResult:
        with Vertical(id="dir"):
            with Horizontal(id="buttons"):
                yield Button("Dir", id="dir_button", classes="button_dir")
                yield Button("Playlists", id="playlists_button", classes="button_dir")
                yield Button("*", id="star_button", classes="button_dir")
            
            with Vertical(id="directory_listing"):
                yield Static("Click 'Dir' to browse folders", id="folder_content")
            
        yield Static(id = "tracklist")
        
        yield Static(id ="player_bar")
        
    def on_mount(self) -> None:
        self.query_one("#dir", Vertical).border_title = "Dir"
        self.query_one("#tracklist", Static).border_title = "Tracklist"
        self.query_one("#player_bar", Static).border_title = "Player Bar"
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "browse_button":
            # Handle button press here
            pass

if __name__ == "__main__":
    app = pysap()
    app.run()