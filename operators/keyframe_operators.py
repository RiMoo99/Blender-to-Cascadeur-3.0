import bpy
from bpy.types import Operator, PropertyGroup

# Define PropertyGroup for keyframe
class KeyframeItem(PropertyGroup):
    frame: bpy.props.IntProperty(name="Frame")
    is_marked: bpy.props.BoolProperty(name="Marked", default=False)

# Handle armature selection
class BTC_OT_PickArmature(Operator):
    bl_idname = "btc.pick_armature"
    bl_label = "Pick Armature"
    bl_description = "Select an armature from the scene"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'ARMATURE'
    
    def execute(self, context):
        # Save current armature to scene
        context.scene.btc_armature = context.active_object
        self.report({'INFO'}, f"Selected armature: {context.active_object.name}")
        
        # Update keyframe list with new armature
        self.update_keyframe_list(context)
        
        return {'FINISHED'}
    
    def update_keyframe_list(self, context):
        # Clear old list
        context.scene.btc_keyframes.clear()
        
        # If no armature, return
        if not context.scene.btc_armature:
            return
            
        armature = context.scene.btc_armature
        
        # Find all keyframes from armature
        if armature.animation_data and armature.animation_data.action:
            keyframes = set()
            
            for fcurve in armature.animation_data.action.fcurves:
                for keyframe in fcurve.keyframe_points:
                    # Add frame to set
                    frame = int(keyframe.co[0])
                    keyframes.add(frame)
            
            # Add keyframes to list
            for frame in sorted(list(keyframes)):
                item = context.scene.btc_keyframes.add()
                item.frame = frame
                item.is_marked = False  # Default is not marked

# Mark current keyframe
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
        
        # Check if keyframe exists in list
        for item in context.scene.btc_keyframes:
            if item.frame == current_frame:
                item.is_marked = True
                self.report({'INFO'}, f"Marked keyframe at frame {current_frame}")
                return {'FINISHED'}
        
        # If keyframe doesn't exist, add to list
        item = context.scene.btc_keyframes.add()
        item.frame = current_frame
        item.is_marked = True
        
        self.report({'INFO'}, f"Added and marked keyframe at frame {current_frame}")
        return {'FINISHED'}

# Clear current keyframe marking
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
        
        # Find and clear keyframe marking
        for item in context.scene.btc_keyframes:
            if item.frame == current_frame:
                item.is_marked = False
                self.report({'INFO'}, f"Cleared keyframe at frame {current_frame}")
                return {'FINISHED'}
        
        self.report({'WARNING'}, f"No keyframe found at frame {current_frame}")
        return {'CANCELLED'}

# Mark all keyframes
class BTC_OT_MarkAllKeyframes(Operator):
    bl_idname = "btc.mark_all_keyframes"
    bl_label = "Mark All Keyframes"
    bl_description = "Mark all keyframes"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.scene.btc_armature is not None and len(context.scene.btc_keyframes) > 0
    
    def execute(self, context):
        count = 0
        for item in context.scene.btc_keyframes:
            if not item.is_marked:
                item.is_marked = True
                count += 1
        
        self.report({'INFO'}, f"Marked {count} keyframes")
        return {'FINISHED'}

# Clear all keyframe markings
class BTC_OT_ClearAllKeyframes(Operator):
    bl_idname = "btc.clear_all_keyframes"
    bl_label = "Clear All Keyframes"
    bl_description = "Clear all keyframes"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.scene.btc_armature is not None and len(context.scene.btc_keyframes) > 0
    
    def execute(self, context):
        count = 0
        for item in context.scene.btc_keyframes:
            if item.is_marked:
                item.is_marked = False
                count += 1
        
        self.report({'INFO'}, f"Cleared {count} keyframes")
        return {'FINISHED'}

# List of classes to register
classes = [
    BTC_OT_PickArmature,
    BTC_OT_MarkCurrentKeyframe,
    BTC_OT_ClearCurrentKeyframe,
    BTC_OT_MarkAllKeyframes,
    BTC_OT_ClearAllKeyframes,
]