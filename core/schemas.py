from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

@dataclass
class TaskSpec:
    task_type: str                       # constellation | ber | mimo_comparison | radiomap | multi_radio_map
    parameters: Dict[str, Any] = field(default_factory=dict)
    raw_prompt: str = ""
    tool_name: Optional[str] = None

@dataclass
class ToolResult:
    ok: bool
    payload: Dict[str, Any]              # could include paths to plots, arrays, metrics
    error: Optional[str] = None
