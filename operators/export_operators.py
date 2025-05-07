import bpy
import json
import os
import time
import tempfile
from bpy.types import Operator
from bpy.props import StringProperty
from ..utils import file_utils, preferences

# Import class từ keyframe_operators
from .keyframe_operators import BTC_OT_PickArmature

# Xuất đối tượng
class BTC_OT_ExportObject(Operator):
    bl_idname = "btc.export_object"
    bl_label = "Export Object"
    bl_description = "Export selected object to Cascadeur"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.scene.btc_armature is not None
    
    def execute(self, context):
        armature = context.scene.btc_armature
        
        if not armature:
            self.report({'ERROR'}, "No armature selected")
            return {'CANCELLED'}
        
        # Lấy cài đặt preferences
        prefs = preferences.get_preferences(context)
        exchange_folder = preferences.get_exchange_folder(context)
        
        # Tạo đường dẫn export
        export_path = file_utils.get_export_path(file_type="fbx", use_temp=True)
        
        try:
            # Export FBX
            if not self.export_fbx(context, export_path):
                self.report({'ERROR'}, "Failed to export FBX")
                return {'CANCELLED'}
            
            # Sao chép file sang thư mục trao đổi
            fbx_path = file_utils.copy_file_to_exchange(export_path, exchange_folder, "fbx")
            if not fbx_path:
                self.report({'ERROR'}, "Failed to copy FBX to exchange folder")
                return {'CANCELLED'}
            
            # Tạo trigger file
            trigger_data = {
                "action": "import_object",
                "data": {
                    "fbx_path": fbx_path,
                    "object_name": armature.name
                }
            }
            
            trigger_path = file_utils.create_trigger_file(exchange_folder, "import_object", trigger_data)
            if not trigger_path:
                self.report({'ERROR'}, "Failed to create trigger file")
                return {'CANCELLED'}
            
            # Tự động mở Cascadeur nếu đã bật tùy chọn
            if prefs.auto_open_cascadeur:
                bpy.ops.btc.open_cascadeur()
            
            self.report({'INFO'}, f"Exported object to {fbx_path}")
            return {'FINISHED'}
        
        except Exception as e:
            self.report({'ERROR'}, f"Export error: {str(e)}")
            return {'CANCELLED'}
    
    def export_fbx(self, context, filepath):
        """Export armature to FBX"""
        try:
            # Lưu trạng thái selection hiện tại
            original_selection = context.selected_objects.copy()
            active_object = context.active_object
            
            # Chọn armature
            bpy.ops.object.select_all(action='DESELECT')
            context.scene.btc_armature.select_set(True)
            context.view_layer.objects.active = context.scene.btc_armature
            
            # Export FBX
            bpy.ops.export_scene.fbx(
                filepath=filepath,
                use_selection=True,
                object_types={'ARMATURE', 'MESH'},
                use_mesh_modifiers=True,
                use_mesh_modifiers_render=True,
                add_leaf_bones=False
            )
            
            # Khôi phục selection
            bpy.ops.object.select_all(action='DESELECT')
            for obj in original_selection:
                obj.select_set(True)
            if active_object:
                context.view_layer.objects.active = active_object
                
            return True
        
        except Exception as e:
            print(f"FBX export error: {str(e)}")
            return False

# Xuất animation
class BTC_OT_ExportAnimation(Operator):
    bl_idname = "btc.export_animation"
    bl_label = "Export Animation"
    bl_description = "Export animation with marked keyframes to Cascadeur"
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: StringProperty(
        name="Save Path",
        description="Path to save the metadata file",
        default="//",
        subtype='FILE_PATH'
    )
    
    @classmethod
    def poll(cls, context):
        return context.scene.btc_armature is not None
    
    def invoke(self, context, event):
        # Lưu frame hiện tại
        self.current_frame = context.scene.frame_current
        
        # Kiểm tra xem armature có được chọn không
        if not context.scene.btc_armature:
            self.report({'WARNING'}, "No armature selected. Please select an armature first.")
            return {'CANCELLED'}
            
        # Kiểm tra xem có keyframes nào được đánh dấu không
        marked_keyframes = self.get_marked_keyframes(context)
        if not marked_keyframes:
            self.report({'WARNING'}, "No keyframes are marked. Please mark keyframes before exporting.")
            return {'CANCELLED'}
        
        # Đặt tên file mặc định dựa trên file blend
        blend_path = bpy.data.filepath
        if blend_path:
            dir_path = os.path.dirname(blend_path)
            filename = os.path.splitext(os.path.basename(blend_path))[0]
            self.filepath = os.path.join(dir_path, f"{filename}_keyframes.json")
        else:
            self.filepath = "//"
        
        # Hiển thị trình duyệt file cho metadata JSON
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        try:
            # Khôi phục frame hiện tại trước trình duyệt file
            if hasattr(self, 'current_frame'):
                context.scene.frame_current = self.current_frame
            
            # Xuất metadata JSON
            marked_keyframes = self.get_marked_keyframes(context)
            
            # Thêm phần mở rộng .json nếu không có
            filepath = self.filepath
            if not filepath.lower().endswith('.json'):
                filepath += '.json'
            
            # Tạo thư mục nếu không tồn tại
            directory = os.path.dirname(filepath)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # Ghi file metadata
            with open(filepath, 'w') as f:
                json.dump(marked_keyframes, f, indent=2)
            
            self.report({'INFO'}, f"Exported keyframe metadata to {filepath}")
            
            # Lấy cài đặt preferences
            prefs = preferences.get_preferences(context)
            exchange_folder = preferences.get_exchange_folder(context)
            
            # Sao chép file sang thư mục trao đổi để sử dụng sau
            json_path = file_utils.copy_file_to_exchange(filepath, exchange_folder, "json")
            if not json_path:
                self.report({'WARNING'}, "Failed to copy JSON to exchange folder, but file was saved locally")
            
            # Đảm bảo chúng ta ở chế độ object trước khi tiếp tục
            if context.object and context.object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            
            # Gọi hàm xuất ARP với độ trễ sử dụng bộ hẹn giờ
            def open_arp_export_delayed():
                self.open_arp_export(context)
                return None  # Xóa bộ hẹn giờ
                
            bpy.app.timers.register(open_arp_export_delayed, first_interval=0.5)
            
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error exporting metadata: {e}")
            return {'CANCELLED'}
    
    def get_marked_keyframes(self, context):
        """Lấy danh sách keyframes được đánh dấu"""
        marked_keyframes = {}
        
        for item in context.scene.btc_keyframes:
            if item.is_marked:
                marked_keyframes[str(item.frame)] = {}
        
        return marked_keyframes
    
    def open_arp_export(self, context):
        """Mở panel xuất Auto-Rig Pro"""
        try:
            # Lưu frame hiện tại
            current_frame = context.scene.frame_current
            
            # Chọn armature
            armature = context.scene.btc_armature
            if not armature:
                self.report({'WARNING'}, "No armature selected. Please select an armature first.")
                return
            
            # Đảm bảo chúng ta ở chế độ Object
            if context.object and context.object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            
            # Bỏ chọn tất cả đối tượng và chỉ chọn armature
            bpy.ops.object.select_all(action='DESELECT')
            armature.select_set(True)
            context.view_layer.objects.active = armature
            
            # Cố gắng mở panel xuất ARP
            success = False
            
            # Thử các phương pháp khác nhau
            arp_methods = [
                ("arp.arp_export_fbx_panel", "Opened ARP export panel"),
                ("arp_export_fbx_panel", "Opened ARP export panel (method 2)"),
                ("arp.export_fbx_panel", "Opened ARP export panel (method 3)"),
                ("auto_rig_pro.export_fbx_panel", "Opened ARP export panel (method 4)")
            ]
            
            for op_name, success_msg in arp_methods:
                try:
                    getattr(bpy.ops, op_name)('INVOKE_DEFAULT')
                    self.report({'INFO'}, success_msg)
                    success = True
                    break
                except Exception as e:
                    print(f"ARP export attempt failed with {op_name}: {e}")
            
            # Nếu tất cả các lần thử đều thất bại, hiển thị hướng dẫn
            if not success:
                def draw_guide(self, context):
                    layout = self.layout
                    layout.label(text="Auto-Rig Pro Export Guide:", icon='INFO')
                    box = layout.box()
                    box.label(text="1. Make sure your armature is selected")
                    box.label(text="2. Open the Auto-Rig Pro panel in the 'N' sidebar")
                    box.label(text="3. Click on 'Export' tab or button")
                    box.label(text="4. Configure export settings")
                    box.label(text="5. Click 'Export FBX' to save your file")
                    box.label(text="6. Export to the exchange folder for Cascadeur")
                
                context.window_manager.popup_menu(draw_guide, title="Auto-Rig Pro Export Guide", icon='HELP')
                self.report({'INFO'}, "Please follow the guide to export with Auto-Rig Pro")
                
                # Hiển thị thông báo về thư mục trao đổi
                exchange_folder = preferences.get_exchange_folder(context)
                self.report({'INFO'}, f"Export the FBX to: {exchange_folder}/fbx")
            
            # Khôi phục frame ban đầu
            context.scene.frame_current = current_frame
                
        except Exception as e:
            self.report({'ERROR'}, f"Error opening ARP export: {e}")

# Xuất hoàn chỉnh (hỗ trợ file trigger)
class BTC_OT_ExportComplete(Operator):
    bl_idname = "btc.export_complete"
    bl_label = "Export Complete"
    bl_description = "Create trigger file to export to Cascadeur"
    bl_options = {'REGISTER', 'UNDO'}
    
    fbx_path: StringProperty(
        name="FBX Path",
        description="Path to the exported FBX file",
        default="",
        subtype='FILE_PATH'
    )
    
    json_path: StringProperty(
        name="JSON Path",
        description="Path to the exported JSON metadata file",
        default="",
        subtype='FILE_PATH'
    )
    
    def execute(self, context):
        # Lấy cài đặt preferences
        prefs = preferences.get_preferences(context)
        exchange_folder = preferences.get_exchange_folder(context)
        
        # Kiểm tra xem FBX path có hợp lệ không
        if not self.fbx_path or not os.path.exists(self.fbx_path):
            self.report({'ERROR'}, "Invalid FBX path")
            return {'CANCELLED'}
        
        # Kiểm tra xem JSON path có hợp lệ không
        if not self.json_path or not os.path.exists(self.json_path):
            self.report({'ERROR'}, "Invalid JSON path")
            return {'CANCELLED'}
        
        try:
            # Sao chép file sang thư mục trao đổi
            fbx_path = file_utils.copy_file_to_exchange(self.fbx_path, exchange_folder, "fbx")
            if not fbx_path:
                self.report({'ERROR'}, "Failed to copy FBX to exchange folder")
                return {'CANCELLED'}
                
            json_path = file_utils.copy_file_to_exchange(self.json_path, exchange_folder, "json")
            if not json_path:
                self.report({'ERROR'}, "Failed to copy JSON to exchange folder")
                return {'CANCELLED'}
            
            # Tạo trigger file
            trigger_data = {
                "action": "import_animation",
                "data": {
                    "fbx_path": fbx_path,
                    "json_path": json_path,
                    "object_name": context.scene.btc_armature.name if context.scene.btc_armature else "Unknown"
                }
            }
            
            trigger_path = file_utils.create_trigger_file(exchange_folder, "import_animation", trigger_data)
            if not trigger_path:
                self.report({'ERROR'}, "Failed to create trigger file")
                return {'CANCELLED'}
            
            # Tự động mở Cascadeur nếu đã bật tùy chọn
            if prefs.auto_open_cascadeur:
                bpy.ops.btc.open_cascadeur()
            
            self.report({'INFO'}, f"Created trigger for Cascadeur at {trigger_path}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Export error: {str(e)}")
            return {'CANCELLED'}

# Danh sách các lớp để đăng ký
classes = [
    BTC_OT_ExportObject,
    BTC_OT_ExportAnimation,
    BTC_OT_ExportComplete,
]