import os
import re
import traceback

from util.str_util import Str
from util.text.log_util import LogUtil
from lotto_main import LottoMain
from util.text.file_util import FileUtil
from vo.number_vo import NumberVO


class CheckWinning(LottoMain):
    def __init__(self, round=0):
        super().__init__()

        if round == 0:
            numbervo: NumberVO = self.getLastVo()
            self.round = numbervo.get_round()
        else:
            self.round = round
            numbervo: NumberVO = self.numberVos[round-1]
        
        self.winning_numbers = set(numbervo.get_numbers())
        self.win_nums = numbervo.toString(isSum=True, isBonus=True)
        
        self.bonus_number = numbervo.get_bonus()

        self.logger = LogUtil.get_logger("LottoFileAnalyzer")

    def check_ticket(self, ticket: list[int]):
        matched_count = len(set(ticket) & self.winning_numbers)
        has_bonus = self.bonus_number in ticket

        # 등수 정의 (삼항 연산 활용)
        rank = (
            5
            if matched_count == 3
            else (
                4
                if matched_count == 4
                else (
                    3
                    if matched_count == 5 and not has_bonus
                    else (
                        2
                        if matched_count == 5 and has_bonus
                        else 1 if matched_count == 6 else 0
                    )
                )
            )
        )

        return {
            "ticket": ticket,
            "matched_count": matched_count,
            "has_bonus": has_bonus,
            "rank": rank,
        }

    def analyze_lotto_file(self, file_path: str):
        """_summary_
        로또 번호를 분석하여 당첨 여부를 체크하는 메서드 - make/round.txt 파일을 분석하여 당첨 여부를 체크합니다.
        Args:
            file_path (str): _description_
        Returns:
            _type_: _description_
        """

        # 1. 조기 반환(Early Return) 패턴 적용: 파일이 아예 없으면 즉시 종료
        if not os.path.exists(file_path):
            self.logger.error(f"파일을 찾을 수 없습니다: {os.path.abspath(file_path)}")
            return  # 함수를 즉시 종료하고 메인으로 돌아감

        self.logger.debug("")
        self.logger.debug(f"*** 분석 시작: {file_path}. =========================")
        # 2. 예외 처리(try-except) 구조로 안전하게 파일 열기
        
        res = {"wins": []}
        res['winning_numbers'] = self.win_nums
        res["winning_numbers"] = res["winning_numbers"].replace("\t", "    ")
        try:
            collected_numbers = []
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    # 1. 상단 로또 조합 패턴 분석 (ex: 06-20-29-33-38-40)
                    if "-" in line and "\t" in line:
                        strs = line.split("\t")
                        ticket = [int(n) for n in strs[0].split("-")]

                        result = self.check_ticket(ticket)
                        """
                        "ticket": ticket,
                        "matched_count": matched_count,
                        "has_bonus": has_bonus,
                        "rank": rank,
                        """
                        if 0 < result["rank"]:
                            res1 = result.copy()
                            res1["numstr"] = strs[0]
                            res["wins"].append(res1)
                            self.logger.debug(
                                f"[조합] {strs[0]} -> 일치: {result['matched_count']}개 (보너스: {result['has_bonus']}) | 결과: {result['rank']}등"
                            )
                        else:
                            self.logger.debug(f"{strs[0]}")

                    # 2. 하단 번호=개수 패턴 분석 (ex: 01 = 1)
                    elif "=" in line:
                        match = re.match(r"(\d+)\s*=\s*(\d+)", line)
                        if match:
                            num = int(match.group(1))
                            collected_numbers.append(num)

            # 3. 하단 수집 번호 최종 결과 도출
            collected_numbers.sort()
            final_matches = set(collected_numbers) & self.winning_numbers
            bonus_match = self.bonus_number in collected_numbers

            sorted(final_matches)
            
            res["selected_numbers_count"] = len(collected_numbers)
            res["selected_numbers"] = ", ".join(str(n) for n in collected_numbers)
            res["final_matches_count"] = len(final_matches)
            res["final_matches"] = ", ".join(str(n) for n in final_matches)
            res["match_bonus"] = bonus_match
            
            self.logger.debug("== 하단 집계 번호 분석 결과 ==")
            self.logger.debug(
                f"- 생성된 번호 리스트({len(collected_numbers)}): {collected_numbers}"
            )
            self.logger.debug(
                f"- 당첨 번호 일치 ({len(final_matches)}개): {list(final_matches)}"
            )
            self.logger.debug(
                f"- 보너스 번호 일치 여부{self.bonus_number}: {'일치' if bonus_match else '불일치'}"
            )
            return res

        except FileNotFoundError:
            # 혹시 모를 동시성 삭제 이슈 방어
            self.logger.error(f"파일 열기 실패: {file_path}가 경로에 없습니다.")

        except Exception as e:
            # 인코딩 에러 등 기타 알 수 없는 에러 방어
            self.logger.error(f"파일 처리 중 예상치 못한 오류 발생: {e}")
            traceback.print_exc()

    def analyze_lotto_all_file(self, file_path: str):
        """_summary_
        로또 번호를 분석하여 당첨 여부를 체크하는 메서드 - make/round_all[filtered].txt 파일을 분석하여 당첨 여부를 체크합니다.
        Args:
            file_path (str): _description_
        Returns:
            _type_: _description_
        """

        # 1. 조기 반환(Early Return) 패턴 적용: 파일이 아예 없으면 즉시 종료
        if not os.path.exists(file_path):
            self.logger.error(f"파일을 찾을 수 없습니다: {os.path.abspath(file_path)}")
            return  # 함수를 즉시 종료하고 메인으로 돌아감

        res_all = {}
        
        self.logger.debug("")
        self.logger.debug(f"*** 분석 시작: {file_path}. =========================")
        # 2. 예외 처리(try-except) 구조로 안전하게 파일 열기
        try:
            wins = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    # 1. 상단 로또 조합 패턴 분석 (ex: 06-20-29-33-38-40)
                    if "-" in line and "\t" in line:
                        nums_str, count = line.split("\t")
                        ticket = [int(n) for n in nums_str.split("-")]

                        result = self.check_ticket(ticket)
                        if 0 < result["rank"]:
                            wins[result["rank"]] += 1

            for rank, count in wins.items():
                if 0 < count:
                    self.logger.debug(f"- {rank}등 당첨 개수: {count}개")
                    res_all[rank] = count
            return res_all
        except FileNotFoundError:
            # 혹시 모를 동시성 삭제 이슈 방어
            self.logger.error(f"파일 열기 실패: {file_path}가 경로에 없습니다.")

        except Exception as e:
            # 인코딩 에러 등 기타 알 수 없는 에러 방어
            self.logger.error(f"파일 처리 중 예상치 못한 오류 발생: {e}")
        
        return None


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":

    checker = CheckWinning()

    round = checker.round

    print(f"== {round}회 로또 당첨 대조 리포트 ==")

    result_filename = FileUtil.RESULT_FILENAME

    filename = FileUtil.get_lotto_make_file(round)
    res1 = checker.analyze_lotto_file(filename)

    filename = FileUtil.get_lotto_make_filtered_file(round)
    res2 = checker.analyze_lotto_all_file(filename)

    filename = FileUtil.get_lotto_make_all_file(round)
    res3 = checker.analyze_lotto_all_file(filename)
    
    print(res1)
    print(res2)
    print(res3)

    print(result_filename)
    
    lst: list[str] = [""]
    lst.append(f"round: {round}")
    lst.append(f"로또 번호: {res1["winning_numbers"].replace("\t", "    ")}")
    lst.append(f"선택 번호: {res1["selected_numbers_count"]}")
    lst.append(res1["selected_numbers"])
    lst.append(f"일치 번호: {res1["final_matches_count"]}    {res1["final_matches"]}    보너스: {res1["match_bonus"]}")
    lst.append("")
    lst.append("당첨 내역")
    if 0 < len(res1["wins"]):
        for win in res1["wins"]:
            lst.append(f"{win['numstr']}    {win['rank']}등    bonus: {win['has_bonus']}")
    else:
        lst.append("당첨 내역이 없습니다.")
    lst.append("")
    lst.append("filtered ----------------")
    for key, value in res2.items():
        lst.append(f"{key}등: {Str.number_format(value)}")
    lst.append("all ---------------------")
    for key, value in res3.items():
        lst.append(f"{key}등: {Str.number_format(value)}")
    
    print("\n".join(lst))
    FileUtil.writeln(result_filename, "\n".join(lst), "a")
    