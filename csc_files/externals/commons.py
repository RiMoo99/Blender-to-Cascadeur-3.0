import csc
import tempfile
import os


def set_export_settings(preferences: dict = None) -> csc.fbx.FbxSettings:
    """
    Setting the fbx export settings in Cascadeur.
    
    Args:
        preferences: Dictionary with settings
    
    Returns:
        FbxSettings object
    """
    if preferences is None:
        preferences = {}
        
    settings = csc.fbx.FbxSettings()
    settings.mode = csc.fbx.FbxSettingsMode.Binary

    if preferences.get("euler_filter", False):
        settings.apply_euler_filter = True
    else:
        settings.apply_euler_filter = False
        
    if preferences.get("up_axis") == "Z":
        settings.up_axis = csc.fbx.FbxSettingsAxis.Z
    else:
        settings.up_axis = csc.fbx.FbxSettingsAxis.Y
        
    if preferences.get("bake_animation", True):
        settings.bake_animation = True
    else:
        settings.bake_animation = False
        
    return settings


def get_export_path(scene_name: str) -> str:
    """
    FBX export path in the temp folder using the scene name.
    
    Args:
        scene_name: Name of the Cascadeur scene
    
    Returns:
        FBX export path
    """
    temp_dir = tempfile.gettempdir()
    file_name = scene_name.replace(".casc", "") + ".fbx"
    return os.path.join(temp_dir, file_name)


def ensure_dir_exists(directory: str) -> str:
    """
    Đảm bảo thư mục tồn tại, tạo nếu không có.
    
    Args:
        directory: Đường dẫn thư mục
    
    Returns:
        Đường dẫn thư mục
    """
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    return directory