from random import choice
from string import ascii_letters
from time import sleep
from collections.abc import Iterator

def mock_stream(size: int = 32) -> Iterator[str]:
  for _ in range(size):
    yield choice(ascii_letters)
    sleep(0.1)
