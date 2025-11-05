import time
from esp32 import Partition
import uos as os
import network
import ota      

def _log_info():
    run = Partition(Partition.RUNNING)
    info = run.info()
    label = info[4] if len(info) >= 5 else None
    label = None
    u = os.uname()

    fw_ver = getattr(u, 'version', None) or getattr(u, 'release', None)
    sta = network.WLAN(network.STA_IF)
    if not sta.active():
        sta.active(True)
    mb = sta.config('mac')
    mac = ':'.join('%02x' % b for b in mb)
    
    print('[BOOT] running=', label, 'fw=', fw_ver, 'mac=', mac)


def _run():
    _log_info()
    Partition.mark_app_valid_cancel_rollback()

    for i in range(3, 0, -1):
        print('[BOOT] starting OTA in', i)
        time.sleep(1)
    try:
        ota.run()
    except Exception as ex:
        print('[BOOT][ERR]', ex)

_run()
