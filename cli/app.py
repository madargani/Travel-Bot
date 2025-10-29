from textual.app import App, ComposeResult
from textual.widgets import Markdown
from textual.containers import Horizontal, VerticalScroll

from components.ChatInterface import ChatInterface

from pathlib import Path

EXAMPLE_MARKDOWN = Path('cli/example_trip.md').read_text()

class TravelBot(App):
  CSS_PATH = "styles/styles.tcss"
  AUTO_FOCUS = "#chat_input"

  def compose(self) -> ComposeResult:
    with Horizontal():
      yield ChatInterface(classes='column')
      with VerticalScroll():
        yield Markdown(EXAMPLE_MARKDOWN, classes='column')

if __name__ == "__main__":
  app = TravelBot()
  app.run()
