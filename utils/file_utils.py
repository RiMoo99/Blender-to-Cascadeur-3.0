import os
import time
import tempfile
import shutil
from datetime import datetime, timedelta

def ensure_dir_exists(directory):
    """Đảm bảo thư mục tồn tại, tạo nếu không có."""
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def create_trigger_file(exchange_folder, action, data=None):
    """Tạo file trigger để thông báo Cascadeur thực hiện hành động."""
    ensure_dir_exists(exchange_folder)
    cascadeur_trigger_folder = os.path.join(exchange_folder, "cascadeur_triggers")
    ensure_dir_exists(cascadeur_trigger_folder)
    
    # Chuẩn bị dữ liệu
    trigger_data = {
        "action": action,
        "timestamp": time.time(),
        "data": data or {}
    }
    
    # Tạo tên file với timestamp để tránh xung đột
    timestamp = int(time.time())
    trigger_path = os.path.join(cascadeur_trigger_folder, f"trigger_{action}_{timestamp}.json")
    
    # Ghi file trigger
    with open(trigger_path, 'w') as f:
        import json
        json.dump(trigger_data, f, indent=2)
    
    return trigger_path

def copy_file_to_exchange(source_path, exchange_folder, subfolder=None):
    """Sao chép file đến thư mục trao đổi."""
    ensure_dir_exists(exchange_folder)
    
    # Tạo thư mục con nếu cần
    target_folder = exchange_folder
    if subfolder:
        target_folder = os.path.join(exchange_folder, subfolder)
        ensure_dir_exists(target_folder)
    
    # Lấy tên file từ đường dẫn nguồn
    filename = os.path.basename(source_path)
    target_path = os.path.join(target_folder, filename)
    
    # Sao chép file
    shutil.copy2(source_path, target_path)
    
    return target_path

def get_export_path(file_type="fbx", use_temp=True, exchange_folder=None):
    """
    Tạo đường dẫn để xuất file.
    
    Args:
        file_type: Loại file (fbx, json, ...)
        use_temp: Sử dụng thư mục tạm hay không
        exchange_folder: Thư mục trao đổi (nếu không sử dụng thư mục tạm)
    """
    current_time = time.strftime("%Y%m%d%H%M%S")
    filename = f"blender_to_cascadeur_{current_time}.{file_type}"
    
    if use_temp:
        temp_dir = tempfile.gettempdir()
        return os.path.join(temp_dir, filename)
    
    if exchange_folder:
        subfolder = file_type
        folder = os.path.join(exchange_folder, subfolder)
        ensure_dir_exists(folder)
        return os.path.join(folder, filename)
    
    # Fallback to temp dir if no exchange folder
    temp_dir = tempfile.gettempdir()
    return os.path.join(temp_dir, filename)

def mark_trigger_as_processed(trigger_path):
    """Đánh dấu file trigger đã được xử lý bằng cách đổi tên."""
    if os.path.exists(trigger_path):
        processed_path = trigger_path + ".processed"
        try:
            os.rename(trigger_path, processed_path)
            return processed_path
        except:
            # Fallback to removal if rename fails
            try:
                os.remove(trigger_path)
            except:
                pass
    return None

def cleanup_old_triggers(exchange_folder, hours=24):
    """Dọn dẹp các file trigger cũ."""
    if not exchange_folder or not os.path.exists(exchange_folder):
        return
    
    # Tính thời gian giới hạn
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    # Kiểm tra thư mục triggers của Blender
    blender_trigger_folder = os.path.join(exchange_folder, "blender_triggers")
    if os.path.exists(blender_trigger_folder):
        for filename in os.listdir(blender_trigger_folder):
            if filename.endswith(".json.processed"):
                filepath = os.path.join(blender_trigger_folder, filename)
                file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                if file_mtime < cutoff_time:
                    try:
                        os.remove(filepath)
                    except:
                        pass
    
    # Kiểm tra thư mục triggers của Cascadeur
    cascadeur_trigger_folder = os.path.join(exchange_folder, "cascadeur_triggers")
    if os.path.exists(cascadeur_trigger_folder):
        for filename in os.listdir(cascadeur_trigger_folder):
            if filename.endswith(".json.processed"):
                filepath = os.path.join(cascadeur_trigger_folder, filename)
                file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                if file_mtime < cutoff_time:
                    try:
                        os.remove(filepath)
                    except:
                        pass