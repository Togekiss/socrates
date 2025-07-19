import datetime
import sys
import os
import subprocess
import json
import re
from collections import deque

GRAY = '\033[90m'
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[34m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
RESET = '\033[0m'

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
save_to_json(data, file_path)

    Function to write a JSON file.
    
"""
def save_to_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

"""
clean(message)

    Function to remove ANSI escape sequences from a string and remove leading and trailing newlines.
"""
def clean(message):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    no_ansi = ansi_escape.sub('', message)

    return no_ansi.lstrip('\n').rstrip('\n')

"""
log( level, message)

    Centralized function to handle information messages.
    
    It prints the message if the corresponding flag is set in the constants module.
    It also writes the message to a log file if the LOG flag is set.

    Args:
        level (str): The level of the message (info, debug, console).
        message (str): The message to be logged.

"""
def log(level="base", message=""):
    set_path()
    from res import constants as c

    if level == "base":
        print(GREEN + message + RESET)
    elif level == "info":
        if c.INFO:
            print(CYAN + message + RESET)
    elif level == "debug":
        if c.DEBUG:
            print(BLUE + message + RESET)
    elif level == "console":
        if c.CONSOLE:
            print(GRAY + message, end="")
    
    level = "console" if level == "consolelog" else level
    
    if c.LOG:
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        with open(c.LOG_FILE, "a", encoding="utf-8") as file:
            file.write(f"[{timestamp}]{level}: {clean(message)}\n")

"""
 run_command(command: str, show_lines: int = 0)

    Run a shell command, stream its output in real time, and return the full output.
    
    Args:
        command (str): The shell command to run.
        show_lines (int, optional): The number of lines to clear before streaming output.
    
    Returns:
        tuple[int, str]: A tuple containing the return code and the full output.
"""
def run_command(command: str, show_lines: int = None):
    set_path()
    from res import constants as c

    log("console", f"# RUNNING CONSOLE COMMAND #\n")
    log("console", f"> {MAGENTA}{command}{GRAY}\n")

    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    full_output = []
    tail_buffer = deque(maxlen=show_lines if show_lines else 0)

    try:
        for line in process.stdout:
            full_output.append(line)  # Collect output for return

            if show_lines and c.CONSOLE:
                # Clear previous lines (simulate dynamic overwrite)
                print("\033[F" * len(tail_buffer), end="")  # Move cursor up

                tail_buffer.append(line)
                
                for l in tail_buffer:
                    print(f">\t{l.strip():<80}")  # Print line padded to overwrite
                    log("consolelog", f">\t{l}")
            else:
                log("console", f">\t{line}")
            
    except KeyboardInterrupt:
        log("\nCommand interrupted by user.")
        process.terminate()

    process.wait()

    log("console", f"\n{RESET}# END OF CONSOLE COMMAND #\n\n")
    return process.returncode, ''.join(full_output)
