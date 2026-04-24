"""Port — automated CLI for porting GitHub Copilot components to Claude Code format.

Named after the porting framework it automates, this tool analyzes a source
repository, classifies its components, maps them to Claude Code equivalents,
generates the ported artifacts, and validates the results.
"""

__version__ = "0.2.0"

from port.config import PortConfig, load_config

__all__ = ["PortConfig", "load_config", "__version__"]
