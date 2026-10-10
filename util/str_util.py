import os
import re
import sys


class Str:

    @staticmethod
    def to_string_time(tm, type, is_millis=False) -> str:
        """_summary_
        time to 00:00:00.000
        Args:
            tm (time millis)
            type (str [hour, minute, second]): hour부터, minute부터, second만 출력
            is_millis (bool, False): 밀리초 포함 여부
        Returns:
            str: 00:00:00.000, 00:00.000, 00.000, 00:00:00, 00:00, 00
        """
        sb = []
        millis = tm % 1000
        seconds = tm // 1000
        if is_millis:
            sb.append(f".{millis:03d}")
        
        second = seconds % 60
        if type == "second":
            sb.append(f"{second:02d}")
            return "".join(sb.reverse())
        
        minutes = seconds // 60
        minute = minutes % 60
        if type=="minute":
            sb.append(f"{minute:02d}")
            return "".join(reversed(sb))
        
        hours = minutes // 60
        sb.append(f"{hours:02d}")
        return "".join(sb[::-1])

    @staticmethod
    def to_string_number(num: int, length: int=2) -> str:
        """_summary_
        number to 00
        Args:
            num (int): number
            length (int, 2): length of string
        Returns:
            str: 00
        """
        return f"{num:0{length}d}"
    
    @staticmethod
    def str_to_int(s: str) -> int:
        """_summary_
        string to integer
        Args:
            s (str): string
        Returns:
            int: integer
        """
        if s and s.isdigit():
            return int(s)
        return 0
    
    @staticmethod
    def int_to_str(i: int) -> str:
        """_summary_
        integer to string
        Args:
            i (int): integer
        Returns:
            str: string
        """
        return str(i)
    
    @staticmethod
    def str_to_bool(s: str) -> bool:
        """_summary_
        string to boolean
        Args:
            s (str): string
        Returns:
            bool: boolean
        """
        if s and s.lower() in ["true", "1", "yes", "y"]:
            return True
        return False
    
    @staticmethod
    def bool_to_str(b: bool) -> str:
        """_summary_
        boolean to string
        Args:
            b (bool): boolean
        Returns:
            str: string
        """
        return "True" if b else "False"
    
    @staticmethod
    def is_not_blank(s: str=None) -> bool:
        if s and not s.strip() == "":
            return True
        return False

    @staticmethod
    def is_blank(s: str=None) -> bool:
        if s and not s.strip() == "":
            return False
        return True

    @staticmethod
    def is_blank_list(lst: list=None) -> bool:
        if lst and 0 < len(lst):
            return False
        return True
    
    @staticmethod
    def is_not_blank_list(lst: list=None) -> bool:
        if lst and 0 < len(lst):
            return True
        return False
    
    @staticmethod
    def is_not_blank_tuple(tpl: tuple=None) -> bool:
        if tpl and 0 < len(tpl):
            return True
        return False
    
    @staticmethod
    def is_blank_tuple(tpl: tuple=None) -> bool:
        if tpl and 0 < len(tpl):
            return False
        return True
    
    @staticmethod
    def is_not_blank_set(st: set=None) -> bool:
        if st and 0 < len(st):
            return True
        return False
    
    @staticmethod
    def is_blank_set(st: set=None) -> bool:
        if st and 0 < len(st):
            return False
        return True
    
    @staticmethod
    def is_not_blank_dict(dct: dict=None) -> bool:
        if dct and 0 < len(dct):
            return True
        return False

    @staticmethod
    def is_blank_dict(dct: dict=None) -> bool:
        if dct and 0 < len(dct):
            return False
        return True

    @staticmethod
    def is_han(ch) -> bool:
        return (
            (0xAC00 <= ch <= 0xD7A3)
            or (0x3131 <= ch <= 0x318F)
            or (0x1100 <= ch <= 0x11FF)
            or (0xD7B0 <= ch <= 0xD7FF)
        )
    
    @staticmethod
    def is_alpha(ch) -> bool:
        return ((65 <= ch <= 90) or (97 <= ch <= 122))

    @staticmethod
    def is_digit(ch) -> bool:
        return (48 <= ch <= 57)

    @staticmethod
    def strip_not_digit(s: str) -> str:
        return re.sub(r"\D", "", s)

    @staticmethod
    def number_format(number: int) -> str:
        return f"{number:,}"

    @staticmethod
    def get_class_name(clazz_object) -> str:
        return clazz_object.__class__.__name__


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":
    print(os.path.abspath("."))

    # 1. 현재 파일(.py 또는 .exe)이 실제로 위치한 '진짜 폴더 경로' 구하기
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller 단일 파일(.exe)로 실행된 경우
        # 만약 이미지를 .exe 내부에 빌드(내장)했다면 sys._MEIPASS를 사용하고,
        # 이미지를 .exe 외부에 두고 쓸 거라면 os.path.dirname(sys.executable)을 사용합니다.
        print(sys._MEIPASS)
        base_path = os.path.dirname(sys.executable)
    else:
        # 일반 파이썬 환경(.py)으로 실행된 경우 (현재 스크립트 파일의 절대 경로 기준)
        base_path = os.path.dirname(os.path.abspath(__file__))

    # 2. 진짜 폴더 경로를 기준으로 image 폴더 연결
    folder_path = os.path.join(base_path, "image")

    print(f"고정된 이미지 폴더 경로: {folder_path}")
    
    print(Str.is_blank(" "))
    print(Str.is_blank())
    print(Str.is_blank(" abc "))
    