from textual.app import App, ComposeResult
from textual.widgets import Static, Input, Markdown, Placeholder
from textual.widget import Widget
from textual.containers import Horizontal, VerticalScroll
from textual import on

from pathlib import Path

EXAMPLE_MARKDOWN = Path('cli/example_trip.md').read_text()

class ChatInterface(Widget):
  def compose(self) -> ComposeResult:
    yield VerticalScroll(id = 'message_container')
    yield Input(placeholder="Tell me about your dream trip")

  @on(Input.Submitted)
  def send_message(self, event: Input.Submitted) -> None:
      message_container = self.query_one('#message_container')
      event.input.clear()
      message_container.mount(Placeholder(event.value, classes='message'))

class TravelBot(App):
  CSS_PATH = "styles/styles.tcss"

  def compose(self) -> ComposeResult:
    with Horizontal():
      yield ChatInterface(classes='column')
      with VerticalScroll():
        yield Markdown(EXAMPLE_MARKDOWN, classes='column')

if __name__ == "__main__":
  app = TravelBot()
  app.run()
