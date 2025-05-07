import bpy
import os  # Thêm import os
from bpy.types import Panel, UIList

# Tạo lớp cơ sở cho tất cả các panel
class PanelBasics:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "B2C"  # Tên trên N-panel

# Panel chính: Blender to Cascadeur
class BTC_PT_BlenderToCascadeurPanel(PanelBasics, Panel):
    bl_idname = "BTC_PT_blender_to_cascadeur"
    bl_label = "Blender to Cascadeur"
    
    def draw_header(self, context):
        self.layout.label(text="", icon="EXPORT")
    
    def draw(self, context):
        layout = self.layout
        # Main panel is empty, sub-panels will be used

# Panel con - Character Selection
class BTC_PT_CharacterPanel(PanelBasics, Panel):
    bl_idname = "BTC_PT_character"
    bl_label = "Choose Character"
    bl_parent_id = "BTC_PT_blender_to_cascadeur"
    
    def draw(self, context):
        layout = self.layout
        
        # Hiển thị thông tin armature
        box = layout.box()
        row = box.row()
        row.alignment = 'CENTER'
        row.label(text="Armature Info")
        
        # Hiển thị thông tin armature đã chọn
        if context.scene.btc_armature:
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text=f"Selected: {context.scene.btc_armature.name}")
            
            # Display animation info if available
            if context.scene.btc_armature.animation_data and context.scene.btc_armature.animation_data.action:
                action = context.scene.btc_armature.animation_data.action
                row = box.row()
                row.alignment = 'CENTER'
                row.label(text=f"Animation: {action.name}")
                
                # Display frame range
                start_frame, end_frame = self.get_action_frame_range(action)
                row = box.row()
                row.alignment = 'CENTER'
                row.label(text=f"Frames: {start_frame} - {end_frame}")
        else:
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text="No armature selected")
        
        # Nút chọn armature
        row = layout.row()
        row.operator("btc.pick_armature", text="Pick Armature", icon="ARMATURE_DATA")
        
    def get_action_frame_range(self, action):
        """Get frame range of an action"""
        start_frame = float('inf')
        end_frame = float('-inf')
        
        for fcurve in action.fcurves:
            for keyframe in fcurve.keyframe_points:
                frame = keyframe.co[0]
                start_frame = min(start_frame, frame)
                end_frame = max(end_frame, frame)
                
        # Convert to int if valid range found
        if start_frame != float('inf') and end_frame != float('-inf'):
            return (int(start_frame), int(end_frame))
        
        # Fallback to scene range
        return (0, 0)

# Panel con - Keyframe Markers
class BTC_PT_KeyframeMarkersPanel(PanelBasics, Panel):
    bl_idname = "BTC_PT_keyframe_markers"
    bl_label = "Keyframe Markers"
    bl_parent_id = "BTC_PT_blender_to_cascadeur"
    
    @classmethod
    def poll(cls, context):
        return context.scene.btc_armature is not None
    
    def draw(self, context):
        layout = self.layout
        
        # Hiển thị frame hiện tại
        row = layout.row()
        row.label(text=f"Current Frame: {context.scene.frame_current}")
        
        # Nút đánh dấu và xóa keyframe hiện tại
        row = layout.row(align=True)
        row.operator("btc.mark_current_keyframe", text="Mark Current", icon="KEYFRAME")
        row.operator("btc.clear_current_keyframe", text="Clear Current", icon="KEYFRAME_HLT")
        
        # Nút đánh dấu và xóa tất cả keyframe
        row = layout.row(align=True)
        row.operator("btc.mark_all_keyframes", text="Mark All", icon="KEYFRAME_HLT")
        row.operator("btc.clear_all_keyframes", text="Clear All", icon="X")

# Panel con - Marked Keyframes
class BTC_PT_MarkedKeyframesPanel(PanelBasics, Panel):
    bl_idname = "BTC_PT_marked_keyframes"
    bl_label = "Marked Keyframes"
    bl_parent_id = "BTC_PT_blender_to_cascadeur"
    
    @classmethod
    def poll(cls, context):
        return context.scene.btc_armature is not None and len(context.scene.btc_keyframes) > 0
    
    def draw(self, context):
        layout = self.layout
        
        # Display marked keyframe count
        marked_count = sum(1 for item in context.scene.btc_keyframes if item.is_marked)
        total_count = len(context.scene.btc_keyframes)
        
        row = layout.row()
        row.label(text=f"Marked: {marked_count} / {total_count} keyframes")
        
        # UIList with checkbox
        row = layout.row()
        row.template_list(
            "BTC_UL_KeyframeList", "", 
            context.scene, "btc_keyframes", 
            context.scene, "btc_keyframe_index", 
            rows=6
        )
        
        # Jump to selected keyframe
        if total_count > 0 and context.scene.btc_keyframe_index >= 0 and context.scene.btc_keyframe_index < total_count:
            selected_frame = context.scene.btc_keyframes[context.scene.btc_keyframe_index].frame
            row = layout.row()
            op = row.operator("screen.frame_jump", text=f"Jump to Frame {selected_frame}", icon="TIME")
            op.end = False

# Panel con - Export
class BTC_PT_ExportPanel(PanelBasics, Panel):
    bl_idname = "BTC_PT_export"
    bl_label = "Export"
    bl_parent_id = "BTC_PT_blender_to_cascadeur"
    
    @classmethod
    def poll(cls, context):
        return context.scene.btc_armature is not None
    
    def draw(self, context):
        layout = self.layout
        
        # Check if any keyframes are marked
        has_marked_keyframes = False
        for item in context.scene.btc_keyframes:
            if item.is_marked:
                has_marked_keyframes = True
                break
        
        # Display warning if no keyframes are marked
        if not has_marked_keyframes:
            box = layout.box()
            box.label(text="No keyframes are marked", icon="ERROR")
            box.label(text="Mark keyframes before exporting")
        
        # Export objects
        row = layout.row()
        row.scale_y = 1.2
        row.operator("btc.export_object", text="Export Object", icon="OBJECT_DATA")
        
        # Export animation
        row = layout.row()
        row.scale_y = 1.2
        row.enabled = has_marked_keyframes
        row.operator("btc.export_animation", text="Export Animation", icon="ARMATURE_DATA")

# Panel chính: Cascadeur Cleaner
class BTC_PT_CascadeurCleanerPanel(PanelBasics, Panel):
    bl_idname = "BTC_PT_cascadeur_cleaner"
    bl_label = "Cascadeur Cleaner"
    
    def draw_header(self, context):
        self.layout.label(text="", icon="BRUSH_DATA")
    
    def draw(self, context):
        layout = self.layout
        
        # Cascadeur executable status
        from ..utils.csc_handling import CascadeurHandler
        handler = CascadeurHandler()
        
        if handler.is_csc_exe_path_valid:
            box = layout.box()
            box.label(text="Cascadeur Found", icon="CHECKMARK")
            box.label(text=os.path.basename(handler.csc_exe_path_addon_preference))
        else:
            box = layout.box()
            box.label(text="Cascadeur Not Found", icon="ERROR")
            box.label(text="Set path in Addon Preferences")
            box.operator("preferences.addon_show", text="Open Preferences").module=__package__.split(".")[0]
        
        # Nút mở Cascadeur
        row = layout.row()
        row.scale_y = 1.2
        row.enabled = handler.is_csc_exe_path_valid
        row.operator("btc.open_cascadeur", text="Open Cascadeur", icon="MESH_UVSPHERE")
        
        # Nút import FBX và JSON
        col = layout.column(align=True)
        col.enabled = handler.is_csc_exe_path_valid
        
        row = col.row(align=True)
        row.operator("btc.import_fbx", text="Import FBX", icon="IMPORT")
        row.operator("btc.import_json", text="Import JSON", icon="FILE_TEXT")
        
        # Nút Clean Keyframes
        row = col.row()
        row.operator("btc.clean_keyframes_cascadeur", text="Clean Keyframes", icon="BRUSH_DATA")

# Panel chính: Cascadeur to Blender
class BTC_PT_CascadeurToBlenderPanel(PanelBasics, Panel):
    bl_idname = "BTC_PT_cascadeur_to_blender"
    bl_label = "Cascadeur to Blender"
    
    def draw_header(self, context):
        self.layout.label(text="", icon="IMPORT")
    
    def draw(self, context):
        layout = self.layout
        
        # Cascadeur executable status
        from ..utils.csc_handling import CascadeurHandler
        handler = CascadeurHandler()
        
        # Import from Cascadeur
        col = layout.column()
        col.enabled = handler.is_csc_exe_path_valid
        
        row = col.row()
        row.scale_y = 1.2
        row.operator("btc.import_scene", text="Import Scene", icon="SCENE_DATA")
        
        row = col.row()
        row.scale_y = 1.2
        row.operator("btc.import_all_scenes", text="Import All Scenes", icon="DOCUMENTS")
        
        # Clean Keyframes in Blender
        box = layout.box()
        box.label(text="Cleanup Tools:", icon="BRUSH_DATA")
        
        row = box.row()
        row.operator("btc.clean_keyframes", text="Clean Keyframes", icon="BRUSH_DATA")

# Đăng ký UIList cho phần Marked Keyframes
class BTC_UL_KeyframeList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.7)
            split.label(text=f"Frame: {item.frame}")
            
            # Tạo checkbox cho trạng thái đánh dấu
            checkbox_icon = 'CHECKBOX_HLT' if item.is_marked else 'CHECKBOX_DEHLT'
            split.prop(item, "is_marked", text="", icon=checkbox_icon, emboss=False)
            
            # Add jump to frame button
            op = split.operator("screen.frame_jump", text="", icon="TIME")
            op.end = False
        
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text=str(item.frame))
            layout.prop(item, "is_marked", text="")