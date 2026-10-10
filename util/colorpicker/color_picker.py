import ctypes
import os
import tkinter as tk
import pyautogui
from PIL import Image, ImageTk, ImageGrab

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
        
        # 윈도우 OS의 배율(DPI) 설정으로 인한 마우스 좌표 오차 차단
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

        self.title("단독 컬러 스포이드")
        self.geometry("360x220")
        self.resizable(False, False)

        self.active_picker_windows = []  
        self.magnifier_canvas = None # 돋보기를 그릴 캔버스 변수
        self.mag_window = None
        self.monitor_list = []

        self.relative_path = "util/colorpicker"
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
        """연결된 모든 모니터의 정확한 가상 배치 지도를 가져옵니다."""
        monitors = []
        def monitor_enum_proc(hMonitor, hdcMonitor, lprcMonitor, dwData):
            rect = lprcMonitor.contents
            width = rect.right - rect.left
            height = rect.bottom - rect.top
            monitors.append({'left': rect.left, 'top': rect.top, 'width': width, 'height': height, 'right': rect.right, 'bottom': rect.bottom})
            return True

        MonitorEnumProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_ulong, ctypes.c_ulong, ctypes.POINTER(ctypes.wintypes.RECT), ctypes.c_double)
        ctypes.windll.user32.EnumDisplayMonitors(None, None, MonitorEnumProc(monitor_enum_proc), 0)
        return monitors
    
    def activate_picker(self):
        self.start_btn.config(text="모니터 화면 아무 곳이나 클릭하세요...", state="disabled")
        self.info_lbl.config(text="ESC나 마우스 우클릭을 누르면 취소됩니다.", fg="blue")
        
        self.clear_overlays()
        self.monitor_list = self.get_monitor_info()
        
        for m in self.monitor_list:
            overlay = tk.Toplevel(self)
            overlay.withdraw()
            
            overlay.geometry(f"{m['width']}x{m['height']}+{m['left']}+{m['top']}")
            overlay.overrideredirect(True)
            overlay.attributes("-alpha", 0.01)
            overlay.attributes("-topmost", True)
            overlay.config(cursor="crosshair") 
            
            overlay.bind("<Button-1>", self.on_overlay_click)
            # 편리한 취소를 위해 마우스 우클릭(<Button-3>) 시 스포이드가 종료되도록 바인딩
            overlay.bind("<Button-3>", lambda e: self.cancel_picker())
            overlay.bind("<Motion>", self.on_overlay_move)
            overlay.bind("<Escape>", lambda e: self.cancel_picker())
            
            overlay.deiconify()
            self.active_picker_windows.append(overlay)
            
        self.mag_window = tk.Toplevel(self)
        self.mag_window.withdraw()
        self.mag_window.overrideredirect(True)
        self.mag_window.attributes("-topmost", True)
        
        self.magnifier_canvas = tk.Canvas(self.mag_window, width=120, height=120, highlightthickness=0, bg="black")
        self.magnifier_canvas.pack()

        # 👈 [오류 해결 포인트] 리스트 자체가 아니라, 리스트의 첫 번째 개별 창[0]에 포커스를 주어 튕김을 막습니다.
        if self.active_picker_windows:
            self.active_picker_windows[0].focus_set()

    def on_overlay_move(self, event):
        """마우스가 위치한 현재 모니터 공간을 인지하여 돋보기가 밖으로 찢어지는 현상을 방어합니다."""
        x, y = event.x_root, event.y_root
        
        box_size = 7
        bbox = (x - box_size, y - box_size, x + box_size + 1, y + box_size + 1)
        
        try:
            screenshot = ImageGrab.grab(bbox=bbox, all_screens=True)
            zoomed_img = screenshot.resize((120, 120), Image.NEAREST)
            
            self.tk_img = ImageTk.PhotoImage(zoomed_img)
            self.magnifier_canvas.create_image(0, 0, anchor="nw", image=self.tk_img)
            
            cx, cy = 60, 60
            self.magnifier_canvas.create_rectangle(cx-4, cy-4, cx+4, cy+4, outline="red", width=1)
            
            # 현재 마우스가 위치한 '진짜 모니터 공간'을 추적
            current_monitor = None
            for m in self.monitor_list:
                if m['left'] <= x < m['right'] and m['top'] <= y < m['bottom']:
                    current_monitor = m
                    break
            
            if not current_monitor:
                screen_width, screen_height = pyautogui.size()
                current_monitor = {'left': 0, 'top': 0, 'right': screen_width, 'bottom': screen_height}

            # 기본 위치: 마우스 우하단
            offset_x = 20
            offset_y = 20
            
            # 1. 하단 방어: 현재 모니터 바닥에 걸치면 위로 점프
            if y + offset_y + 120 > current_monitor['bottom']:
                offset_y = -145
                
            # 2. 우측 방어: 현재 모니터 오른쪽에 걸치면 왼쪽으로 점프
            if x + offset_x + 120 > current_monitor['right']:
                offset_x = -145

            # 3. 좌측 짤림 방어: 왼쪽 모니터 경계로 넘어갈 때 잘리지 않게 마우스 우측 고정
            if x + offset_x < current_monitor['left']:
                offset_x = 20

            if self.mag_window:
                self.mag_window.geometry(f"121x121+{x + offset_x}+{y + offset_y}")
                self.mag_window.deiconify()
                
        except Exception:
            if self.mag_window:
                try:
                    self.mag_window.geometry(f"121x121+{x + 20}+{y + 20}")
                    self.mag_window.deiconify()
                except Exception:
                    pass

    def on_overlay_click(self, event):
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
        if hasattr(self, 'active_picker_windows') and self.active_picker_windows:
            for window in self.active_picker_windows:
                try:
                    window.destroy()
                except Exception:
                    pass
            self.active_picker_windows.clear()
            
        if hasattr(self, 'mag_window') and self.mag_window:
            try:
                self.mag_window.destroy()
            except Exception:
                pass
            self.mag_window = None

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
