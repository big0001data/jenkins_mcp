from typing import Any
from mcp.server.fastmcp import FastMCP
from fetch_info import get_system_info

# Initialize FastMCP server
mcp = FastMCP("sysinfo")

# Jenkins job list API endpoint
# Jenkins provides information in JSON format via the /api/json endpoint.
# Adding 'tree=jobs[name]' optimizes the response to only include job names.
# The URL-encoded `jobs%5Bname%5D` can be used as `jobs[name]` in Python, and requests will handle encoding.
api_url = f"{jenkins_url}/api/json?tree=jobs[name]"

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

# The job list request uses the GET method.
# No request body or Content-Type header is required.
@mcp.tool("Get Jenkins Job List")
def get_jenkins_job_list():
    # Send GET request
    try:
        print("Fetching Jenkins job list...")
        response = requests.get(  # Use GET instead of POST.
            api_url,
            auth=(username, api_token),
            # requests library follows redirects by default.
            # verify=False skips SSL certificate verification (not needed for HTTP).
        )

        # Check response status code
        if response.status_code == 200:
            print("Successfully fetched Jenkins job list.")
            # Parse JSON response
            jobs_data = response.json()

            # Check for "jobs" key in response and print job list
            if "jobs" in jobs_data:
                print("\n--- Jenkins Job List ---")
                if jobs_data["jobs"]:
                    for job in jobs_data["jobs"]:
                        # Print only the job_list provided as "name".
                        print(f"- {job['name']}")
                else:
                    print("No jobs found in Jenkins.")
            else:
                print("Could not find 'jobs' key in response. Check Jenkins API response format.")
                print(f"Full response: {jobs_data}")
        else:
            print(f"Error fetching job list: {response.status_code} - {response.text}")
            print("Jenkins response details:")
            print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

# New tool: Provide Jenkins server URL
@mcp.tool("Get Jenkins Server URL", description="Returns the Jenkins server URL. (젠킨스 서버의 주소를 반환합니다.)")
def get_jenkins_server_url():
    """Returns the Jenkins server URL."""
    return jenkins_url

# New tool: Check Jenkins server connection
@mcp.tool("Check Jenkins Server Connection", description="Checks if the Jenkins server is accessible with the configured credentials.")
def check_jenkins_server_connection():
    """Attempts to connect to the Jenkins server and returns whether the connection is successful."""
    try:
        response = requests.get(
            jenkins_url,
            auth=(username, api_token),
            timeout=10  # Short timeout for quick feedback
        )
        if response.status_code == 200:
            return f"Successfully connected to Jenkins server at {jenkins_url} as user '{username}'."
        elif response.status_code == 403:
            return f"Failed to connect: Authentication failed (403 Forbidden). Check your username or API token."
        else:
            return f"Failed to connect: Received status code {response.status_code}. Response: {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Connection error: {e}"

@mcp.tool("Create Jenkins Job", description="Creates a new Jenkins job with the given name and configuration XML file path.")
def jenkins_server_create_job(job_name: str, job_config_path: str) -> str:
    """
    Creates a new Jenkins job using the provided job name and job configuration XML file path.
    Args:
        job_name (str): The name of the new Jenkins job to create.
        job_config_path (str): The file path to the Jenkins job configuration XML.
    Returns:
        str: Success or error message.
    """
    if not os.path.exists(job_config_path):
        return f"Job config file not found: {job_config_path}"
    try:
        with open(job_config_path, "r") as f:
            job_config_xml = f.read()
        api_url = f"{jenkins_url}/createItem?name={job_name}"
        headers = {"Content-Type": "application/xml"}
        response = requests.post(
            api_url,
            auth=(username, api_token),
            headers=headers,
            data=job_config_xml
        )
        if response.status_code == 200:
            return f"Job '{job_name}' created successfully."
        elif response.status_code == 400 and "A job already exists" in response.text:
            return f"Job '{job_name}' already exists."
        else:
            return f"Error creating job: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

@mcp.tool("Build Jenkins Job", description="Triggers a build for the specified Jenkins job name.")
def jenkins_server_build_job(job_name: str) -> str:
    """
    Triggers a build for the specified Jenkins job.
    Args:
        job_name (str): The name of the Jenkins job to build.
    Returns:
        str: Success or error message.
    """
    api_url = f"{jenkins_url}/job/{job_name}/build"
    try:
        response = requests.post(
            api_url,
            auth=(username, api_token),
            timeout=10
        )
        if response.status_code in [200, 201, 302]:
            msg = f"Job '{job_name}' build triggered successfully."
            if response.status_code == 302 and 'Location' in response.headers:
                msg += f" Redirected to: {response.headers['Location']}"
            return msg
        else:
            return f"Error triggering build for job '{job_name}': {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

def ollama_message_to_lc_message(msg):
    # Convert Ollama Message to LangChain message if needed
    if hasattr(msg, "role"):
        if msg.role == "assistant":
            return AIMessage(content=msg.content)
        elif msg.role == "user":
            return HumanMessage(content=msg.content)
        elif msg.role == "system":
            return SystemMessage(content=msg.content)
    return msg

def get_streaming_callback():
    accumulated_text = []
    accumulated_tool_info = []

    def callback_func(data: Any):
        nonlocal accumulated_text, accumulated_tool_info

        if isinstance(data, dict):
            agent_step_key = next(
                (k for k in data if isinstance(data.get(k), dict) and "messages" in data[k]), None
            )
            if agent_step_key:
                messages = data[agent_step_key].get("messages", [])
                for message in messages:
                    message = ollama_message_to_lc_message(message)  # 변환 적용
                    # 이하 기존 코드 유지

if __name__ == "__main__":
    # Start the MCP server with stdio transport
    mcp.run(transport="stdio")

