from textual.app import ComposeResult
from textual.widgets import Static, Input
from textual.containers import VerticalScroll
from textual.widget import Widget
from textual import on, work

from helpers.mock_stream import mock_stream

class ChatInterface(Widget):
  def compose(self) -> ComposeResult:
    yield VerticalScroll(id = 'message_container')
    yield Input(placeholder="Tell me about your dream trip", id="chat_input")

  @on(Input.Submitted)
  def send_message(self, event: Input.Submitted) -> None:
      message_container = self.query_one('#message_container')
      event.input.clear()
      message_container.mount(Static(event.value, classes='user message'))
      message_container.mount(response := Static('', classes='agent message'))
      self.send_prompt(event.value, response)

  @work(thread=True)
  def send_prompt(self, prompt: str, response: Static) -> None:
    response_content = ""
    llm_response = mock_stream()
    for chunk in llm_response:
      response_content += chunk
      response.update(response_content)
