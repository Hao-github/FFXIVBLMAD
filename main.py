from myClass.AdAnalysiser import AdAnalysiser
from myClass.Downloader import Downloader
import os
from configparser import ConfigParser

conf = ConfigParser()
conf.read("config.ini", encoding="utf-8")
dataDir = conf["属性"]["chrome缓存目录"].rsplit("\\", maxsplit=1)[0]
criticalNum = int(conf["属性"]["暴击值"])
directNum = int(conf["属性"]["直击值"])

downloader = Downloader(dataDir)
downloader.openWebsite("https://miyehn.me/ffxiv-blm-rotation/")
myDict = {
    "tracks_all.txt": "所有轨道",
    "fight.csv": "csv格式",
    "damage-log.csv": "下载详细伤害结算记录（CSV格式）",
}
for k, v in myDict.items():
    if os.path.exists(downloader.download_dir + "\\" + k):
        os.remove(downloader.download_dir + "\\" + k)
    downloader.downloadFromText(v)

downloader.quit()

analysiser = AdAnalysiser(
    "input/damage-log.csv",
    "input/fight.csv",
    "input/tracks_all.txt",
    criticalNum,
    directNum,
)
result = analysiser.calBuffOnDamageDf()
result.to_csv("output.csv")
realPPS = float(result["realPotency"].sum() / analysiser.getActiveTime())
print("realPPS = " + str(round(realPPS, 5)))
print("具体数据已输出至output.csv")
os.system("pause")
