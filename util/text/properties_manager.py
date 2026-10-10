from jproperties import Properties


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":
    file_path = "util/text/config.properties"

    p = Properties()
    p.properties
    # 1. 파일 읽기
    with open(file_path, "rb") as f:
        p.load(f)

    # 값 가져오기 (기본적으로 utf-8 또는 iso-8859-1 디코딩 처리)
    db_url = p.get("database.url").data
    print(db_url)

    # 2. 값 수정 및 쓰기
    p["database.timeout"] = "30"
    with open("config.properties", "wb") as f:
        p.store(f, encoding="utf-8")


    #========= 단순 읽기용
    def load_properties(filepath):
        properties = {}
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 빈 줄이나 주석(#, !) 건너뛰기
                if not line or line.startswith('#') or line.startswith('!'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    properties[key.strip()] = value.strip()
        return properties

    # 사용 예시
    props = load_properties("config.properties")
    print(props.get("database.url"))
