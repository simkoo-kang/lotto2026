import configparser
import io
from util.text.log_util import LogUtil
from util.text.file_util import FileUtil


class IniManager:
    def __init__(self, ini_file: str=None):
        self.filename = ini_file
        
        self.logger = LogUtil.get_logger(__file__)
        
        self.config = configparser.ConfigParser()
        if self.filename:
            self.load_ini_file(self.filename)
    
    def get_keys(self):
        """_summary_
        section names
        Returns:
            KeyView: _description_
        """
        return self.config.keys()
    
    def get_items(self):
        """_summary_
        key, value(Section)
        Returns:
            ItemsView: _description_
        """
        return self.config.items()
    
    def add_section(self, section_name: str) -> configparser.SectionProxy:
        return self.create_section(section_name=section_name)
    
    def create_section(self, section_name: str) -> configparser.SectionProxy:
        self.config.add_section(section=section_name)
        return self.config[section_name]
    
    def get_value(self, key_name: str) -> str:
        return self.config[key_name]
    
    def set_value(self, key_name: str, value):
        self.config[key_name] = str(value)
    
    def get_section(self, section_name: str):
        return self.config[section_name]
    
    def get_section_value(self, section_name: str, key_name: str):
        section = self.config[section_name]
        if section:
            return self.config[section_name][key_name]
        return None
    
    def set_section_value(self, section_name: str, key_name: str, value):
        section = self.config[section_name]
        if not section:
            section = self.add_section(section_name=section_name)
        section[key_name] = str(value)
    
    def set_section_by_dict(self, section_name: str, section_value: dict[str, str]):
        section = self.create_section(section_name=section_name)
        section.clear()
        section.update(section_value)
    
    def load_ini_file(self, file_path: str):
        if not file_path:
            self.logger.debug("file_path is None!")
            return False
        # 2. 파일 읽기
        self.config.read(file_path, encoding='utf-8')
        return True

    def save_ini_file(self, file_path: str=None):
        if not self.config:
            self.logger.debug("저장할 내용이 없습니다.")
            return False
        
        ini_file = file_path if file_path else self.filename
        if not ini_file:
            self.logger.debug("file_path is None!")
            return False
        
        FileUtil.mkdirs(file_path=ini_file)
        try:
            with open(file_path, 'w', encoding='utf-8') as configfile:
                self.config.write(configfile)
            # return True - else문 실행을 위해
        except Exception as e:
            self.logger.debug(f"오류가 발생하였습니다.{e}")
            return False
        else:
            self.logger.debug(f"{ini_file}를 정상적으로 읽어 왔습니다.")
            return True
        finally:
            pass
    
    def to_string(self):
        string_buffer = io.StringIO()
        self.config.write(string_buffer)
        return string_buffer.getvalue()
    
    def to_string_by_section(self, section: configparser.SectionProxy):
        # 섹션 이름 추가
        lines = [f"[{section.name}]"]
        # 하위 Key-Value 추가
        for key, value in section.items():
            lines.append(f"{key} = {value}")
        return "\n".join(lines)


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":
    file_path = "util/text/config.ini"
    
    ini = IniManager(ini_file=file_path)
    
    filter = ini.get_section("Filter")
    print(filter, filter.getboolean("EnableBonus"))
    
    # # 값 가져오기 (문자열로 반환됨)
    # encoding = config['LottoConfig']['FileEncoding']
    # print(encoding)
    # # 데이터 타입 변환 기능 활용 (int, boolean 등)
    # max_rounds = config.getint('LottoConfig', 'MaxRounds')
    # enable_bonus = config.getboolean('Filter', 'EnableBonus')

    # print(max_rounds, enable_bonus)  # 출력: 1244 False
    
    mysection = { 'key1': 'value'}
    sp = ini.set_section_by_dict(section_name='mysection', section_value=mysection)
    
    ss = ini.add_section('second section')
    ss['delay'] = '1500'
    
    print(ini.to_string())
    
    print(ini.config.keys())
    for key in ini.config.keys():
        print(key)
    print(ini.config.items())
    for key, value in ini.config.items():
        print(key, ini.to_string_by_section(value))
    
# # 1. 임시 설정 관리자 생성
# temp_config = configparser.ConfigParser()

# # 2. 빈 섹션 생성
# temp_config.add_section('MySection')

# # 3. 참조를 변수에 담기 (원하셨던 SectionProxy 객체 생성 완료!)
# sp = temp_config['MySection']

# # 이제 자유롭게 값을 넣고 사용할 수 있습니다.
# sp['Key1'] = 'Value1'
# print(type(sp))  # <class 'configparser.SectionProxy'>

# sp = temp_config['MySection']
# print(sp.get('Key1'))
