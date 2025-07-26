import platform
import psutil
import GPUtil
import asyncio

async def get_system_info():
    output = []

    system_info = platform.uname()
    output.append("System Information:")
    output.append(f"System: {system_info.system}")
    output.append(f"Node Name: {system_info.node}")
    output.append(f"Release: {system_info.release}")
    output.append(f"Version: {system_info.version}")
    output.append(f"Machine: {system_info.machine}")
    output.append(f"Processor: {system_info.processor}")

    cpu_info = platform.processor()
    cpu_count = psutil.cpu_count(logical=False)
    logical_cpu_count = psutil.cpu_count(logical=True)

    output.append("\nCPU Information:")
    output.append(f"Processor: {cpu_info}")
    output.append(f"Physical Cores: {cpu_count}")
    output.append(f"Logical Cores: {logical_cpu_count}")

    memory_info = psutil.virtual_memory()

    output.append("\nMemory Information:")
    output.append(f"Total Memory: {memory_info.total} bytes")
    output.append(f"Available Memory: {memory_info.available} bytes")
    output.append(f"Used Memory: {memory_info.used} bytes")
    output.append(f"Memory Utilization: {memory_info.percent}%")

    disk_info = psutil.disk_usage('/')

    output.append("\nDisk Information:")
    output.append(f"Total Disk Space: {disk_info.total} bytes")
    output.append(f"Used Disk Space: {disk_info.used} bytes")
    output.append(f"Free Disk Space: {disk_info.free} bytes")
    output.append(f"Disk Space Utilization: {disk_info.percent}%")

    # gpus = GPUtil.getGPUs()

    # if not gpus:
    #     output.append("No GPU detected.")
    # else:
    #     for i, gpu in enumerate(gpus):
    #         output.append(f"\nGPU {i + 1} Information:")
    #         output.append(f"ID: {gpu.id}")
    #         output.append(f"Name: {gpu.name}")
    #         output.append(f"Driver: {gpu.driver}")
    #         output.append(f"GPU Memory Total: {gpu.memoryTotal} MB")
    #         output.append(f"GPU Memory Free: {gpu.memoryFree} MB")
    #         output.append(f"GPU Memory Used: {gpu.memoryUsed} MB")
    #         output.append(f"GPU Load: {gpu.load * 100}%")
    #         output.append(f"GPU Temperature: {gpu.temperature}°C")

    return "\n".join(output)

if __name__ == "__main__":
    res = asyncio.run(get_system_info())
    print(res)