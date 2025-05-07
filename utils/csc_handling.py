import subprocess
import platform
import os
import bpy

# Hàm cục bộ thay vì import từ file_utils để tránh vòng lặp import
def file_exists(file_path):
    """Kiểm tra xem file có tồn tại hay không."""
    return os.path.exists(file_path)

def get_default_csc_exe_path():
    """
    Returns the default Cascadeur executable path based on the operating system.
    """
    system = platform.system()
    if system == "Windows":
        paths = [
            r"C:\Program Files\Cascadeur\cascadeur.exe",
            r"C:\Program Files (x86)\Cascadeur\cascadeur.exe"
        ]
        for path in paths:
            if file_exists(path):
                return path
    elif system == "Darwin":  # macOS
        paths = [
            r"/Applications/Cascadeur.app",
            r"~/Applications/Cascadeur.app"
        ]
        for path in paths:
            expanded_path = os.path.expanduser(path)
            if file_exists(expanded_path):
                return expanded_path
    elif system == "Linux":
        paths = [
            r"/opt/cascadeur/cascadeur",
            r"~/cascadeur/cascadeur"
        ]
        for path in paths:
            expanded_path = os.path.expanduser(path)
            if file_exists(expanded_path):
                return expanded_path
    
    return ""

class CascadeurHandler:
    @property
    def csc_exe_path_addon_preference(self):
        """
        Get the set Cascadeur executable path from the addon's preferences.
        """
        preferences = bpy.context.preferences
        addon_prefs = preferences.addons[__package__.split(".")[0]].preferences
        return addon_prefs.csc_exe_path

    @property
    def csc_dir(self):
        """
        Get the root directory of Cascadeur installation.
        """
        if self.is_csc_exe_path_valid:
            if platform.system() == "Darwin":  # macOS
                return os.path.dirname(self.csc_exe_path_addon_preference)
            else:
                return os.path.dirname(self.csc_exe_path_addon_preference)

    @property
    def is_csc_exe_path_valid(self):
        """
        Check if the Cascadeur executable path is valid.
        """
        csc_path = self.csc_exe_path_addon_preference
        return True if csc_path and file_exists(csc_path) else False

    @property
    def commands_path(self):
        """
        Get the path to the Cascadeur commands directory.
        """
        if platform.system() == "Darwin":  # macOS
            resources_dir = os.path.join(self.csc_dir, "Contents", "MacOS", "resources")
        else:
            resources_dir = os.path.join(self.csc_dir, "resources")
        
        return os.path.join(resources_dir, "scripts", "python", "commands")

    def start_cascadeur(self):
        """
        Start Cascadeur using the specified executable path.
        """
        csc_path = self.csc_exe_path_addon_preference
        subprocess.Popen([csc_path])

    def execute_csc_command(self, command):
        """
        Execute a Cascadeur command using the specified executable path.
        """
        subprocess.Popen([self.csc_exe_path_addon_preference, "--run-script", command])