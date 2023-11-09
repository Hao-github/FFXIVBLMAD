import pandas as pd
from buff import get_all_marker, getBuffDict


class AdAnalysiser:
    def __init__(
        self, damage_log: str, fight: str, tracks: str, criticalNum: int, directNum: int
    ) -> None:
        self.damageDf: pd.DataFrame = pd.read_csv(damage_log)
        self.castDf: pd.DataFrame = pd.read_csv(fight)
        self.markerDf: pd.DataFrame = get_all_marker(tracks)
        self.untargetableDf = self.markerDf.query(
            "markerType=='Untargetable'"
        ).drop_duplicates()
        self.buffDf = (
            self.markerDf.query("markerType=='Info'")
            .drop_duplicates()
            .assign(
                percentage=lambda x: x["description"].map(
                    getBuffDict(criticalNum, directNum)
                )
            )
        )
        self.endTime: float = self.damageDf["time"].iloc[-1]

    def calCastTime(self, sourceRow):
        ret = sourceRow["damageSource"].split("@")
        return ret[0], float(ret[1]) - 27

    def calSnapshotTime(self, df):
        df["castTime"].fillna(0.5, inplace=True)
        return df.eval("snapshotTime = beginCastTime + castTime - 0.5")

    def removeUntargetableTime(self, df):
        isUntargetable = df["time"].apply(
            lambda x: self.untargetableDf.eval("time < @x < time + duration").any()
        )
        return df[~isUntargetable]

    def dealDamageDf(self) -> pd.DataFrame:
        return (
            self.damageDf.pipe(self.removeUntargetableTime)
            .join(self.damageDf.apply(self.calCastTime, axis=1, result_type="expand"))
            .rename({0: "action", 1: "beginCastTime"}, axis=1)
            .groupby(by="damageSource", as_index=False, sort=False)
            .agg(
                {
                    "potency": "sum",
                    "time": "first",
                    "action": "first",
                    "beginCastTime": "first",
                }
            )
        )

    def calBuffOnDamageDf(self) -> pd.DataFrame:
        return (
            pd.merge(
                self.dealDamageDf().round(5),
                self.castDf.rename({"time": "beginCastTime"}, axis=1).round(5),
                how="left",
                on=["beginCastTime", "action"],
            )
            .drop(["damageSource", "isGCD"], axis=1)
            .pipe(self.calSnapshotTime)
            .assign(
                buff=lambda x: x["snapshotTime"].apply(
                    lambda x: (
                        self.buffDf[self.buffDf.eval("time < @x < time + duration")][
                            "percentage"
                        ]
                        + 1
                    ).product()
                ),
                realPotency=lambda x: x["potency"] * x["buff"],
            )
        )

    def getEndTime(self) -> float:
        return self.damageDf["time"].iloc[-1]

    def getActiveTime(self) -> float:
        return self.getEndTime() - self.untargetableDf["duration"].sum()
