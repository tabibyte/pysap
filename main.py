from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Button, Static

class pysap(App):
    CSS_PATH = "styles.tcss"

    def compose(self) -> ComposeResult:
        with Horizontal(id="dir"):
            yield Button("Dir", id="dir_button", classes="button")
            
            yield Button("Playlists", id="playlists_button", classes="button")
        
            yield Button("*", id="star_button", classes="button")
            
        yield Static(id = "tracklist")
        
        yield Static(id ="player_bar")
        
    def on_mount(self) -> None:
        self.query_one("#dir", Horizontal).border_title = "Dir"
        self.query_one("#tracklist", Static).border_title = "Tracklist"
        self.query_one("#player_bar", Static).border_title = "Player Bar"
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "browse_button":
            # Handle button press here
            pass

if __name__ == "__main__":
    app = pysap()
    app.run()