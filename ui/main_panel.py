import bpy
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
        row.scale_y = 0.5
        row.scale_x = 1.5
        row.label(text="Armature Info")
        
        # Hiển thị thông tin armature đã chọn
        if context.scene.btc_armature:
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text=f"Selected: {context.scene.btc_armature.name}")
        
        # Nút chọn armature
        row = layout.row()
        row.operator("btc.pick_armature", text="Pick Armature", icon="EYEDROPPER")

# Panel con - Keyframe Markers
class BTC_PT_KeyframeMarkersPanel(PanelBasics, Panel):
    bl_idname = "BTC_PT_keyframe_markers"
    bl_label = "Keyframe Markers"
    bl_parent_id = "BTC_PT_blender_to_cascadeur"
    
    def draw(self, context):
        layout = self.layout
        
        # Nút đánh dấu và xóa keyframe hiện tại
        row = layout.row(align=True)
        row.operator("btc.mark_current_keyframe", text="Mark Current Keyframe", icon="KEYFRAME")
        row.operator("btc.clear_current_keyframe", text="Clear Current Keyframe", icon="KEYFRAME_HLT")
        
        # Nút đánh dấu và xóa tất cả keyframe
        row = layout.row(align=True)
        row.operator("btc.mark_all_keyframes", text="Mark All Keyframes", icon="KEYFRAME_HLT")
        row.operator("btc.clear_all_keyframes", text="Clear All Keyframes", icon="X")

# Panel con - Marked Keyframes
class BTC_PT_MarkedKeyframesPanel(PanelBasics, Panel):
    bl_idname = "BTC_PT_marked_keyframes"
    bl_label = "Marked Keyframes"
    bl_parent_id = "BTC_PT_blender_to_cascadeur"
    
    def draw(self, context):
        layout = self.layout
        
        # UIList với checkbox
        row = layout.row()
        row.template_list("BTC_UL_KeyframeList", "", context.scene, "btc_keyframes", 
                          context.scene, "btc_keyframe_index", rows=4)

# Panel con - Export
class BTC_PT_ExportPanel(PanelBasics, Panel):
    bl_idname = "BTC_PT_export"
    bl_label = "Export"
    bl_parent_id = "BTC_PT_blender_to_cascadeur"
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.operator("btc.export_object", text="Export Object", icon="OBJECT_DATA")
        
        row = layout.row()
        row.operator("btc.export_animation", text="Export Animation", icon="ARMATURE_DATA")

# Panel chính: Cascadeur Cleaner
class BTC_PT_CascadeurCleanerPanel(PanelBasics, Panel):
    bl_idname = "BTC_PT_cascadeur_cleaner"
    bl_label = "Cascadeur Cleaner"
    
    def draw_header(self, context):
        self.layout.label(text="", icon="BRUSH_DATA")
    
    def draw(self, context):
        layout = self.layout
        
        # Nút mở Cascadeur
        row = layout.row()
        row.scale_y = 1.2
        row.operator("btc.open_cascadeur", text="Open Cascadeur", icon="MESH_UVSPHERE")
        
        # Nút Import FBX và JSON
        row = layout.row(align=True)
        row.operator("btc.import_fbx", text="Import FBX", icon="IMPORT")
        row.operator("btc.import_json", text="Import JSON", icon="FILE_TEXT")
        
        # Nút Clean Keyframes
        row = layout.row()
        row.operator("btc.clean_keyframes_cascadeur", text="Clean Keyframes", icon="BRUSH_DATA")

# Panel chính: Cascadeur to Blender
class BTC_PT_CascadeurToBlenderPanel(PanelBasics, Panel):
    bl_idname = "BTC_PT_cascadeur_to_blender"
    bl_label = "Cascadeur to Blender"
    
    def draw_header(self, context):
        self.layout.label(text="", icon="IMPORT")
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.operator("btc.import_scene", text="Import Scene", icon="SCENE_DATA")
        
        row = layout.row()
        row.operator("btc.import_all_scenes", text="Import All Scenes", icon="DOCUMENTS")
        
        row = layout.row()
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
        
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text=str(item.frame))