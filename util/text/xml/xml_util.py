from typing import Dict, List, Optional
import xml.etree.ElementTree as ET

from util.text.file_util import FileUtil
from util.str_util import Str
from util.list_util import ListUtil
from util.text.log_util import LogUtil


class AttrNode:
    def __init__(self, tag_name: str, attrs: Optional[Dict[str, str]]=None):
        """_summary_
        tag name without content
        Args:
            name (str): _description_
            attrs (Optional[Dict[str, str]], None): attrs
        """
        self._tag_name: str = tag_name
        
        self.logger = LogUtil.get_logger(__file__)
        
        self._attrs_key_set: set = set()
        self._attrs: Dict[str, str] = attrs if attrs else {}
    
    def has_attr(self, attr_name: str) -> bool:
        """_summary_
        check if attr exists
        Args:
            attr_name (str): _description_
        Returns:
            bool: _description_
        """
        return attr_name.strip() in self._attrs_key_set
    
    def add_attrs_key(self, key: str):
        if self.has_attr(key):
            return False
        self._attrs_key_set.add(key)
        return True
    
    def remove_attrs_key(self, key: str):
        if self.has_attr(key):
            self._attrs_key_set.remove(key)
            return True
        return False
    
    def clear_attrs(self):
        self._attrs_key_set = set()
        self._attrs = {}
    
    def attrs_keys(self) -> set:
        """_summary_
        get attr name set
        Returns:
            set: attr name set
        """
        return self._attrs_key_set

    def get_tag_name(self) -> str:
        """_summary_
        get tag name
        Returns:
            str: tag name
        """
        return self._tag_name
    
    def set_tag_name(self, tag_name: str):
        """_summary_
        set tag name
        Args:
            name (str): tag name
        """
        self._tag_name = tag_name.strip()
    
    def get_attr_value(self, attr_name: str) -> str:
        """_summary_
        attr value
        Args:
            attr_name (str): attr name
        Returns:
            str: attr value or None
        """
        if Str.is_blank_dict(self._attrs):
            return None
        
        key = attr_name.strip()
        if self.has_attr(key):
            return self._attrs[key]
        return None

    def add_attr(self, attr_name: str, attr_value) -> bool:
        """_summary_
        append attr
        Args:
            name (str): attr name
            value (variable): attr value
        """
        key = attr_name.strip()
        if self.add_attrs_key(key):
            self._attrs[key] = str(attr_value).strip()
            return True
        self.logger.debug(f"이미 존재하는 attr name입니다. name[{attr_name}]")
        return False
    
    def remove_attr(self, attr_name: str) -> tuple:
        """_summary_
        remove attr with name
        Args:
            name (str): attr name
        """
        key = attr_name.strip()
        if self.remove_attrs_key(key=key):
            value = self._attrs[key]
            del self._attrs[key]
            return (key, value)
        self.logger.debug(f"존재하지 않는 attr name입니다. name[{key}]")
        return None

    def get_attrs(self) -> Dict[str, str]:
        """_summary_
        all attrs
        Returns:
            Dict[str, str]: all attrs
        """
        return self._attrs
    
    def set_attrs(self, attrs: Dict[str, str]):
        """_summary_
        attrs at all
        Args:
            attrs (Dict[str, str]): attrs all
        """
        self.clear_attrs()
        for attr in attrs:
            self.add_attr(attr_name=attr, attr_value=attrs[attr])
    
    def get_non_text_tag(self) -> str:
        """_summary_
        none text tag
        Returns:
            str: <name attrs />
        """
        sb = ListUtil.StrBuilder(f"<{self._tag_name}")
        if self._attrs and 0 < len(self._attrs):
            for key, value in self._attrs.items():
                sb.append(f' {key}="{value}"')
        
        sb.append(" />")
        return sb.to_string("")
    
    def get_start_tag(self) -> str:
        """_summary_
        start tag
        Returns:
            str: <name attrs>
        """
        sb = ListUtil.StrBuilder(f"<{self._tag_name}")
        if self._attrs and 0 < len(self._attrs):
            for key, value in self._attrs.items():
                sb.append(f' {key}="{value}"')
        
        sb.append(">")
        return sb.to_string("")
    
    def get_end_tag(self) -> str:
        """_summary_
        end tag
        Returns:
            str: </name>
        """
        return f"</{self._tag_name}>"
    
    def attr_count(self) -> int:
        """_summary_
        count attrs
        Returns:
            int: count attrs or 0
        """
        if self._attrs:
            return len(self._attrs)
        return 0
    
    def to_string(self) -> str:
        """_summary_
        전체 데이터 구조화 <name attrs />
        Returns:
            str: <name attrs />
        """
        return self.get_non_text_tag()
    
    
class Field(AttrNode):
    def __init__(self, tag_name: str="field", attrs: Optional[Dict[str, str]]=None, text: str=None):
        """_summary_
        field element class
        Args:
            tag_name (str, field): _description_. Defaults to "field".
            attrs (Optional[Dict[str, str]], {}): _description_. Defaults to {}.
            text (str, ""): _description_. Defaults to "".
        """
        super().__init__(tag_name, attrs)
        
        # 생성자에서 처음에 None 또는 빈 딕셔너리로 타입을 확실히 명시해 둡니다.
        self._text: str = "" if Str.is_blank(text) else text.strip()

    def set_text(self, text: str):
        self._text = text.strip()
    
    def get_text(self) -> str:
        """_summary_
        get text content
        1. text가 존재하면 text 반환
        Returns:
            str: "" if no text else text.strip()
        """
        return self._text
    
    def to_string(self, tab: str = "") -> str:
        """_summary_
        전체 데이터 구조화
        1. 시작 태그 + 내용 + 종료 태그
        Returns:
            str: xml string 시작 태그 + 내용 + 종료 태그
        """
        if Str.is_blank(self._text):
            return f"{tab}{self.get_non_text_tag()}"
        
        sb = ListUtil.StrBuilder(f"{tab}{self.get_start_tag()}").append(self._text).append(self.get_end_tag())
        return sb.to_string("")


class Fields(AttrNode):
    def __init__(self, tag_name: str, attrs: Optional[Dict[str, str]]=None, fields: Optional[List[Field]]=None):
        """_summary_
        item or head element class
        Args:
            tag_name (str): _description_
            attrs (Optional[Dict[str, str]], {}): _description_. Defaults to {}.
            fields (List[Field], []): _description_. Defaults to [Field]=[].
        """
        super().__init__(tag_name, attrs)
        
        self.logger = LogUtil.get_logger(__file__)
        
        self.clear_fields()
        self.set_fields(fields)
    
    def clear_fields(self):
        self._fields_key_set: set = set()
        self._fields: list[Field] = []
    
    def fields_keys(self) -> set:
        """_summary_
        get fields key set
        Returns:
            set: _description_
        """
        return self._fields_key_set
    
    def contains_key(self, key_name: str) -> bool:
        """_summary_
        if key set contains key_name
        Args:
            key_name (str): _description_
        Returns:
            bool: _description_
        """
        return key_name in self._fields_key_set
    
    def add_fields_key(self, key: str) -> bool:
        if self.contains_key(key):
            return False
        self._fields_key_set.add(key)
        return True
    
    def remove_fields_key(self, key: str) -> bool:
        if self.contains_key(key):
            self._fields_key_set.remove(key)
            return True
        return False
    
    def get_field_by_index(self, index: int) -> Field:
        """_summary_
        get field by index
        Args:
            index (int): index of field
        Returns:
            Field: _description_
        """
        if 0 <= index < len(self._fields):
            return self._fields[index]
        return None

    def get_field_by_tag(self, tag_name: str) -> Field:
        """_summary_
        get field with tag name
        Args:
            tag_name (str): tag name
        Returns:
            Field: field with the specified tag name, or None if not found
        """
        if not self._fields or len(self._fields) < 1:
            self.logger.debug(f"필드가 없습니다.")
            return None
        
        return next((field for field in self._fields if field.get_tag_name() == tag_name), None)
    
    def get_field_by_text(self, text: str) -> Field:
        """_summary_
        search text and find then return field or item
        Args:
            text (str): content
        Returns:
            Field: field containing text, or None if not found
        """
        if not self._fields or len(self._fields) < 1:
            return None
        
        return next((field for field in self._fields if field.get_text() == text), None)

    def add_field(self, field: Field) -> bool:
        """_summary_
        append field
        Args:
            field (Field): 추가할 필드
        """
        self.logger.debug("하위 클래스에서 구현하세요.")
        return False
    
    def remove_field_by_index(self, index: int) -> Field:
        """_summary_
        지정된 인덱스의 필드를 제거합니다.
        1. 인덱스가 유효한 범위에 있으면 해당 필드 제거 후 True 반환
        2. 인덱스가 범위를 벗어나면 False 반환
        Args:
            index (int): index of field to remove
        Returns:
            bool: True if removed else False
        """
        field = self.get_field_by_index(index=index)
        if field:
            return self.remove_field(field=field)
        return None
    
    def remove_field_by_tag(self, tag_name: str) -> Field:
        """_summary_
        지정된 태그 이름을 가진 필드를 제거합니다.
        1. 필드가 없거나, 해당 태그 이름을 가진 필드가 없으면 False 반환
        2. 필드가 존재하고, 해당 태그 이름을 가진 필드가 존재하면 해당 필드 제거 후 True 반환
        Args:
            tag_name (str): tag name of field to remove
        Returns:
            bool: True if removed else False
        """
        field = self.get_field_by_tag(tag_name=tag_name)
        if field:
            return self.remove_field(field=field)
        return None
    
    def remove_field_by_text(self, text: str) -> Field:
        """_summary_
        지정된 텍스트를 가진 필드를 제거합니다.
        1. 필드가 없거나, 해당 텍스트를 가진 필드가 없으면 False 반환
        2. 필드가 존재하고, 해당 텍스트를 가진 필드가 존재하면 해당 필드 제거 후 True 반환
        Args:
            text (str): text of field to remove
        Returns:
            bool: True if removed else False
        """
        field = self.get_field_by_text(text=text)
        if field:
            return self.remove_field(field=field)
        return None
    
    def remove_field(self, field: Field) -> Field:
        """_summary_
        지정된 필드를 제거합니다.
        1. 필드가 존재하면 제거 후 True 반환
        2. 필드가 None이면 False 반환
        Args:
            field (Field): field to remove
        Returns:
            bool: True if removed else False
        """
        self.logger.debug("하위 클래스에서 구현하세요.")
        return None
    
    def get_fields(self) -> list:
        """_summary_
        get field list
        1. 필드가 존재하면 필드 리스트 반환
        Returns:
            list: [] if no fields else field list
        """
        return self._fields
    
    def set_fields(self, fields: List[Field]=None):
        """_summary_
        set field list
        1. 기존 필드 리스트를 새 필드 리스트로 교체합니다.
        2. 상속 받는 클래스에서 구현
        3. 필드 중복 체크
        4. 필드 키 설정 (Head에서는 attr_name, Item에서는 tag_name)
        Args:
            fields (List, []): _description_. Defaults to [].
        """
        if fields:
            for field in fields:
                self.add_field(field=field)
    
    def fields_count(self) -> int:
        """_summary_
        count fields
        1. 필드가 존재하면 필드 개수를 반환
        Returns:
            int: 0 if no fields else count
        """
        if self._fields:
            return len(self._fields)
        return 0
    
    def to_string(self, tab: str="\t") -> str:
        """_summary_
        전체 데이터 구조화
        Args:
            tab (str, '\t'): 들여 쓰기
        Returns:
            str:
            <item attrs>
                <field attrs> text </field>
                <field attrs> text </field>
            </item>
        """
        if Str.is_blank_list(self._fields):
            return f"{tab}{self.get_non_text_tag()}"
        
        sb = ListUtil.StrBuilder(f"{tab}{self.get_start_tag()}")
        for field in self._fields:
            sb.append(f"\n{field.to_string(tab + '\t')}")
        
        sb.append(f"\n{tab}{self.get_end_tag()}")
        return sb.to_string("")


class Head(Fields):
    def __init__(self, tag_name: str="head", attrs: Optional[Dict[str, str]] = None, fields: Optional[List[Field]] = None):
        """_summary_
        head element class
        1. tag_name: "head" (default)
        Args:
            tag_name (str, "head"): The name of the head element. Defaults to "head".
            attrs (Optional[Dict[str, str]], None): Attributes for the head element. Defaults to None.
            fields (List, None): Fields for the head element. Defaults to [].
        """
        super().__init__(tag_name, attrs, fields)
        
        self.logger = LogUtil.get_logger(__file__)
    
    def add_field(self, field) -> bool:
        """_summary_
        필드 추가
        Args:
            field (Field): 추가할 필드
        Returns:
            Head: self
        """
        key = field.get_attr_value("name")
        if self.add_fields_key(key):
            self._fields.append(field)
            return True
        self.logger.debug(f"{key}가 이미 존재합니다.")
        return False
    
    def remove_field(self, field) -> Field:
        """_summary_
        필드 삭제
        Args:
            field (Field): 삭제할 필드
        Returns:
            Field: 삭제된 필드 or None
        """
        key = field.get_attr_value("name")
        if self.remove_fields_key(key):
            self._fields.remove(field)
            return field
        self.logger.debug(f"{key}가 존재하지 않습니다.")
        return None
    
    
class Item(Fields):
    def __init__(self, tag_name: str="item", attrs: Optional[Dict[str, str]] = None, fields: List = []):
        """_summary_
        item element class
        1. tag_name: "item" (default)
        Args:
            tag_name (str, "item"): The name of the item element. Defaults to "item".
            attrs (Optional[Dict[str, str]], None): Attributes for the item element. Defaults to None.
            fields (List, None): Fields for the item element. Defaults to [].
        """
        super().__init__(tag_name, attrs, fields)
        
        self.logger = LogUtil.get_logger(__file__)
    
    def add_field(self, field) -> bool:
        key = field.get_tag_name()
        if self.add_fields_key(key):
            self._fields.append(field)
            return True
        self.logger.debug(f"{key}가 이미 존재합니다.")
        return False
    
    def remove_field(self, field) -> Field:
        key = field.get_tag_name()
        if self.remove_fields_key(key):
            self._fields.remove(field)
            return field
        self.logger.debug(f"{key}가 존재하지 않습니다.")
        return None


class Items(AttrNode):
    def __init__(self, tag_name: str="items", attrs: Optional[Dict[str, str]] = None):
        """_summary_
        items element class
        1. tag_name: "items" (default)
        Args:
            tag_name (str, "items"): The name of the items element. Defaults to "items".
            attrs (Optional[Dict[str, str]], None): Attributes for the items element. Defaults to None.
        """
        super().__init__(tag_name, attrs)
        
        self.logger = LogUtil.get_logger(__file__)
        
        self.clear_items()
    
    def items_keys(self) -> set:
        return self._items_key_set
    
    def contains_key(self, key_name: str) -> bool:
        return key_name in self._items_key_set
    
    def add_items_key(self, key: str=None) -> bool:
        if self.contains_key(key):
            return False
        self._items_key_set.add(key)
        return True
    
    def remove_items_key(self, key: str=None) -> bool:
        if self.contains_key(key):
            self._items_key_set.remove(key)
            return True
        return False
    
    def clear_items(self):
        self._items_key_set: set = set()
        self._items: list[Item] = []
    
    def items_count(self) -> int:
        """_summary_
        count items
        1. 아이템이 존재하면 아이템 개수를 반환
        Returns:
            int: 0 if no items else count
        """
        if self._items:
            return len(self._items)
        return 0
    
    def get_item_by_index(self, index: int) -> Item:
        """_summary_
        get item by index
        Args:
            index (int): 아이템 인덱스
        Returns:
            Item: 아이템 or None
        """
        if 0 <= index < len(self._items):
            return self._items[index]
        self.logger.debug(f"인덱스 범위를 벗어났습니다. index[{index}]")
        raise None
    
    def get_item_by_tagtext(self, tag_name: str, text: str) -> Item:
        """_summary_
        get item by tag name and text
        1. 지정된 태그 이름과 값이 일치하는 첫 번째 Item을 반환합니다.
        2. 일치하는 Item이 없으면 None 반환
        Args:
            tag_name (str): 태그 이름
            text (str): 텍스트 값
        Returns:
            Item: 일치하는 Item 객체 또는 None
        """
        txt = text.strip()
        for item in self._items:
            title_fld = item.get_field_by_tag(tag_name=tag_name)
            if title_fld and title_fld.get_text().strip() == txt:
                return item
        return None

    def add_item(self, item: Item) -> bool:
        """_summary_
        append item
        Args:
            item (Item): 추가할 아이템
        """
        field = item.get_field_by_tag("path")
        if field:
            key = field.get_text()
            if self.add_items_key(key=key):
                self._items.append(item)
                return True
            self.logger.debug(f"{key}가 이미 존재합니다.")
        self.logger.debug(f"item에 path tag를 가지고 있지 않습니다.")
        return False
    
    def remove_item(self, item: Item=None) -> Item:
        """_summary_
        remove item
        Args:
            item (Item): 제거할 아이템
        Returns:
            bool: True if del else False
        """
        if item:
            if item in self._items:
                field = item.get_field_by_tag("path")
                key = field.get_text()
                if self.remove_items_key(key):
                    self._items.remove(item)
                    return item
        self.logger.debug(f"Item이 존재하지 않습니다.")
        return None
    
    def remove_item_first(self) -> Item:
        if self._items:
            return self._items.pop(0)
        return None
    
    def remove_item_last(self) -> Item:
        if self._items:
            return self._items.pop()
        return None
    
    def remove_item_by_index(self, index: int) -> Item:
        """_summary_
        remove item by index
        Args:
            index (int): 제거할 아이템 인덱스
        Returns:
            bool: True if del else False
        """
        item = self.get_item_by_index(index=index)
        if item:
            return self.remove_item(item=item)
        
        self.logger.debug(f"인덱스 범위를 벗어났습니다. index[{index}]")
        return None
    
    def remove_item_by_tagtext(self, tag_name: str, text: str) -> Item:
        """_summary_
        remove item by tag name and text
        1. 지정된 태그 이름과 값이 일치하는 첫 번째 Item을 제거합니다.
        2. 일치하는 Item이 없으면 False 반환
        Args:
            tag_name (str): 태그 이름
            text (str): 텍스트 값
        Returns:
            bool: True if removed else False
        """
        item = self.get_item_by_tagtext(tag_name=tag_name, text=text)
        if item:
            self._items.remove(item)
            return item
        return None
    
    def get_items(self) -> list:
        """_summary_
        get item list
        1. 아이템이 존재하면 아이템 리스트 반환
        Returns:
            list: [] if no items else item list
        """
        return self._items
    
    def set_items(self, items: list[Item]):
        """_summary_
        set item list
        1. 기존 아이템 리스트를 새 아이템 리스트로 교체합니다.
        Args:
            items (list[Item]): 새 아이템 리스트
        """
        self.clear_items()
        for item in items:
            self.add_item(item=item)
    
    def get_item_tagtext_list(self, tag_name: str) -> list[str]:
        """_summary_
        지정된 태그 이름을 가진 모든 Field의 텍스트를 리스트로 반환합니다.
        Args:
            tag_name (str): tag name
        Returns:
            list[str]: tag_name에 해당하는 모든 Field의 텍스트를 리스트로 반환합니다. Field가 존재하지 않으면 빈 리스트를 반환합니다.
        """
        datalist = []
        for item in self._items:
            field = item.get_field_by_tag(tag_name=tag_name)
            if field:
                datalist.append(field.get_text().strip())
            else:
                self.logger.debug(f"{tag_name}의 이름을 가진 필드가 존재하지 않습니다.")
        return datalist
    
    def to_string(self, tab: str="\t") -> str:
        """_summary_
        전체 데이터 구조화
        Args:
            tab (str, '\t'): 들여 쓰기
        Returns:
            str:
            <items attrs>
                <item attrs>
                    <field attrs> text </field>
                    <field attrs> text </field>
                </item>
            </items>
        """
        if Str.is_blank_list(self._items):
            return f"{tab}{self.get_non_text_tag()}"
        
        sb = ListUtil.StrBuilder(f"{tab}{self.get_start_tag()}")
        for item in self._items:
            sb.append(f"\n{item.to_string(tab + '\t')}")

        sb.append(f"\n{tab}{self.get_end_tag()}")
        return sb.to_string("")


class XmlManager(Field):
    def __init__(self, tag_name = "data", attrs: Optional[Dict[str, str]] = None, file_path: str=None, xml_data: str=None):
        """_summary_
        data structure for xml file
        1. file_path가 존재하면 해당 파일을 읽어 xml_data로 변환
        2. xml_data가 존재하면 해당 문자열을 파싱하여 data 구조로 변환
        3. file_path와 xml_data가 모두 존재하지 않으면 빈 data 구조 생성
        4. file_path와 xml_data가 모두 존재하면 file_path를 우선으로 처리
        5. file_path가 존재하면 load_from_file() 호출
        6. xml_data가 존재하면 load_from_string() 호출
        7. file_path와 xml_data가 모두 존재하지 않으면 빈 data 구조 생성
        8. xml_root은 xml.etree.ElementTree.Element 객체로, XML의 루트 요소를 나타냅니다.
        Args:
            tag_name (str, "data"): root tag name. Defaults to "data".
            attrs (Optional[Dict[str, str]], None): root tag attributes. Defaults to None.
            file_path (str, None): path to the XML file. Defaults to None.
            xml_data (str, None): XML data as a string. Defaults to None.
        """
        super().__init__(tag_name, attrs)
        
        self._head: Head = Head()
        self._items: Items = Items()

        self.xml_root: Optional[ET.Element] = None
        
        self.logger = LogUtil.get_logger(__file__)
        
        self.file_path = file_path
        # self.xml_data = xml_data
        if self.file_path:
            self.load_from_file(self.file_path)
        elif xml_data:
            self.load_from_string(xml_data)
        
        self.updated = False
    
    def is_updated(self) -> bool:
        """_summary_
        check if data is updated
        Returns:
            bool: True if updated else False
        """
        return self.updated
    
    def set_updated(self, updated: bool):
        """_summary_
        set updated flag
        Args:
            updated (bool): True if updated else False
        """
        self.updated = updated
    
    """ for head -------------------------------------"""
    def clear_head(self):
        self._head = Head()
    
    def head_get(self) -> Head:
        """_summary_
        get head
        Returns:
            Head: head object
        """
        return self._head
    
    def head_set(self, head: Head):
        """_summary_
        set head
        Args:
            head (Head): head object
        """
        self._head = head
        self.updated = True
    
    def head_add_field(self, fld: Field):
        """_summary_
        add field to head
        Args:
            fld (Field): field object
        """
        if self._head.add_field(field=fld):
            self.updated = True
    
    def head_get_field_by_tag(self, tag_name: str) -> Field:
        """_summary_
        get field by tag name from head
        Args:
            tag_name (str): tag name of field to return
        Returns:
            Field: Field object if found else None
        """
        return self._head.get_field_by_tag(tag_name=tag_name)
    
    def head_get_field_by_index(self, index: int) -> Field:
        """_summary_
        get field by index from head
        Args:
            index (int): index of field to return
        Returns:
            Field: Field object if found else None
        """
        return self._head.get_field_by_index(index=index)
    
    def head_remove_field_by_index(self, index: int) -> Field:
        """_summary_
        지정된 인덱스의 Head의 Field를 제거합니다.
        1. 인덱스가 유효한 범위에 있으면 해당 Field 제거 후 True 반환
        2. 인덱스가 범위를 벗어나면 False 반환
        Args:
            index (int): index of field to remove
        Returns:
            Field: 제거된 필드
        """
        removed = self._head.remove_field_by_index(index=index)
        if removed:
            self.updated = True
        return removed
    
    def head_remove_field_by_tag(self, tag_name: str) -> Field:
        """_summary_
        지정된 태그 이름을 가진 Head의 Field를 제거합니다.
        1. Head가 없거나, 해당 태그 이름을 가진 Field가 없으면 False 반환
        2. Head가 존재하고, 해당 태그 이름을 가진 Field가 존재하면 해당 Field 제거 후 True 반환
        Args:
            tag_name (str): tag name of field to remove
        Returns:
            bool: True if removed else False
        """
        removed = self._head.remove_field_by_tag(tag_name=tag_name)
        if removed:
            self.updated = True
        return removed
    
    def head_remove_field(self, field: Field) -> Field:
        """_summary_
        지정된 Field를 제거합니다.
        1. Field가 없거나, 해당 Field가 Head에 없으면 False 반환
        2. Field가 존재하고, Head에 존재하면 해당 Field 제거 후 True 반환
        Args:
            field (Field): field to remove
        Returns:
            bool: True if removed else False
        """
        removed = self._head.remove_field(field=field)
        if removed:
            self.updated = True
        return removed
    
    def head_get_attr_value(self, attr_name: str) -> str:
        """_summary_
        get head attr value
        Args:
            attr_name (str): attr name
        Returns:
            str: attr value or None
        """
        return self._head.get_attr_value(attr_name=attr_name)
    
    def head_add_attr(self, attr_name: str, attr_value: str):
        """_summary_
        set head attr
        Args:
            attr_name (str): attr name
            attr_value (str): attr value
        """
        if self._head.add_attr(attr_name=attr_name, attr_value=attr_value):
            self.updated = True
    
    def head_remove_attr(self, attr_name: str) -> tuple:
        """_summary_
        remove head attr
        Args:
            attr_name (str): attr name
        Returns:
            bool: True if removed else False
        """
        removed = self._head.remove_attr(attr_name=attr_name)
        if removed:
            self.updated = True
        return removed
    
    def head_get_attrs(self) -> Optional[Dict[str, str]]:
        """_summary_
        get head attrs
        Returns:
            Optional[Dict[str, str]]: head attrs or None
        """
        return self._head.get_attrs()
    
    def head_set_attrs(self, attrs: Dict[str, str]):
        """_summary_
        set head attrs
        Args:
            attrs (Dict[str, str]): head attrs
        """
        self._head.set_attrs(attrs=attrs)
        self.updated = True
    
    """ for items ------------------------------------- """
    def clear_items(self):
        self._items.clear_items()
    
    def items_get(self) -> Items:
        """_summary_
        get items
        Returns:
            Items: items object
        """
        return self._items
    
    def items_set(self, items: Items):
        """_summary_
        set items
        Args:
            items (Items): items object
        """
        self.clear_items()
        self._items = items
        self.updated = True
    
    def items_get_count(self) -> int:
        """_summary_
        아이템 개수를 반환합니다.
        1. 아이템이 존재하면 아이템 개수를 반환
        Returns:
            int: 0 if no items else count
        """
        return self._items.items_count()
    
    def items_get_item_by_index(self, index: int) -> Item:
        """_summary_
        지정된 인덱스의 Item을 반환합니다.
        1. 인덱스가 유효한 범위에 있으면 해당 Item 반환
        2. 인덱스가 범위를 벗어나면 None 반환
        Args:
            index (int): index of item to return
        Returns:
            Item: Item object if found else None
        """
        return self._items.get_item_by_index(index=index)
    
    def items_get_item_by_tagtext(self, tag_name: str, text: str) -> Item:
        """_summary_
        지정된 태그 이름과 값이 일치하는 첫 번째 Item을 반환합니다.
        1. 일치하는 Item이 없으면 None 반환
        Args:
            tag_name (str): tag name of field to search
            text (str): text value of field to search
        Returns:
            Item: Item object if found else None
        """
        return self._items.get_item_by_tagtext(tag_name=tag_name, text=text)
    
    def items_add_item(self, item: Item) -> bool:
        """_summary_
        지정된 Item을 추가합니다.
        1. Item이 존재하면 추가 후 True 반환
        2. Item이 None이면 False 반환
        Args:
            item (Item): item to add
        Returns:
            bool: True if added else False
        """
        if self._items.add_item(item=item):
            self.updated = True
            return True
        return False
    
    def items_remove_item(self, item: Item) -> Item:
        """_summary_
        지정된 Item을 제거합니다.
        1. Item이 존재하면 제거 후 True 반환
        2. Item이 None이면 False 반환
        Args:
            item (Item): item to remove
        Returns:
            Item: item or None
        """
        removed = self._items.remove_item(item=item)
        if removed:
            self.updated = True
        return removed
    
    def items_remove_item_last(self) -> Item:
        """_summary_
        마지막 Item을 찾아 제거합니다.
        1. Item이 없으면 False 반환
        Returns:
            bool: True if removed else False
        """
        removed = self._items.remove_item_last()
        if removed:
            self.updated = True
        return removed
    
    def items_remove_item_first(self) -> Item:
        """_summary_
        첫 번째 Item을 찾아 제거합니다.
        1. Item이 없으면 False 반환
        Returns:
            bool: True if removed else False
        """
        removed = self._items.remove_item_first()
        if removed:
            self.updated = True
        return removed
    
    def items_remove_item_by_index(self, index: int) -> Item:
        """_summary_
        지정된 인덱스의 Item을 제거합니다.
        1. 인덱스가 유효한 범위에 있으면 해당 Item 제거 후 True 반환
        2. 인덱스가 범위를 벗어나면 False 반환
        Args:
            index (int): index of item to remove
        Returns:
            bool: True if removed else False
        """
        removed = self._items.remove_item_by_index(index=index)
        if removed:
            self.updated = True
        return removed
    
    def items_remove_item_by_tagtext(self, tag_name: str, text: str) -> bool:
        """_summary_
        지정된 태그 이름과 값이 일치하는 첫 번째 Item을 찾아 제거합니다.
        1. 일치하는 Item이 없으면 False 반환
        Args:
            tag_name (str): tag name of field to search
            text (str): text value of field to search
        Returns:
            bool: True if removed else False
        """
        removed = self._items.remove_item_by_tagtext(tag_name=tag_name, text=text)
        if removed:
            self.updated = True
        return removed
    
    def items_get_list(self) -> list[Item]:
        """_summary_
        모든 Item을 리스트로 반환합니다.
        Returns:
            list[Item]: 모든 Item의 리스트
        """
        return self._items.get_items()
    
    def items_set_list(self, items: list[Item]):
        """_summary_
        기존 Item 리스트를 새 Item 리스트로 교체합니다.
        Args:
            items (list[Item]): 새 Item 리스트
        """
        self._items.set_items(items=items)
        self.updated = True
    
    def items_get_attr_value(self, attr_name: str) -> str:
        """_summary_
        get items attr value
        Args:
            attr_name (str): attr name
        Returns:
            str: attr value or None
        """
        return self._items.get_attr_value(attr_name=attr_name)
    
    def items_add_attr(self, attr_name: str, attr_value: str):
        """_summary_
        set items attr
        Args:
            attr_name (str): attr name
            attr_value (str): attr value
        """
        if self._items.add_attr(attr_name=attr_name, attr_value=attr_value):
            self.updated = True
    
    def items_remove_attr(self, attr_name: str) -> tuple:
        """_summary_
        remove items attr
        Args:
            attr_name (str): attr name
        Returns:
            bool: True if removed else False
        """
        removed = self._items.remove_attr(attr_name=attr_name)
        if removed:
            self.updated = True
        return removed
    
    def items_get_attrs(self) -> Dict[str, str]:
        """_summary_
        get items attrs
        Returns:
            Dict[str, str]: items attrs or {}
        """
        return self._items.get_attrs()
    
    def items_set_attrs(self, attrs: Dict[str, str]):
        """_summary_
        set items attrs
        Args:
            attrs (Dict[str, str]): items attrs
        """
        self._items.set_attrs(attrs=attrs)
        self.updated = True
    
    def items_get_tagtext_list(self, tag_name: str) -> list[str]:
        """_summary_
        지정된 태그 이름을 가진 모든 Field의 텍스트를 리스트로 반환합니다.
        1. Field가 존재하지 않으면 빈 리스트를 반환합니다.
        Args:
            tag_name (str): tag name
        Returns:
            list[str]: field.get_text()를 리스트로 반환, Field가 존재하지 않으면 빈 리스트 반환
        """
        return self._items.get_item_tagtext_list(tag_name=tag_name)
    
    def save(self, file_path: str=None):
        """_summary_
        현재 데이터 구조를 기반으로 xml_root를 갱신하고, xml_root를 문자열로 변환하여 파일에 저장합니다.
        1. 변경된 내용이 없으면 로그를 남기고 종료
        Args:
            file_path (str, None): xml file path, None이면 self.file_path 사용
        """
        if not self.updated:
            self.logger.debug(f"변경된 내용이 없습니다.({file_path})")
            return
        
        save_file = file_path if file_path else self.file_path
        if save_file is None:
            self.logger.debug("저장할 파일 경로가 없습니다.")
            return
        
        xml_data = self.to_string()
        if xml_data is None:
            self.logger.debug("저장할 XML 데이터가 없습니다.")
            return
        
        FileUtil.writeln(file_path=save_file, string=xml_data, mode="w")
        self.logger.debug(f"XML 파일을 저장했습니다.({save_file})")
    
    def load_from_file(self, file_path):
        """_summary_
        xml file to data structure
        1. file_path가 존재하지 않으면 로그를 남기고 종료
        Args:
            file_path (str): xml file path
        """
        import os
        if os.path.exists(file_path):
            xml_string = FileUtil.read_all(self.file_path)
            self.load_from_string(xml_string)
        else:
            self.logger.debug(f"파일이 존재하지 않습니다.({file_path})")
    
    def update_from_data(self) -> bool:
        """_summary_
        현재 데이터 구조를 기반으로 xml_root를 갱신합니다.
        1. 변경된 내용이 없으면 False 반환
        Returns:
            bool: True if updated else False
        """
        if not self.updated:
            self.logger.debug("변경된 내용이 없습니다.")
            return False
        
        xml_string = self._to_string()
        self.load_from_string(xml_string=xml_string)
        return True

    def load_from_string(self, xml_string):
        """_summary_
        xml string to data structure
        1. xml_string이 비어있으면 로그를 남기고 종료
        2. xml_string을 파싱하여 xml_root에 저장
        3. xml_root를 순회하며 data 구조를 구성
        Args:
            xml_string (str): xml string
        """
        if Str.is_blank(xml_string):
            self.logger.debug("xml_string이 비어있습니다.")
            return
        
        self.logger.debug(f"{xml_string}을 파싱하여 데이터 구조를 구성합니다.")
        self.xml_root = ET.fromstring(xml_string)
        item: Item = None
        for it in self.xml_root.iter():
            match it.tag:
                case "data" | "head" | "items":
                    pass
                case "field":
                    field = Field()
                    for key, value in it.items():
                        field.add_attr(key, value)
                    self.head_add_field(field)
                case "item":
                    if item:
                        self.items_add_item(item)
                    item = Item()
                    # self.items_add_item(item)
                case _:
                    field = Field(it.tag)
                    for key, value in it.items():
                        field.add_attr(key, value)
                    field.set_text(it.text.strip())
                    if item:
                        item.add_field(field)
        if item:
            self.items_add_item(item)
        self.updated = False
    
    def _to_string(self) -> str:
        """_summary_
        data structure to xml string
        1. 시작 태그를 추가
        Returns:
            str: xml string from data structure
        """
        sb = ListUtil.StrBuilder().append(self.get_start_tag())
        
        # 1. 시작 태그 (예: <items>)
        # get_start_tag()가 없다면 기본 문자열 구조로 대체 가능합니다.
        
        # 2. Head 정보가 있다면 문자열에 포함
        if self._head:
            sb.append(self._head.to_string("\t"))
        
        # 3. 추가된 Item들을 순회하며 각각의 문자열을 추가 (이 부분이 누락되었었습니다!)
        if self._items:
            sb.append(self._items.to_string("\t"))
        
        sb.append(self.get_end_tag())
        
        self.logger.debug("데이터 구조를 기반으로 XML 문자열을 생성했습니다.")
        return sb.to_string("\n") # 줄바꿈을 주면 알아보기 더 쉽습니다.
    
    def to_string(self) -> str:
        """_summary_
        data structure to xml string
        1. update_from_data()를 호출하여 변경된 내용이 있는지 확인
        Returns:
            str: xml string from data structure
        """
        self.update_from_data()
        
        if self.xml_root is not None and 0 < len(self.xml_root):
            # 4. 예쁜 들여쓰기(Indent) 적용
            if hasattr(ET, "indent"):
                ET.indent(self.xml_root, space="    ", level=0)
                
            # 5. [핵심] 문자열(bytes)로 추출 후 디코딩하여 str 반환
            # xml_declaration=True를 주면 <?xml version='1.0' encoding='utf-8'?> 선언문이 포함됩니다.
            xml_bytes = ET.tostring(self.xml_root, encoding="utf-8", xml_declaration=True)
            return xml_bytes.decode("utf-8")
        return None


# ==========================================
# 실행 및 통합 파싱 테스트 (Ctrl + F5)
# ==========================================
if __name__ == "__main__":

    file_path = "util/xml/test.plx"
    data = XmlManager(file_path=file_path)
    print(data.to_string())
    
    # head = Head()
    
    # field = Field()
    # field.add_attr("name", "title")
    # field.add_attr("key", "True")
    # field.add_attr("required", "True")
    # head.add_field(field)

    # field = Field()
    # field.add_attr("name", "path")
    # field.add_attr("key", "False")
    # field.add_attr("required", "False")
    # head.add_field(field)
    
    # field = Field()
    # field.add_attr("name", "loop")
    # field.add_attr("key", "False")
    # field.add_attr("required", "False")
    # head.add_field(field)
    # data.head_set(head=head)

    # items = Items("items")
    # item = Item()
    # item.add_field(Field("title", text="test.mkv"))
    # item.add_field(Field("path", text="D:/Workspace/vscde/lotto/videos/movies/test.mkv"))
    # item.add_field(Field("loop", text="False"))
    # items.add_item(item)

    # item = Item()
    # item.add_field(Field("title", text="wonderful.mkv"))
    # item.add_field(Field("path", text="D:/Workspace/vscde/lotto/videos/movies/wonderful.mkv"))
    # item.add_field(Field("loop", text="False"))
    # items.add_item(item)

    # item = Item()
    # item.add_field(Field("title", text="good.avi"))
    # item.add_field(Field("path", text="D:/Workspace/vscde/lotto/videos/movies/good.avi"))
    # item.add_field(Field("loop", text="False"))
    # items.add_item(item)
    
    # data.items_set(items=items)

    # print()
    # print(data.head_get().to_string(""))
    
    # print()
    # print(data.items_get().to_string(""))

    # data.save(file_path=file_path)
    # print(data.to_string())
    titles = data.items_get_tagtext_list(tag_name="title")
    
    paths = data.items_get_tagtext_list(tag_name="path")
    
    print(titles)
    print(paths)
