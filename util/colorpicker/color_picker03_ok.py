import ctypes
import os
import tkinter as tk
import pyautogui

# 테스트를 위해 임시 클래스 생성 (ResUtil이 없을 경우 대비)
try:
    from util.resource import ResUtil
except ImportError:
    class ResUtil:
        @staticmethod
        def resource_path(path, filename):
            return os.path.abspath(os.path.join(path, filename))


class ColorPickerWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("단독 컬러 스포이드")
        self.geometry("360x220")
        self.resizable(False, False)

        self.relative_path = "util"
        try:
            icon_path = ResUtil.resource_path(self.relative_path, "colorpicker.ico")
            self.iconbitmap(icon_path)
        except Exception:
            pass
        
        # 👈 [오류 해결] 충돌 가능성이 있는 이름을 피하기 위해 변수명을 완전히 바꿨습니다.
        self.active_picker_windows = []  

        self.relative_path = "util"
        try:
            icon_path = ResUtil.resource_path(self.relative_path, "colorpicker.ico")
            self.iconbitmap(icon_path)
        except Exception:
            pass
        
        self.info_lbl = tk.Label(self, text="아래 버튼을 누르면 스포이드 모드가 시작됩니다.", font=("맑은 고딕", 9))
        self.info_lbl.pack(pady=12)

        result_frame = tk.Frame(self, relief="solid", bd=1)
        result_frame.pack(pady=5, fill="x", padx=25)

        self.color_box = tk.Label(result_frame, bg="#FFFFFF", width=8, height=3, relief="flat")
        self.color_box.pack(side="left", padx=15, pady=10)

        self.code_lbl = tk.Label(result_frame, text="HEX: #FFFFFF\nRGB: (255, 255, 255)", 
                                 font=("맑은 고딕", 10, "bold"), justify="left")
        self.code_lbl.pack(side="left", padx=(10, 0))

        self.start_btn = tk.Button(self, text="화면 클릭하여 색상 추출", 
                                   font=("맑은 고딕", 10, "bold"), bg="#f3f3f3",
                                   command=self.activate_picker, padx=10, pady=5)
        self.start_btn.pack(pady=18)

        self.bind("<Key>", self.on_key_press)
        self.protocol("WM_DELETE_WINDOW", self.on_window_close)

    def on_key_press(self, event):
        if event.keysym == "Escape":
            self.on_window_close()
    
    def on_window_close(self):
        self.clear_overlays()
        self.destroy()

    def get_monitor_info(self):
        """윈도우 API를 이용해 연결된 모든 모니터의 개별 좌표와 크기를 정확히 가져옵니다."""
        monitors = []
        def monitor_enum_proc(hMonitor, hdcMonitor, lprcMonitor, dwData):
            rect = lprcMonitor.contents
            width = rect.right - rect.left
            height = rect.bottom - rect.top
            monitors.append((rect.left, rect.top, width, height))
            return True

        MonitorEnumProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_ulong, ctypes.c_ulong, ctypes.POINTER(ctypes.wintypes.RECT), ctypes.c_double)
        ctypes.windll.user32.EnumDisplayMonitors(None, None, MonitorEnumProc(monitor_enum_proc), 0)
        return monitors
    
    def activate_picker(self):
        """모든 모니터에 각각 투명 창을 띄워 클릭을 완벽하게 격리합니다."""
        self.start_btn.config(text="모니터 화면 아무 곳이나 클릭하세요...", state="disabled")
        self.info_lbl.config(text="창 밖의 바탕화면, 브라우저 등을 클릭하면 색상이 추출됩니다.", fg="blue")
        
        # 이전 창 정리
        self.clear_overlays()
        
        monitor_list = self.get_monitor_info()
        
        for left, top, width, height in monitor_list:
            overlay = tk.Toplevel(self)
            overlay.withdraw()
            
            overlay.geometry(f"{width}x{height}+{left}+{top}")
            overlay.overrideredirect(True)
            overlay.attributes("-alpha", 0.01)
            overlay.attributes("-topmost", True)
            overlay.config(cursor="crosshair")
            
            overlay.bind("<Button-1>", self.on_overlay_click)
            overlay.bind("<Escape>", lambda e: self.cancel_picker())
            
            overlay.deiconify()
            # 👈 새로운 이름의 리스트에 창 인스턴스들을 차곡차곡 담아둡니다.
            self.active_picker_windows.append(overlay)
            
        if self.active_picker_windows:
            self.active_picker_windows[0].focus_set()

    def on_overlay_click(self, event):
        """어떤 모니터든 투명 창 위에서 마우스를 클릭했을 때 실행되는 콜백"""
        x, y = event.x_root, event.y_root
        
        try:
            r, g, b = pyautogui.pixel(int(x), int(y))
            hex_code = f"#{r:02x}{g:02x}{b:02x}".upper()
            
            self.update_picker_ui(r, g, b, hex_code)
        except Exception as e:
            print(f"픽셀 추출 오류: {e}")
            self.info_lbl.config(text="픽셀 추출에 실패했습니다.", fg="red")
        
        self.clear_overlays()
        self.start_btn.config(state="normal")

    def cancel_picker(self):
        self.clear_overlays()
        self.start_btn.config(state="normal", text="화면 클릭하여 색상 추출")
        self.info_lbl.config(text="색상 추출이 취소되었습니다.", fg="black")

    def clear_overlays(self):
        """생성된 모든 모니터의 오버레이 창을 안전하게 닫고 리스트를 완전히 비웁니다."""
        # 👈 새로운 변수명으로 안전하게 검사 후 삭제를 진행합니다.
        if hasattr(self, 'active_picker_windows') and self.active_picker_windows:
            for window in self.active_picker_windows:
                try:
                    window.destroy()
                except Exception:
                    pass
            self.active_picker_windows.clear()

    def update_picker_ui(self, r, g, b, hex_code):
        self.color_box.config(bg=hex_code)
        self.code_lbl.config(text=f"HEX: {hex_code}\nRGB: ({r}, {g}, {b})")
        self.start_btn.config(text="화면 클릭하여 색상 추출")
        self.info_lbl.config(text="추출 성공! HEX 코드가 클립보드에 복사되었습니다. ✅", fg="green")
        
        self.clipboard_clear()
        self.clipboard_append(hex_code)


if __name__ == "__main__":
    picker = ColorPickerWindow()
    picker.mainloop()
