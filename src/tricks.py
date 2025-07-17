import sys
import os
import subprocess
import json
import res.constants as c

################ File summary #################

"""

This module holds a handful of useful functions and helpers.

"""

################ Functions #################
"""
debug(message), console(message)

    Functions to print messages to the console if DEBUG or CONSOLE is set to True.

"""
def debug(message):
    if c.DEBUG:
        print(message)

def console(message):
    if c.CONSOLE:
        print(message)

"""
save_to_json(data, file_path)

    Function to write a JSON file.
    
"""
def save_to_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


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
    ANSI_BLUE = '\033[94m'
    ANSI_RESET = '\033[0m'

    console(f"# RUNNING CONSOLE COMMAND #")
    console(f"{ANSI_GRAY}> {ANSI_BLUE}{command}{ANSI_GRAY} <\n")

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
            console(f"\t> {line}", end='')  # Stream output to console
            full_output.append(line)  # Collect output for return
    except KeyboardInterrupt:
        print("\nCommand interrupted by user.")
        process.terminate()

    process.wait()

    console(f"\n{ANSI_RESET}# END OF CONSOLE COMMAND #\n")
    return process.returncode, ''.join(full_output)
