import json
import pandas as pd


def critcalBuffToDamageBuff(criticalNum: int, critcalBuff: float):
    # 计算暴击buff的实际增伤情况
    percentage = int(200 * (criticalNum - 400) / 1900 + 50) / 1000
    critcalIncrease = int(200 * (criticalNum - 400) / 1900 + 400) / 1000
    return (critcalBuff * critcalIncrease) / (1 + percentage * critcalIncrease)


def DirectBuffToDamageBuff(directNum: int, directBuff: float):
    # 计算直击buff的实际增伤情况
    percentage = int(550 * (directNum - 400) / 1900) / 1000
    return directBuff * 0.25 / (1 + percentage)


def getBuffDict(criticalNum: int, directNum: int):
    return {
        "夺取": 0.05,
        "神秘纹": 0.03,
        "桃园": 0.05,
        "龙肠": 0.05,
        "连祷": critcalBuffToDamageBuff(criticalNum, 0.1),
        "占卜": 0.06,
        "大舞": 0.05,
        "光阴神-初": 0.02,
        "光阴神": 0.06,
        "战斗之声": DirectBuffToDamageBuff(directNum, 0.2),
        "灵护": 0.03,
        "鼓励": 0.05,
        "连环计": critcalBuffToDamageBuff(criticalNum, 0.1),
    }


def get_all_marker(tracks: str) -> pd.DataFrame:
    markerDf = pd.DataFrame()
    for track in json.loads(open(tracks, "r", encoding="utf-8").read())["tracks"]:
        markerDf = markerDf._append(track["markers"], ignore_index=True)  # type: ignore
    return markerDf
