import os
import json
import time
import threading
import bpy
from bpy.app.handlers import persistent
from . import file_utils
from . import preferences

class FileWatcher:
    """Theo dõi thư mục trao đổi file và xử lý khi có file mới."""
    
    def __init__(self, exchange_folder, callback):
        self.exchange_folder = exchange_folder
        self.callback = callback
        self.is_running = False
        self.thread = None
        self.processed_files = set()
    
    def start(self):
        """Khởi động thread theo dõi."""
        if self.is_running:
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._run_watcher)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        """Dừng thread theo dõi."""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None
    
    def _run_watcher(self):
        """Hàm chính để theo dõi thư mục."""
        if not os.path.exists(self.exchange_folder):
            os.makedirs(self.exchange_folder)
        
        trigger_folder = os.path.join(self.exchange_folder, "blender_triggers")
        if not os.path.exists(trigger_folder):
            os.makedirs(trigger_folder)
        
        print(f"Watching folder: {trigger_folder}")
        
        while self.is_running:
            try:
                self._check_for_triggers(trigger_folder)
                
                # Dọn dẹp các file cũ nếu cần
                try:
                    prefs = preferences.get_preferences(bpy.context)
                    file_utils.cleanup_old_triggers(self.exchange_folder, prefs.cleanup_interval)
                except:
                    # Fallback to default cleanup interval
                    file_utils.cleanup_old_triggers(self.exchange_folder, 24)
                
                time.sleep(1.0)  # Kiểm tra mỗi giây
            except Exception as e:
                print(f"Error in file watcher: {str(e)}")
    
    def _check_for_triggers(self, folder):
        """Kiểm tra và xử lý các file trigger."""
        if not os.path.exists(folder):
            return
        
        for filename in os.listdir(folder):
            if not filename.startswith("trigger_") or not filename.endswith(".json"):
                continue
            
            filepath = os.path.join(folder, filename)
            
            # Bỏ qua nếu đã xử lý
            if filepath in self.processed_files:
                continue
            
            # Đọc file trigger
            try:
                with open(filepath, 'r') as f:
                    trigger_data = json.load(f)
                
                # Đánh dấu đã xử lý
                self.processed_files.add(filepath)
                
                # Gọi callback để xử lý
                if self.callback:
                    self.callback(trigger_data)
                
                # Đánh dấu file đã xử lý (đổi tên thay vì xóa)
                file_utils.mark_trigger_as_processed(filepath)
            except Exception as e:
                print(f"Error processing trigger file {filepath}: {str(e)}")

# Timer handler để khởi động FileWatcher khi Blender bắt đầu
@persistent
def load_handler(dummy):
    """Handler được gọi khi Blender khởi động."""
    # Khởi động FileWatcher với addon preferences
    try:
        exchange_folder = preferences.get_exchange_folder(bpy.context)
        
        # Khởi động watcher với callback xử lý trigger
        watcher = FileWatcher(exchange_folder, process_trigger)
        watcher.start()
        
        # Lưu watcher vào addon_data
        if not hasattr(bpy.types.WindowManager, "btc_file_watcher"):
            bpy.types.WindowManager.btc_file_watcher = None
        bpy.context.window_manager.btc_file_watcher = watcher
        
        print("File watcher started")
    except Exception as e:
        print(f"Error starting file watcher: {str(e)}")

def process_trigger(trigger_data):
    """Xử lý dữ liệu trigger từ Cascadeur."""
    action = trigger_data.get("action")
    data = trigger_data.get("data", {})
    
    print(f"Received trigger: {action}")
    
    # Xử lý các hành động khác nhau
    if action == "import_scene":
        # Thêm vào hàng đợi xử lý của Blender
        bpy.app.timers.register(lambda: process_import_scene(data))
    elif action == "import_all_scenes":
        bpy.app.timers.register(lambda: process_import_all_scenes(data))
    elif action == "clean_keyframes":
        bpy.app.timers.register(lambda: process_clean_keyframes(data))

def process_import_scene(data):
    """Xử lý import scene từ Cascadeur."""
    fbx_path = data.get("fbx_path")
    if not fbx_path or not os.path.exists(fbx_path):
        print(f"FBX file not found: {fbx_path}")
        return
    
    # Import FBX
    bpy.ops.import_scene.fbx(filepath=fbx_path)
    print(f"Imported scene from {fbx_path}")
    return None  # Yêu cầu cho bpy.app.timers

def process_import_all_scenes(data):
    """Xử lý import tất cả scene từ Cascadeur."""
    fbx_paths = data.get("fbx_paths", [])
    
    for fbx_path in fbx_paths:
        if os.path.exists(fbx_path):
            bpy.ops.import_scene.fbx(filepath=fbx_path)
    
    print(f"Imported {len(fbx_paths)} scenes")
    return None  # Yêu cầu cho bpy.app.timers

def process_clean_keyframes(data):
    """Xử lý clean keyframes dựa trên JSON từ Cascadeur."""
    json_path = data.get("json_path")
    if not json_path or not os.path.exists(json_path):
        print(f"JSON file not found: {json_path}")
        return
    
    # Đọc JSON
    with open(json_path, 'r') as f:
        keyframes_data = json.load(f)
    
    # Xử lý dữ liệu keyframe
    # Tùy thuộc vào cấu trúc của JSON
    
    print(f"Processed keyframes from {json_path}")
    return None  # Yêu cầu cho bpy.app.timers