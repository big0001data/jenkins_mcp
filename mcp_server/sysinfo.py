from typing import Any
from mcp.server.fastmcp import FastMCP
from fetch_info import get_system_info

# Initialize FastMCP server
mcp = FastMCP("sysinfo")


@mcp.tool()
async def get_sysinfo() -> str:
    """Get the current system information.
    Gives system information such as System, Node name, Release, Version, Machine, Processor
    CPU Information such as Processor, Physical Cores, Logical Cores
    Memory Information such as Total Memory, Available Memory, Used Memory, Memory Utilization
    Disk Information such as Total Disk Space, Used Disk Space, Free Disk Space, Disk Space Utilization
    """
    data = await get_system_info()
    return data


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')