import bpy
import os
from bpy.types import AddonPreferences
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty

class BTCAddonPreferences(AddonPreferences):
    bl_idname = __package__.split(".")[0]
    
    # Đường dẫn đến Cascadeur executable
    csc_exe_path: StringProperty(
        name="Cascadeur Executable",
        subtype='FILE_PATH',
        description="Path to Cascadeur executable"
    )
    
    # Thư mục dùng cho trao đổi file
    exchange_folder: StringProperty(
        name="Exchange Folder",
        subtype='DIR_PATH',
        description="Folder used for file exchange between Blender and Cascadeur"
    )
    
    # Tùy chọn vị trí lưu file
    exchange_folder_location: EnumProperty(
        name="Exchange Folder Location",
        items=[
            ('CASCADEUR', "Cascadeur Folder", "Create a subfolder in Cascadeur installation directory"),
            ('ADDON', "Add-on Folder", "Create a subfolder in the add-on directory"),
            ('CUSTOM', "Custom Location", "Use a custom folder location"),
            ('TEMP', "Temporary Folder", "Use system's temporary folder")
        ],
        default='TEMP',
        description="Choose where to store exchange files"
    )
    
    # Thời gian tự động dọn dẹp các file cũ
    cleanup_interval: IntProperty(
        name="Cleanup Interval (hours)",
        description="Automatically clean up processed trigger files older than this many hours",
        default=24,
        min=1,
        max=168
    )
    
    # Tự động mở Cascadeur khi export
    auto_open_cascadeur: BoolProperty(
        name="Auto-open Cascadeur",
        description="Automatically open Cascadeur when exporting",
        default=False
    )
    
    # Port cho socket communication (fallback)
    socket_port: IntProperty(
        name="Socket Port",
        description="Port for socket communication (fallback method)",
        default=48152,
        min=1024,
        max=65535
    )
    
    def draw(self, context):
        layout = self.layout
        
        # Cascadeur Executable
        box = layout.box()
        box.label(text="Cascadeur Settings:")
        row = box.row()
        row.prop(self, "csc_exe_path")
        
        # Exchange Folder
        box = layout.box()
        box.label(text="File Exchange Settings:")
        row = box.row()
        row.prop(self, "exchange_folder_location")
        
        # Only show custom folder field if CUSTOM is selected
        if self.exchange_folder_location == 'CUSTOM':
            row = box.row()
            row.prop(self, "exchange_folder")
        
        # Cleanup settings
        row = box.row()
        row.prop(self, "cleanup_interval")
        
        # Options
        box = layout.box()
        box.label(text="Options:")
        row = box.row()
        row.prop(self, "auto_open_cascadeur")
        
        # Socket settings (fallback)
        box = layout.box()
        box.label(text="Advanced Settings:")
        row = box.row()
        row.prop(self, "socket_port")
        
        # Installation
        box = layout.box()
        box.label(text="Cascadeur Add-on Installation:")
        row = box.row()
        row.operator("btc.install_cascadeur_addon", text="Install Cascadeur Add-on")
        
        # Info
        box = layout.box()
        box.label(text="How to use:")
        col = box.column()
        col.label(text="1. Set the Cascadeur executable path")
        col.label(text="2. Set the exchange folder location")
        col.label(text="3. Install the add-on in Cascadeur")
        col.label(text="4. Start using the B2C panel in the 3D viewport")

# Danh sách các lớp để đăng ký
classes = [
    BTCAddonPreferences,
]

def get_preferences(context):
    """Helper function to get add-on preferences"""
    return context.preferences.addons[__package__.split(".")[0]].preferences

def get_exchange_folder(context):
    """Get the exchange folder path based on preferences"""
    prefs = get_preferences(context)
    
    if prefs.exchange_folder_location == 'CUSTOM' and prefs.exchange_folder:
        return prefs.exchange_folder
    
    if prefs.exchange_folder_location == 'CASCADEUR' and prefs.csc_exe_path:
        # Get Cascadeur directory
        from .csc_handling import CascadeurHandler
        csc_dir = CascadeurHandler().csc_dir
        return os.path.join(csc_dir, "exchange")
    
    if prefs.exchange_folder_location == 'ADDON':
        # Get addon directory
        addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(addon_dir, "exchange")
    
    # Default to temp folder
    import tempfile
    return os.path.join(tempfile.gettempdir(), "blender_to_cascadeur_exchange")

def get_port_number():
    """Get the port number from preferences"""
    import configparser
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "settings.cfg")
    config = configparser.ConfigParser()
    
    if os.path.exists(config_path):
        config.read(config_path)
        if config.has_section("Addon Settings") and config.has_option("Addon Settings", "port"):
            return config.getint("Addon Settings", "port")
    
    # Default port
    return 48152