bl_info = {
    "name": "Blender to Cascadeur",
    "author": "Ri x Claude",
    "version": (2, 3, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > B2C",
    "description": "Mark keyframes for Cascadeur export with extended features",
    "category": "Animation",
}

import bpy
import sys
import os

# Define addon preferences class first to avoid registration issues
class BTCAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    csc_exe_path: bpy.props.StringProperty(
        name="Cascadeur executable",
        subtype="FILE_PATH",
        default="",
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

# Import and register modules
if "bpy" in locals():
    import importlib
    # Import module ui
    from . import ui
    importlib.reload(ui)
    
    # Import other modules
    from . operators import (
        keyframe_operators,
        export_operators,
        import_operators,
        clean_operators,
        csc_operators
    )
    importlib.reload(keyframe_operators)
    importlib.reload(export_operators)
    importlib.reload(import_operators)
    importlib.reload(clean_operators)
    importlib.reload(csc_operators)
    
    from . utils import (
        file_utils,
        file_watcher,
        preferences
    )
    importlib.reload(file_utils)
    importlib.reload(file_watcher)
    importlib.reload(preferences)
else:
    # First time import
    from . import ui
    from . operators import (
        keyframe_operators,
        export_operators,
        import_operators,
        clean_operators,
        csc_operators
    )
    from . utils import (
        file_utils,
        file_watcher,
        preferences
    )

# Create list of all classes to register
classes = []
classes.extend(ui.classes)
classes.extend(keyframe_operators.classes)
classes.extend(export_operators.classes)
classes.extend(import_operators.classes)
classes.extend(clean_operators.classes)
classes.extend(csc_operators.classes)
classes.extend(preferences.classes)

# Add BTCAddonPreferences to the list of classes
classes.append(BTCAddonPreferences)

def update_csc_exe_path(self, context):
    """Function called when Cascadeur path changes."""
    # Check if path is valid
    from .utils.csc_handling import CascadeurHandler
    handler = CascadeurHandler()
    
    if handler.is_csc_exe_path_valid:
        # Automatically install necessary files
        try:
            bpy.ops.btc.install_cascadeur_addon()
        except:
            # Might be in the process of initializing the addon, skip
            pass

def register():
    # Register classes
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Register scene properties
    bpy.types.Scene.btc_keyframes = bpy.props.CollectionProperty(type=keyframe_operators.KeyframeItem)
    bpy.types.Scene.btc_keyframe_index = bpy.props.IntProperty(name="Keyframe Index")
    
    # Register armature properties
    bpy.types.Scene.btc_armature = bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Armature",
        description="Selected armature for export",
        poll=lambda self, obj: obj.type == 'ARMATURE'
    )
    
    # Register handlers for file watcher
    bpy.app.handlers.load_post.append(file_watcher.load_handler)

def unregister():
    # Remove handlers
    if file_watcher.load_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(file_watcher.load_handler)
    
    # Stop file watcher if running
    if hasattr(bpy.types, "WindowManager") and hasattr(bpy.types.WindowManager, "btc_file_watcher"):
        watcher = bpy.context.window_manager.btc_file_watcher
        if watcher:
            watcher.stop()
        del bpy.types.WindowManager.btc_file_watcher
    
    # Unregister scene properties
    del bpy.types.Scene.btc_armature
    del bpy.types.Scene.btc_keyframe_index
    del bpy.types.Scene.btc_keyframes
    
    # Unregister classes in reverse order
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
