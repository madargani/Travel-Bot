from textual.app import App, ComposeResult
from textual.widgets import Static, Input, Markdown, Placeholder
from textual.widget import Widget
from textual.containers import Horizontal, VerticalScroll

class ChatInterface(Widget):
  def compose(self) -> ComposeResult:
    with VerticalScroll():
      for i in range(10):
        yield Placeholder(classes='message')
    yield Input(placeholder="Tell me about your dream trip")

class TripDetailPanel(Placeholder):
  pass

class TravelBot(App):
  CSS_PATH = "styles/styles.tcss"

  def compose(self) -> ComposeResult:
    with Horizontal():
      yield ChatInterface(classes='column')
      yield TripDetailPanel(classes='column')

if __name__ == "__main__":
  app = TravelBot()
  app.run()
