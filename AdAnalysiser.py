import json
import pandas as pd


class AdAnalysiser:
    def __init__(
        self,
        damage_log: str,
        fight: str,
        tracks: str,
        criticalNum: int,
        directNum: int,
        buff: str = "黑魔ad计算器团辅名称命名.xls",
    ) -> None:
        markerDf = pd.DataFrame()
        for track in json.loads(open(tracks, "r", encoding="utf-8").read())["tracks"]:
            markerDf = markerDf._append(track["markers"], ignore_index=True)  # type: ignore

        # 计算初始df
        self.damageDf: pd.DataFrame = pd.read_csv(damage_log)
        untargetableDf = markerDf.query("markerType=='Untargetable'").drop_duplicates()
        isUntargetable = self.damageDf["time"].apply(
            lambda x: untargetableDf.eval("time < @x < time + duration").any()
        )
        self.damageDf = self.damageDf[~isUntargetable]

        self.activeTime: float = (
            self.damageDf["time"].iloc[-1] - untargetableDf["duration"].sum()
        )

        self.critRate = int(200 * (criticalNum - 400) / 1900 + 50) / 1000
        self.critDamage = int(200 * (criticalNum - 400) / 1900 + 400) / 1000
        self.directRate = int(550 * (directNum - 400) / 1900) / 1000

        self.castDf: pd.DataFrame = (
            pd.read_csv(fight).rename({"time": "beginCastTime"}, axis=1).round(5)
        )
        self.buffDf: pd.DataFrame = (
            pd.read_excel(buff)
            .melt(
                id_vars=["增伤百分比", "暴击率百分比", "直击率百分比"],
                value_vars=["中文", "英文", "日文"],
            )
            .merge(
                markerDf.query("markerType=='Info'").drop_duplicates(),
                how="right",
                left_on="value",
                right_on="description",
            )
            .rename(
                {
                    "增伤百分比": "buff",
                    "暴击率百分比": "critRate",
                    "直击率百分比": "dirRate",
                },
                axis=1,
            )
        )

    def helper(self, df):
        critical = (df["critRate"].sum() * self.critDamage) / (
            1 + self.critRate * self.critDamage
        ) + 1
        direct = df["dirRate"].sum() * 0.25 / (1 + self.directRate)
        return (df["buff"] + 1).product() * (critical + 1) * (direct + 1)

    def getAnswer(self):
        return (
            self.damageDf.assign(
                action=self.damageDf.damageSource.str.split("@").str[0],
                beginCastTime=self.damageDf.damageSource.str.split("@")
                .str[1]
                .astype(float)
                - 27,
            )
            .groupby(by="damageSource", as_index=False, sort=False)
            .agg(
                {
                    "potency": "sum",
                    "time": "first",
                    "action": "first",
                    "beginCastTime": "first",
                }
            )
            .round(5)
            .merge(self.castDf, how="left", on=["beginCastTime", "action"])
            .drop(["damageSource", "isGCD"], axis=1)
            .fillna(0.5)
            .assign(
                snapshotTime=lambda x: x["beginCastTime"] + x["castTime"] - 0.5,
                buff=lambda x: x["snapshotTime"].apply(
                    lambda y: self.helper(
                        self.buffDf.query("time < @y < time + duration")
                    )
                ),
                realPotency=lambda x: x["potency"] * x["buff"],
            )
        )
