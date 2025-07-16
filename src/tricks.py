import sys
import os
import subprocess

################ File summary #################

"""

This module holds a handful of useful functions and helpers.

"""

################ Functions #################

"""
set_path()

    This function sets the path to the project folder.

"""
def set_path():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.append(project_root)


"""
 run_command(command: str)

    Run a shell command, stream its output in real time, and return the full output.
    
    Args:
        command (str): The shell command to run.
    
    Returns:
        tuple[int, str]: A tuple containing the return code and the full output.
"""
def run_command(command: str):
    
    ANSI_GRAY = '\033[90m'
    ANSI_RESET = '\033[0m'

    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    full_output = []

    try:
        for line in process.stdout:
            print(f"{ANSI_GRAY}> {line}{ANSI_RESET}", end='')  # Stream output to console
            full_output.append(line)  # Collect output for return
    except KeyboardInterrupt:
        print("\nCommand interrupted by user.")
        process.terminate()

    process.wait()
    return process.returncode, ''.join(full_output)
