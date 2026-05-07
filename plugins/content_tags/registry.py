from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class EmbedTag:
    required_args: tuple[str, ...]
    optional_args: tuple[str, ...]
    render: Callable[[dict[str, str]], str]

REGISTRY: dict[str, EmbedTag] = {}
