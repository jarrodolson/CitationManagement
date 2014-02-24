##This program runs through all citations and then saves single record of each
## into a new folder
import glob

inFold = "C:\\Users\\jarrodanderin\\Documents\\_NewPrograms\\CleanCitations\\AllRIS_MayIncludeDuplicates"
outFold = "C:\Users\jarrodanderin\Documents\_NewPrograms\CleanCitations\\AllRIS_Unique"
uniqueDic = {}

fiLi = glob.glob(inFold+"\\*")
for fi in fiLi:
    fiName = fi.split("\\")[-1]
    fiIn = open(fi)
    fiObj = fiIn.read()
    fiIn.close()
    uniqueDic[fiObj]=fiName

for x in uniqueDic:
    fout = open(outFold+"\\"+str(uniqueDic[x]),"w")
    fout.write(str(x))
    fout.close()
