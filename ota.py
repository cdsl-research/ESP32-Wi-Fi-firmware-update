import time, network, urequests as rq, uhashlib as uh, esp32, machine, esp

# ===== CONFIG =====
WIFI_SSID = WiFiのSSID
WIFI_PASS = WiFiのパスワード
FW_URL    = "http://サーバーのIPアドレス:任意のポート番号/OTA/ファームウェアのファイル名"
CHUNK     = 1024


# ===== OTA writer (direct write to inactive OTA partition) =====
BLK = 4096

class OTADirectWriter:
    def __init__(self, total_len=0, sha16=b"\x00"*16):
        self.run  = esp32.Partition(esp32.Partition.RUNNING)
        self.part = self.run.get_next_update()
        if self.part is None:
            raise OSError("No OTA update partition")
        _t, _st, addr, psize, _label, _enc = self.part.info()
        self.addr  = addr
        self.psize = psize
        self.total = total_len or psize
        self.sha16 = sha16 or b"\x00"*16
        self.h     = uh.sha256()
        self.buf   = bytearray(BLK)
        self.boff  = 0
        self.written = 0
        # erase range based on expected total (or full slot if unknown)
        nblk = (self.total + BLK - 1) // BLK
        if hasattr(self.part, "erase_blocks"):
            self.part.erase_blocks(0, nblk)
        else:
            start_sector = addr // BLK
            for i in range(nblk):
                esp.flash_erase(start_sector + i)

    def write(self, data):
        mv = memoryview(data)
        self.h.update(mv)
        off = 0
        while off < len(mv):
            n = min(len(mv) - off, BLK - self.boff)
            self.buf[self.boff:self.boff+n] = mv[off:off+n]
            self.boff += n
            off += n
            if self.boff == BLK:
                bi = self.written // BLK
                self.part.writeblocks(bi, self.buf)
                self.written += BLK
                self.boff = 0

    def finalize(self):
        if self.boff:
            for i in range(self.boff, BLK):
                self.buf[i] = 0xFF
            bi = self.written // BLK
            self.part.writeblocks(bi, self.buf)
            self.written += BLK
            self.boff = 0
        return True

    def switch_and_reboot(self):
        try:
            try:
                esp32.Partition.set_boot(self.part)
            except Exception:
                runp = esp32.Partition(esp32.Partition.RUNNING)
                nxtp = runp.get_next_update()
                if nxtp:
                    esp32.Partition.set_boot(nxtp)
        except Exception:
            pass
        print("reset machine")
        machine.reset()


# ===== HTTP stream =====
def _http_iter(url, sz=CHUNK):
    r = rq.get(url)
    if getattr(r, 'status_code', 200) != 200:
        try:
            r.close()
        except Exception:
            pass
        raise OSError("HTTP {}".format(getattr(r, 'status_code', -1)))
    try:
        while True:
            b = r.raw.read(sz)
            if not b:
                break
            yield b
    finally:
        try:
            r.close()
        except Exception:
            pass


# ===== WiFi =====
def _wifi():
    s = network.WLAN(network.STA_IF)
    if not s.active():
        s.active(True)
    if not s.isconnected():
        s.connect(WIFI_SSID, WIFI_PASS)
        t0 = time.ticks_ms()
        while not s.isconnected() and time.ticks_diff(time.ticks_ms(), t0) < 15000:
            time.sleep_ms(200)
    if not s.isconnected():
        raise OSError("WiFi connect failed")
    return s


# ===== Main =====
def run(fw_url=None):
    print("[OTA] start")
    _wifi()
    url = fw_url or FW_URL
    print("[OTA] GET", url)
    writer = OTADirectWriter(0, b"\x00"*16)
    total = 0
    print("now downloading...")
    for part in _http_iter(url, CHUNK):
        writer.write(part)
        total += len(part)
    ok = writer.finalize()
    print("[OTA] finalize:", ok, "bytes=", total)
    if ok:
        writer.switch_and_reboot()
    return ok
