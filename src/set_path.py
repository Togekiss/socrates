import sys
import os

################ File summary #################

"""

This module only exists to set the root path to the project folder for scripts that reside in subfolders.

Main function: set_path()

    This function sets the path to the project folder.

"""

################ Main function #################

def set_path():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.append(project_root)
