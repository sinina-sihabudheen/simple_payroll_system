from datetime import datetime
from apps.attendance.models import EsslPunch, EsslConfig
from apps.employees.models import EmployeeProfile
from django.conf import settings

def fetch_essl_data():
    """
    Connects to the ESSL device, fetches attendance logs, and saves them to the database.
    Returns a tuple (success, message).
    """
    try:
        from zk import ZK, const  # lazy import to avoid startup crash if not installed
    except Exception:
        return False, "zk library not installed; cannot connect to device"
    cfg = EsslConfig.objects.first()
    device_ip = cfg.device_ip if cfg else getattr(settings, 'ESSL_DEVICE_IP', '192.168.1.201')
    device_port = cfg.device_port if cfg else getattr(settings, 'ESSL_DEVICE_PORT', 4370)
    
    zk = ZK(device_ip, port=device_port, timeout=5)
    
    try:
        conn = zk.connect()
        conn.disable_device()
        
        count = 0
        try:
            attendance_records = conn.get_attendance()
            for att in attendance_records:
                punch_time = att.timestamp
                user_id = att.user_id

                # Save to EsslPunch model if not exists
                if not EsslPunch.objects.filter(employee_code=user_id, punch_time=punch_time).exists():
                    EsslPunch.objects.create(employee_code=user_id, punch_time=punch_time)
                    count += 1
        except Exception as e:
            return False, f"Error processing records: {str(e)}"
        finally:
            conn.enable_device()
            conn.disconnect()
            
        return True, f"Successfully fetched {count} new records."
        
    except Exception as e:
        return False, f"Could not connect to ESSL device at {device_ip}:{device_port}. Error: {str(e)}"
