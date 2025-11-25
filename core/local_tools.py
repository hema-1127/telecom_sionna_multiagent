"""
REAL local tool registry.

This file connects SimulationAgent's local fallback
to the actual Sionna tool implementations inside /tools.

IMPORTANT:
- Do NOT keep dummy/stub tool functions here.
- Only keep imports + registry.
"""

from tools.simulate_constellation import simulate_constellation
from tools.simulate_ber import simulate_ber
from tools.simulate_ber_mimo import simulate_ber_mimo
from tools.simulate_radio_map import simulate_radio_map
from tools.simulate_multi_radio_map import simulate_multi_radio_map


# Registry used by SimulationAgent
LOCAL_TOOL_REGISTRY = {
    "simulate_constellation": simulate_constellation,
    "simulate_ber": simulate_ber,
    "simulate_ber_mimo": simulate_ber_mimo,
    "simulate_radio_map": simulate_radio_map,
    "simulate_multi_radio_map": simulate_multi_radio_map,
}
