bl_info = {
    "name": "Blender to Cascadeur",
    "author": "Ri x Claude",
    "version": (3, 0, 0),  
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > B2C",
    "description": "Mark keyframes for Cascadeur export with extended features",
    "category": "Animation",
}

import bpy
import sys
import os
import importlib

# Define addon preferences class first to avoid registration issues
class BTCAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    csc_exe_path: bpy.props.StringProperty(
        name="Cascadeur executable",
        subtype="FILE_PATH",
        default="",
        update=lambda self, context: update_csc_exe_path(self, context)
    )

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=False)
        row = col.row()
        row.prop(self, "csc_exe_path")
        row = col.row()
        row.operator(
            "btc.install_cascadeur_addon",
            text="Install Cascadeur Add-on",
            icon="MODIFIER",
        )

def update_csc_exe_path(self, context):
    """Function called when Cascadeur path changes."""
    # Check if path is valid
    try:
        from .utils.csc_handling import CascadeurHandler
        handler = CascadeurHandler()
        
        if handler.is_csc_exe_path_valid:
            # Automatically install necessary files
            try:
                bpy.ops.btc.install_cascadeur_addon()
            except Exception:
                # Might be in the process of initializing the addon, skip
                pass
    except Exception:
        pass

# Import modules directly with better error handling
from . import ui
from .operators import (
    keyframe_operators,
    export_operators, 
    import_operators,
    clean_operators,
    csc_operators
)
from .utils import (
    file_utils,
    file_watcher,
    preferences
)

# Reload modules if already imported
if "bpy" in locals():
    # Try to reload modules
    try:
        importlib.reload(ui)
        ui.reload_modules()
        
        importlib.reload(keyframe_operators)
        importlib.reload(export_operators)
        importlib.reload(import_operators)
        importlib.reload(clean_operators)
        importlib.reload(csc_operators)
        
        importlib.reload(file_utils)
        importlib.reload(file_watcher)
        importlib.reload(preferences)
    except Exception as e:
        print(f"Error reloading modules: {e}")

# Create list of all classes to register
classes = []
# Register PropertyGroup first
classes.append(keyframe_operators.KeyframeItem)
# Then register UI classes
classes.extend(ui.classes)
# Next register Operator classes
classes.extend(keyframe_operators.classes)
classes.extend(export_operators.classes)
classes.extend(import_operators.classes)
classes.extend(clean_operators.classes)
classes.extend(csc_operators.classes)
# Next register Preference classes
classes.extend(preferences.classes)
# Finally register addon preference class
classes.append(BTCAddonPreferences)

def register():
    # Register classes
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            print(f"Error registering class {cls.__name__}: {e}")
    
    # Register scene properties
    try:
        bpy.types.Scene.btc_keyframes = bpy.props.CollectionProperty(
            type=keyframe_operators.KeyframeItem
        )
        bpy.types.Scene.btc_keyframe_index = bpy.props.IntProperty(name="Keyframe Index")
        
        # Register armature properties
        bpy.types.Scene.btc_armature = bpy.props.PointerProperty(
            type=bpy.types.Object,
            name="Armature",
            description="Selected armature for export",
            poll=lambda self, obj: obj.type == 'ARMATURE'
        )
    except Exception as e:
        print(f"Error registering properties: {e}")
    
    # Register handlers for file watcher
    try:
        bpy.app.handlers.load_post.append(file_watcher.load_handler)
    except Exception as e:
        print(f"Error registering file watcher: {e}")

def unregister():
    # Remove handlers
    try:
        if file_watcher.load_handler in bpy.app.handlers.load_post:
            bpy.app.handlers.load_post.remove(file_watcher.load_handler)
    except Exception as e:
        print(f"Error removing handlers: {e}")
    
    # Stop file watcher if running
    try:
        if hasattr(bpy.types, "WindowManager") and hasattr(bpy.types.WindowManager, "btc_file_watcher"):
            watcher = bpy.context.window_manager.btc_file_watcher
            if watcher:
                watcher.stop()
            del bpy.types.WindowManager.btc_file_watcher
    except Exception as e:
        print(f"Error stopping file watcher: {e}")
    
    # Unregister scene properties
    try:
        del bpy.types.Scene.btc_armature
        del bpy.types.Scene.btc_keyframe_index
        del bpy.types.Scene.btc_keyframes
    except Exception as e:
        print(f"Error unregistering properties: {e}")
    
    # Unregister classes in reverse order
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            print(f"Error unregistering class {cls.__name__}: {e}")

if __name__ == "__main__":
    register()