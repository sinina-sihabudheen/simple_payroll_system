from zk import ZK, const
from datetime import datetime
from apps.attendance.models import EsslPunch
from apps.employees.models import EmployeeProfile

def fetch_essl_data():
    zk = ZK('192.168.1.201', port=4370, timeout=5)
    conn = zk.connect()
    conn.disable_device()

    for att in conn.get_attendance():
        punch_time = att.timestamp
        user_id = att.user_id

        # Save to EsslPunch model if not exists
        if not EsslPunch.objects.filter(employee_code=user_id, punch_time=punch_time).exists():
            EsslPunch.objects.create(employee_code=user_id, punch_time=punch_time)

    conn.enable_device()
    conn.disconnect()
