import bpy
from bpy.types import Operator, PropertyGroup

# Định nghĩa PropertyGroup cho keyframe
class KeyframeItem(PropertyGroup):
    frame: bpy.props.IntProperty(name="Frame")
    is_marked: bpy.props.BoolProperty(name="Marked", default=False)

# Xử lý chọn armature
class BTC_OT_PickArmature(Operator):
    bl_idname = "btc.pick_armature"
    bl_label = "Pick Armature"
    bl_description = "Select an armature from the scene"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'ARMATURE'
    
    def execute(self, context):
        # Lưu armature hiện tại vào scene
        context.scene.btc_armature = context.active_object
        self.report({'INFO'}, f"Selected armature: {context.active_object.name}")
        
        # Cập nhật danh sách keyframe với armature mới
        self.update_keyframe_list(context)
        
        return {'FINISHED'}
    
    def update_keyframe_list(self, context):
        # Xóa danh sách cũ
        context.scene.btc_keyframes.clear()
        
        # Nếu không có armature, return
        if not context.scene.btc_armature:
            return
            
        armature = context.scene.btc_armature
        
        # Tìm tất cả keyframe từ armature
        if armature.animation_data and armature.animation_data.action:
            keyframes = set()
            
            for fcurve in armature.animation_data.action.fcurves:
                for keyframe in fcurve.keyframe_points:
                    # Thêm frame vào set
                    frame = int(keyframe.co[0])
                    keyframes.add(frame)
            
            # Thêm keyframe vào danh sách
            for frame in sorted(list(keyframes)):
                item = context.scene.btc_keyframes.add()
                item.frame = frame
                item.is_marked = False  # Mặc định là không đánh dấu

# Đánh dấu keyframe hiện tại
class BTC_OT_MarkCurrentKeyframe(Operator):
    bl_idname = "btc.mark_current_keyframe"
    bl_label = "Mark Current Keyframe"
    bl_description = "Mark the current keyframe"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.scene.btc_armature is not None
    
    def execute(self, context):
        current_frame = context.scene.frame_current
        
        # Kiểm tra xem keyframe có tồn tại trong danh sách không
        keyframe_exists = False
        for item in context.scene.btc_keyframes:
            if item.frame == current_frame:
                item.is_marked = True
                keyframe_exists = True
                break
        
        if not keyframe_exists:
            # Nếu keyframe không tồn tại, thêm vào danh sách
            item = context.scene.btc_keyframes.add()
            item.frame = current_frame
            item.is_marked = True
        
        self.report({'INFO'}, f"Marked keyframe at frame {current_frame}")
        return {'FINISHED'}

# Xóa đánh dấu keyframe hiện tại
class BTC_OT_ClearCurrentKeyframe(Operator):
    bl_idname = "btc.clear_current_keyframe"
    bl_label = "Clear Current Keyframe"
    bl_description = "Clear the current keyframe"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.scene.btc_armature is not None
    
    def execute(self, context):
        current_frame = context.scene.frame_current
        
        # Tìm và xóa đánh dấu keyframe
        for item in context.scene.btc_keyframes:
            if item.frame == current_frame:
                item.is_marked = False
                self.report({'INFO'}, f"Cleared keyframe at frame {current_frame}")
                return {'FINISHED'}
        
        self.report({'WARNING'}, f"No keyframe found at frame {current_frame}")
        return {'CANCELLED'}

# Đánh dấu tất cả keyframe
class BTC_OT_MarkAllKeyframes(Operator):
    bl_idname = "btc.mark_all_keyframes"
    bl_label = "Mark All Keyframes"
    bl_description = "Mark all keyframes"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.scene.btc_armature is not None
    
    def execute(self, context):
        for item in context.scene.btc_keyframes:
            item.is_marked = True
        
        self.report({'INFO'}, "Marked all keyframes")
        return {'FINISHED'}

# Xóa tất cả đánh dấu keyframe
class BTC_OT_ClearAllKeyframes(Operator):
    bl_idname = "btc.clear_all_keyframes"
    bl_label = "Clear All Keyframes"
    bl_description = "Clear all keyframes"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.scene.btc_armature is not None
    
    def execute(self, context):
        for item in context.scene.btc_keyframes:
            item.is_marked = False
        
        self.report({'INFO'}, "Cleared all keyframes")
        return {'FINISHED'}

# Danh sách các lớp để đăng ký
classes = [
    KeyframeItem,
    BTC_OT_PickArmature,
    BTC_OT_MarkCurrentKeyframe,
    BTC_OT_ClearCurrentKeyframe,
    BTC_OT_MarkAllKeyframes,
    BTC_OT_ClearAllKeyframes,
]