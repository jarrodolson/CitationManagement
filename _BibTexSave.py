##Program for converting RIS files into BibTex database
import re
import glob

def readInData(fiName):
    fi = open(str(fiName))
    fiObj = fi.read()
    fi.close()    
    return fiObj

def readInCrossRef():
    refDic = {}
    fi = open("KeyForCrossRef.txt")
    fiObj = fi.read()
    fi.close()
    for row in fiObj.split("\n"):
        keyName = row.split(" = ")
        key = keyName[0]
        if keyName[1]!="[special case]":
            keyRef = keyName[1].split(",")
            refDic[key]=keyRef
    return refDic
            

def turnToDic(fiObj):
    reType = re.compile("..  - .*")
    dataLi = reType.findall(fiObj)
    fiDic = {}
    for data in dataLi:
        rowLi = data.split("  - ")
        try:
            exists = fiDic[rowLi[0]]
            exists = exists+" and "+str(rowLi[1])
            fiDic[rowLi[0]] = exists
        except KeyError:
            fiDic[rowLi[0]] = str(rowLi[1])
    return fiDic

def makeArticleDic2(fiDic,elements,crossRefDic):
    newDic = {}
    for el in elements:
        if el == "pages":
            newDic["pages"] = handlePages(fiDic)
        if el == "publisher":
            newDic["publisher"] = handlePublisher(fiDic)
        try:
            cross = crossRefDic[el]
            countTries = 1
            for item in cross:
                try:
                    if el!="year":
                        newDic[el] = fiDic[item]
                        break
                    if el == "year":
                        year,month=yearSplit(fiDic[item])
                        newDic["month"]=month
                        newDic["year"]=year
                except KeyError:
                    if countTries==len(cross) and el=="address":
                        print el
                countTries+=1
        except KeyError:
            if el == "note":
                newDic["note"]="NA"
    return newDic

def handlePublisher(fiDic):
    try:
        pub = fiDic["PB"]
    except KeyError:
        print "No publisher"
        pub = "NA"
    try:
        loc = fiDic["CY"]
    except KeyError:
        print "No location"
        loc = "NA"
    output = str(loc)+": "+str(pub)
    return output

def handlePages(fiDic):
    try:
        sp = fiDic["SP"]
        try:
            ep = fiDic["EP"]
            pages = str(sp)+"-"+str(ep)
        except KeyError:
            pgs = sp.split("-")
            if len(pgs)>1:
                pages = sp
            if len(pgs)==1:
                pages = sp
    except KeyError:
        pages = "NA"
    return pages

def yearSplit(YEAR):
    yearLi = YEAR.split("/")
    year = yearLi[0]
    try:
        month = yearLi[1]
    except IndexError:
        month="NA"
    return year,month

def writeArticleEntry(fout,ty,elements,articleDic,keyDic,countErrors):
    ifError = 0
    try:
        author = articleDic["author"]
        authorLast = author.split(",")[0]
        if len(authorLast)>10:
            authorLast = authorLast[0:10]
    except KeyError:
        authorLast = "NA"
    try:
        year = articleDic["year"]
    except KeyError:
        year = "NA"
    key = str(authorLast)+str(year)
    key = key.replace(" ","").replace(".","")
    countKeys = 2
    keepOn = True
    while keepOn == True:
        try:
            exists = keyDic[key]
            print "Duplicate!!"
            key = key+str(countKeys)
        except KeyError:
            keepOn = False
        countKeys = int(countKeys)+1
    fout.write(str(ty)+"{"+str(key)+",\n")
    for el in elements:
        try:
            data = articleDic[el]
            writeOrNo = True
            if data=="NA":
                writeOrNo = False
            if el=="year" or el=="author" or el=="title" or el=="journal":
                writeOrNo = True
            if writeOrNo==True:
                output = data
                if el == "author":
                    output = output.replace(";", " and")
                fout.write("\t"+str(el)+" = {"+str(output)+"},\n")
        except KeyError:
            ifError+=1
            ##print "Error",el
            ##print articleDic
    fout.write("}\n\n")
    if ifError>0:
        countErrors+=1
    return keyDic,countErrors
 
########################################################################
direct = str(raw_input("What is the path you want to use? "))    

elements_article = ["author","title","journal","volume","number",
                    "pages","year","month","note"]
elements_book = ["author","title","publisher","volume","number","series",
                 "address","edition","year","month","note"]
elements_conference = ["author","title",'booktitle','editor','volume','number',
                       'series','pages','address','year','month','publisher',
                       'note']
elements_manual = ['title','author','organization','address','edition','month',
                   'year','note']
elements_mastersthesis = ['author','title','school','year','type','address',
                          'month','note']
elements_misc = ['author','title','howpublished','month','year','note']
elements_proceedings = ['title','year','editor','volume/number','series','address',
                        'month','organization','publisher','note']
elements_techReport = ['author','title','institution','year','type','number',
                       'address','month','note']
elements_unpublished = ['author','title','note','month','year']

countErrors = 0
fout = open("tempOut.txt","w")
crossRefDic = readInCrossRef()
keyDic = {}
fiGlob = glob.glob(direct+"\\*")
for fiName in fiGlob:
    fiObj = readInData(fiName)
    fiDic = turnToDic(fiObj)

    try:
        ty = fiDic["TY"]
    except KeyError:
        ty = "JOUR"
    if ty == "JOUR":
        articleDic = makeArticleDic2(fiDic,elements_article,crossRefDic)
        keyDic,countErrors = writeArticleEntry(fout,"@article",elements_article,articleDic,keyDic,countErrors)
    if ty == "BOOK":
        bookDic = makeArticleDic2(fiDic,elements_book,crossRefDic)
        keyDic,countErrors = writeArticleEntry(fout,"@book",elements_book,bookDic,keyDic,countErrors)
print "Number of errors is: ",countErrors
fout.close()
