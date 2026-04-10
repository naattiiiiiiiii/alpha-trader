from dataclasses import dataclass, field


@dataclass
class AgentResult:
    score: float  # -100 to +100
    indicators: dict = field(default_factory=dict)
    reasoning: str = ""


class BaseAgent:
    """Base class for all analysis agents."""

    name: str = "base"

    def analyze(self, *args, **kwargs) -> AgentResult:
        raise NotImplementedError
