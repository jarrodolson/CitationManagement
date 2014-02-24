import os
import xlrd
import glob
import shutil
import re

class readAndDecide:
    def __init__(self,parent):
        masterDic = {}
        self.toUseDir = "RIS_ToUse"
        self.seriouslyToUseDir = "RIS_SeriouslyToUse"
        self.notToUseDir = "RIS_NotToUse"
        self.initialDir = "InitialHarvest"
        self.noDupDir = "NoDuplicates"
        ##self.keepDel()
        ##self.checkDup()##For when taking files from many ris cards
        self.makeOutputLi()

    def getInput(self,string,expected):
        ##Takes a string (what will be displayed to user) and an indicator for
        ## what is expected
        cont = False
        while cont==False:
            selection = raw_input(string)
            if expected == "integer":
                pass
            if expected == "li":
                pass
            if expected == "string":
                pass
            cont = True
        return selection

    def doRatings(self):
        relevance = 0
        tags = "NA"
        framework = "NA"
        discipline = "NA"
        note = "NA"
        relevance = self.getInput("How relevant is this entry to this project (1-5)\n","integer")
        tags = self.getInput("What should this be tagged (separate tags by comma)\n","li")
        framework = self.getInput("What framework was used in this article?\n","string")
        discipline = self.getInput("What discipline do the authors come from\n","string")
        thesisRole = self.getInput("Where does this fit into thesis?\n","string")
        note = self.getInput("Any notes you want to make?\n","string")
        return [relevance,tags,framework,discipline,thesisRole,note]

    def doType(self):
        ty = "Unknown"
        ty = 0
        ty = self.getInput("Is this a quant or qualitative study","string")
        rel = self.getInput("Is this a study of war onset?","string")
        return [ty,rel]

    def makeOutputLi(self):
        dic = self.readOutputLi()
        print "Length of dictionary to start with: ",len(dic)
        for fi in glob.glob(self.toUseDir+"\\*.*"):
            ##print "\n"
            authors = self.getAuthors(fi)
            title = self.getTitle(fi)
            year = self.getYr(fi)
            journalTit = self.resourceType(fi)
            metaLi = [title,authors,year,journalTit]
            try:
                values = dic[fi]
                ##print "Found"
            except KeyError:
                os.startfile(fi)
                ratingLi = self.doType()
                ##ratingLi = [0,0,0,0,0]
                writeLi = metaLi+ratingLi
                try:
                    valueLi = dic[fi]
                    print "Duplicated filename"
                except KeyError:
                    dic[fi]=writeLi
                doAnother = raw_input("\nDo you want to do another?\n")
                if str(doAnother).lower()=="no":
                    break
        raw_input("Length of dictionary after activity: "+str(len(dic))+"\nPress any button to quit")
        self.writeOutputLi(dic)

    def clean(self,string):
        string = string.replace(".","")
        string = string.lower()
        return string

    def resourceType(self,fi):
        fiObj = self.openDoc(fi)
        tyRe = re.compile("TY\s\s-\s.*")
        tyLi = tyRe.findall(fiObj)
        found = False
        countAttempt = 0
        tiLi = ["T2","SO","JF"]
        while found==False and countAttempt<len(tiLi):
            titleRE = re.compile(tiLi[countAttempt]+"\s\s-\s.*")
            titleLi = titleRE.findall(fiObj)
            if len(titleLi)>0:
                found=True
            countAttempt+=1
        if found==True:
            title = titleLi[0].replace(tiLi[countAttempt-1]+"  - ","")
            ##print title
        if found==False:
            if len(tyLi)==0 or tyLi[0]=="JOUR":
                print tyLi[0]
                print "Journal title not found:\n",fiObj
            title = ""
        title = self.clean(title)
        return title

    def openDoc(self,fi):
        fiIn = open(fi)
        fiObj = fiIn.read()
        fiIn.close()
        return fiObj

    def getYr(self,fi):
        fiObj = self.openDoc(fi)
        found = False
        countAttempt = 0
        yrLi = ["PY","Y1"]
        while found==False and countAttempt<len(yrLi):
            yrRe = re.compile(yrLi[countAttempt]+"\s\s-\s.*")
            foundYrs = yrRe.findall(fiObj)
            if len(foundYrs)>0:
                found=True
            countAttempt+=1
        if found==True:
            year = foundYrs[0].replace(yrLi[countAttempt-1]+"  - ","")
            ##print year
        if found==False:
            print "Year not found:\n",fiObj
            year = ""
        return year

    def getTitle(self,fi):
        fiObj = self.openDoc(fi)
        tiRe = re.compile("TI\s\s-\s.*")
        tiLi = tiRe.findall(fiObj)
        try:
            title = tiLi[0].replace("TI  - ","")
        except IndexError:
            tiRe = re.compile("T1\s\s-\s.*")
            tiLi = tiRe.findall(fiObj)
            try:
                title = tiLi[0].replace("T1  - ","")
            except IndexError:
                print "Title not found\n",fiObj
                title = ""
        return title

    def getAuthors(self,fi):
        fiObj = self.openDoc(fi)
        auLi = ["AU","A1","A2","A3","A4"]
        found = False
        countAu = 0
        for au in auLi:
            authRe = re.compile(au+"\s\s-\s.*")
            authLi = authRe.findall(fiObj)
            if len(authLi)>0:
                found = True
                break
            countAu += 1
        if found==False:
            print "No author found:\n",fiObj
        authStr = ""
        newAuth = 0
        for author in authLi:
            authStr+=author.replace(auLi[countAu]+"  - ","")
            if len(authLi)>1 and newAuth<len(authLi)-1:
                authStr+=", "
            newAuth+=1
        return authStr
            
    def readOutputLi(self):
        dic = {}
        try:
            intake = open("NotesForQuant.txt")
            intakeObj = intake.read()
            intake.close()
            intakeLi = intakeObj.split("\n")
            countRow = 0
            for row in intakeLi:
                if countRow>0:
                    rowLi = row.split("\t")
                    if len(rowLi[0])>3:
                        dataLi = rowLi[1:len(rowLi)]
                        if len(rowLi)>0:
                            try:
                                valueLi = dic[rowLi[0]]
                                print "Reading in error: Duplicate"
                            except KeyError:
                                dic[rowLi[0]] = dataLi
                countRow+=1
        except IOError:
            pass
        return dic

    def writeOutputLi(self,dic):
        fout = open("NotesForQuant.txt","w")
        fout.write("Filename\tTitle\tAuthors\tYear\tJournalTitle\tType\tRelevance\n")
        countEntry = 0
        for entry in dic:
            countCol = 0
            fout.write(str(entry)+"\t")
            ##print dic[entry]
            for col in dic[entry]:
                fout.write(str(col))
                if countCol!=len(dic[entry])-1:
                    fout.write("\t")
                if countCol==len(dic[entry])-1:
                    fout.write("\n")
                countCol+=1
            
            countEntry+=1
        fout.close()

    def keepDel(self):
        if os.path.isdir(self.toUseDir)==False:
            os.mkdir(self.toUseDir)
        if os.path.isdir(self.notToUseDir)==False:
            os.mkdir(self.notToUseDir)
        for fi in glob.glob(self.noDupDir+"\\*.*"):
            os.startfile(fi)
            cont = False
            while cont == False:
                keepIndic = raw_input("keep or del (or close to quit program)? ")
                if str(keepIndic).lower()=="keep" or str(keepIndic).lower()=="del" or str(keepIndic.lower())=="close":
                    cont = True
            if str(keepIndic).lower()=="close":
                   break
            if str(keepIndic).lower()=="keep":
                cont = self.moveFile(fi,self.toUseDir+"\\"+fi.split("\\")[-1])
                if cont == False:
                    break
                if cont == True:
                    os.remove(fi)
            if str(keepIndic).lower()=="del":
                cont = self.moveFile(fi,self.notToUseDir+"\\"+fi.split("\\")[-1])
                if cont == False:
                    break
                if cont==True:
                    os.remove(fi)
        raw_input("All done! Press enter to continue")

    def openFi(self,fi):
        fi = open(fi)
        fiObj = fi.read()
        fi.close()
        return fiObj

    def checkDup(self):
        masterDic = {}
        folders = os.listdir(self.initialDir)
        for folder in folders:
            for fi in glob.glob(self.initialDir+"\\"+folder+"\\*"):
                fiDic = {}
                fiObj = self.openFi(fi)
                fiObjLi = fiObj.split("\n")
                for row in fiObjLi:
                    rowLi = row.split("  - ")
                    ##print rowLi
                    try:
                        fiDic[rowLi[0]]=rowLi[1]
                    except IndexError:
                        pass
                masterDic[fi]=fiDic

        dupLi = []
        notDupDic = {}
        for dic in masterDic:##Dic is the filename
            useDic = masterDic[dic]##The actual dictionary
            notDupDic[str(useDic)]=dic

                                
        if os.path.isdir(self.noDupDir)==False:
            os.mkdir(self.noDupDir)

        for dic in notDupDic:
            fi = notDupDic[dic]            
            fiNameLi = fi.split("\\")
            fiName = self.noDupDir+"\\"+fiNameLi[1]+"_"+fiNameLi[2]
            shutil.copyfile(fi,fiName)

    def compare(self,str1,str2):
        dup = False
        if str1.lower().replace(" ","")==str2.lower().replace(" ",""):
            dup = True
        return dup

    def moveFile(self,src,dst):
        cont = False
        copied = False
        try:
            fi_2 = open(dst)
            print "ERROR... NOT COPYING... FILE ALREADY EXISTS"
        except IOError:
            shutil.copyfile(src,dst)
            copied = True
        try:
            fi = open(dst)
            fi.close()
            if copied == True:
                cont = True
        except IOError:
            print "Error copying"
        return cont

root = []
myApp = readAndDecide(root)
