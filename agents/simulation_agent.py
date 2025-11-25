from core.logger import setup_logger
from core.schemas import ToolResult
from core.local_tools import LOCAL_TOOL_REGISTRY

TASK_TO_TOOL = {
    "constellation": "simulate_constellation",
    "ber": "simulate_ber",
    "mimo_comparison": "simulate_ber_mimo",
    "radiomap": "simulate_radio_map",
    "multi_radio_map": "simulate_multi_radio_map",
}

class SimulationAgent:
    def __init__(self, mcp_client=None, use_mcp=False):
        self.mcp = mcp_client
        self.use_mcp = use_mcp
        self.logger = setup_logger("SimulationAgent")

    def run(self, task_spec):
        tool_name = TASK_TO_TOOL.get(task_spec.task_type)
        task_spec.tool_name = tool_name
        params = task_spec.parameters or {}

        self.logger.info(f"Calling tool: {tool_name} with params: {params}")

        # ---- 1) Try MCP only if enabled ----
        if self.use_mcp and self.mcp is not None:
            result = self.mcp.call_tool(tool_name, params)
            if result.ok:
                self.logger.info("MCP tool call success.")
                return task_spec, result
            self.logger.warning(f"MCP failed, falling back to local tools: {result.error}")

        # ---- 2) Local tool fallback ----
        try:
            tool_fn = LOCAL_TOOL_REGISTRY[tool_name]
            payload = tool_fn(**params)
            self.logger.info("Local tool call success.")
            return task_spec, ToolResult(ok=True, payload=payload)
        except Exception as e:
            self.logger.error(f"Local tool call failed: {e}")
            return task_spec, ToolResult(ok=False, payload={}, error=str(e))
