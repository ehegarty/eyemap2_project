import pandas as pd
import sys
import regex
import math
from .word_report import trialLevel, checkSentenceEnd, getSentenceCounts

HEADINGS = ['Expt', 'Trial', 'Word']


def fixation_report(varList, AOIData, fixData, saccData, basicInfo):
    exp = {'EXP': basicInfo['name'], 'Subject': basicInfo['partId'], 'Eye': basicInfo['eye']}
    masterResult = 0
    print("STARTING Fixation Report")
    worNum_E = 0
    for x in AOIData:
        for y in AOIData[x]:
            print(AOIData[x][y])
            worNum_E += 1
    basicInfo['WordCount_E'] = worNum_E
    basicInfo['WordNum_E'] = 0
    for i in AOIData:
        print("Trial: " + str(i))
        trialVars = trialLevel(AOIData[i], fixData[int(i)], i, basicInfo['eye'])
        words = wordVars(AOIData[i], basicInfo)
        gazeandfixations = []
        for j in AOIData[i]:
            gazeandfixations.append(checkFixated(AOIData[i][j], fixData[int(i)], saccData[int(i)], AOIData[i], basicInfo))
        arrangedData = arrangeData(words, gazeandfixations, fixData[int(i)], exp, trialVars)
        if int(i) == 0:
            masterResult = pd.DataFrame(arrangedData)
        else:
            df = pd.DataFrame(arrangedData)
        if int(i) > 0:
            frames = [masterResult, df]
            result = pd.concat(frames)
            masterResult = result

    masterResult.fillna("", inplace=True)
    print("END Fixation Report")
    return masterResult


def arrangeData(words, data, fixations, exp, trialVars):
    results = []
    for fix in fixations:
        if fix != "":
            if fix['eye'] == exp['Eye']:
                curFix = fix['id']
                isFixFound = False
                fixLoc = []
                GF = ""
                for info in data:
                    if len(info[2]) > 0:
                        for i in info[2]:
                            if curFix == i['fixID']:
                                isFixFound = True
                                fixLoc = info
                                GF = i['GF']
                tempInfo = []
                fixInfo = {}
                tempInfo.append(exp)
                tempInfo.append(trialVars)
                if isFixFound:
                    for w in words:
                        if w['WordNum_T'] == fixLoc[0]:
                            tempInfo.append(w)
                    gNum = GF[GF.index('G') + 1:GF.index('F')]
                    for g in fixLoc[1]:
                        if g['Gaze_Num'] == gNum:
                            tempInfo.append(g)
                            break
                    for f in fixLoc[2]:
                        if f['GF'] == GF:
                            temp = {}
                            temp['FixLocX'] = fix['x']
                            temp['FixLocY'] = fix['y']
                            tempInfo.append(f)
                            tempInfo.append(temp)
                            break
                else:
                    tempInfo.append({'fixID': curFix})
                for ti in tempInfo:
                    fixInfo.update(ti)
                results.append(fixInfo.copy())
    return results


def wordVars(data, basicInfo):
    LineCount_T = data.get(str(len(data) - 1)).get('row')
    lineWordCounts = []
    for i in range(LineCount_T):
        lineWordCounts.append(0)
    for i in data:
        lineWordCounts[data[i].get('row') - 1] += 1
    varResults = []
    sentenceCounts = getSentenceCounts(data)
    wordInfo = {}
    WordCount_S = 1
    WordNum_S = 1
    SentenceNum_T = 1
    senX = 0
    downSen = sentenceCounts[senX]
    level = basicInfo['aoiType']
    tempWords = []
    for i in data:
        tempText = data[i].get('text')
        if level == "word":
            if tempText[0] == ' ':
                tempText = tempText[1:]
            else:
                tempText = tempText
            # Word = regex.sub('[\p{P}\p{Sm}]+', '', tempText)
            Word = tempText
        else:
            Word = tempText
        wordInfo['Word'] = regex.sub('[\p{P}\p{Sm}]+', '', Word)
        wordInfo['Word_punct'] = Word
        wordInfo['WordLen'] = len(regex.sub('[\p{P}\p{Sm}]+', '', Word))
        wordInfo['WordLen_punct'] = len(Word)
        wordInfo['LineNum_T'] = data[i].get('row')
        wordInfo['WordCount_T'] = data.get(str(len(data) - 1)).get('wordNum')
        wordInfo['WordCount_L'] = lineWordCounts[int(data[i].get('row')) - 1]
        wordInfo['WordCount_S'] = sentenceCounts[senX]
        downSen -= 1
        if downSen == 0:
            if senX < len(sentenceCounts)-1:
                senX += 1
            downSen = sentenceCounts[senX]
        wordInfo['WordCount_E'] = basicInfo['WordCount_E']
        basicInfo['WordNum_E'] += 1
        wordInfo['WordNum_E'] = basicInfo['WordNum_E']
        wordInfo['WordNum_T'] = data[i].get('wordNum')
        wordInfo['WordNum_L'] = data[i].get('col')
        wordInfo['WordNum_S'] = WordNum_S
        WordNum_S += 1
        wordInfo['SentenceNum_T'] = SentenceNum_T
        wordInfo['AOI_Left'] = data[i].get('left')
        wordInfo['AOI_Right'] = data[i].get('right')
        wordInfo['AOI_Top'] = data[i].get('top')
        wordInfo['AOI_Bottom'] = data[i].get('bottom')

        if len(tempText) > 0:
            if checkSentenceEnd(tempText):
                WordNum_S = 1
                SentenceNum_T += 1
        wordInfo['WordLocX'] = data[i].get('x')
        wordInfo['WordLocY'] = data[i].get('y')
        tempWords.append(wordInfo.copy())

    return tempWords


def checkFixated(word, fixData, saccData, AOIData, basicInfo):
    gazeVars = []
    fixVars = []
    left = int(word.get('left'))
    top = int(word.get('top'))
    right = int(word.get('right'))
    bottom = int(word.get('bottom'))
    eye = basicInfo['eye']

    Blink = 0
    LaunchDistBegDec = 0
    NxtWordFix = 0

    SacInAmpX = 0
    SacInAmpY = 0

    tempWord = generateWordDict()
    isGaze = False
    isFirstGaze = False
    firstGazeDur = 0
    GazeDur = 0
    GazeDur_sac = 0
    FixCount_G = 0
    GazeBlinkDur = 0
    GazePupil = 0
    BlinkCount_G = 0
    firstFixDur = 0
    Refixated = 0
    RefixCount_G = 0
    NxtWord_G = 0
    PrevWord_G = 0
    checkedFixes = []
    ReReading_G = 0
    ReReadDur = 0
    TVDur = 0
    FixNum_S = 0
    for i in range(len(fixData)):
        if fixData[i] != "":
            if fixData[i].get('eye') == eye:
                currentFix = fixData[i]
                base = 0
                if eye == 'R':
                    base = 2
                else:
                    base = 3
                if int(currentFix.get('id')) >= base:
                    tFixid = int(currentFix.get('id')) - 2
                    for f in fixData:
                        if f != "":
                            if int(f.get('id')) == tFixid:
                                oldFix = f
                else:
                    oldFix = currentFix
                if int(currentFix.get('id')) <= len(fixData) - 2:
                    tFixid = int(currentFix.get('id')) + 2
                    for f in fixData:
                        if f != "":
                            if int(f.get('id')) == tFixid:
                                nextFix = f
                else:
                    nextFix = currentFix
                fixX = float(currentFix.get('x'))
                fixY = float(currentFix.get('y'))
                isFixated = ((left <= fixX <= right) and (top <= fixY <= bottom))
                tempGaze = {}
                tempFixation = {}
                if isFixated:
                    tempWord['Fixated'] = 1
                    tempWord['FixCount_W'] += 1
                    fixDur = int(currentFix.get('dur'))
                    fixID = currentFix.get('id')
                    if not isGaze:
                        checkedFixes.append(currentFix)
                        tempWord['GazeCount_W'] += 1
                        firstFixDur += fixDur
                        isGaze = True
                        if not isFirstGaze:
                            isFirstGaze = True
                            tempWord['FixStartTime_W'] = int(currentFix.get('st'))
                    if isGaze:
                        tempWord['TVDur'] += fixDur
                        TVDur += fixDur
                        if not(str(currentFix.get('blink')) == 'nan' or currentFix.get('blink') is None):
                            tempWord['BlinkCount_W'] += 1
                            tempWord['BlinkDur_W'] += fixDur
                            GazeBlinkDur += fixDur
                            BlinkCount_G += 1
                        FixCount_G += 1
                        if FixCount_G > 1:
                            Refixated = 1
                            RefixCount_G += 1
                        ReReading_G = checkReRead(currentFix, checkedFixes)
                        saccIn = getSaccade(oldFix, saccData)
                        PrevWord_G = (getWordUnits(oldFix, word, AOIData))[1]
                        LaunchDist = getLandPos(word, currentFix)
                        GazePupil += int(currentFix.get('pupil'))
                        GazeDur += fixDur
                        saccDur = getSaccade(currentFix, saccData)
                        GazeDur_sac += (fixDur + int(saccDur.get('dur')))
                        if tempWord['GazeCount_W'] == 1:
                            firstGazeDur += fixDur
                        else:
                            ReReadDur = TVDur - firstGazeDur
                        tempWord['ReReadDur'] = ReReadDur
                        tempWord['FixEndTime_W'] = int(currentFix.get('et'))
                        saccOut = getSaccade(currentFix, saccData)
                        NxtWord_G = getWordUnits(nextFix, word, AOIData)[1]
                        if not (str(oldFix.get('blink')) == 'nan' or oldFix.get('blink') is None):
                            Blink = -1
                        if not (str(nextFix.get('blink')) == 'nan' or nextFix.get('blink') is None):
                            Blink = 1
                        if (str(nextFix.get('blink')) == 'nan' or nextFix.get('blink') is None) and (
                                str(oldFix.get('blink')) == 'nan' or oldFix.get('blink') is None):
                            Blink = 0
                        LaunchDistBeg = left - float(oldFix.get('x'))
                        LineSwitch = int(word.get('row')) - int(PrevWord_G)
                        Fixheadings = "_G" + str(tempWord['GazeCount_W']) + "F" + str(FixCount_G)
                        tempFixation['fixID'] = fixID
                        tempFixation['GF'] = Fixheadings[1:]
                        tempFixation['FixNum_G'] = FixCount_G
                        tempFixation['isFixation_Blink'] = 0 if str(currentFix.get('blink')) == 'nan' or currentFix.get('blink') is None else 1
                        # tempFixation['Blink'] = Blink
                        tempFixation['FixDur'] = fixDur
                        tempFixation['FixNum_T'] = (int(fixID) / 2) if int(fixID) % 2 == 0 else ((int(fixID) / 2) + 1)
                        tempFixation['FixDur'] = fixDur
                        tempFixation['Pupil'] = currentFix.get('pupil')
                        tempFixation['LandPos'] = LaunchDist[0]
                        tempFixation['LandPosDec'] = LaunchDist[1]
                        tempFixation['LaunchDistBeg'] = math.floor(LaunchDistBeg)
                        tempFixation['LaunchDistBegDec'] = round(LaunchDistBegDec, 1)
                        tempFixation['LineSwitch'] = LineSwitch
                        tempFixation['NxtWordFix'] = getWordUnits(nextFix, word, AOIData)[0]
                        if int(currentFix.get('id')) >= base:
                            tempFixation['PreFixDur'] = oldFix.get('dur')
                            SacInAmpX = 0
                            SacInAmpY = 0
                            tempFixation['SacInAmp'] = saccIn.get('ampl')
                            if float(saccIn.get('dur')) != 0 and (saccIn.get('tx') != '.' or saccIn.get('ty') != '.'):
                                SacInAmpX = (float(saccIn.get('tx')) - float(saccIn.get('x'))) / float(saccIn.get('dur'))
                                SacInAmpY = (float(saccIn.get('ty')) - float(saccIn.get('y'))) / float(saccIn.get('dur'))
                            tempFixation['SacInAmpX'] = SacInAmpX
                            tempFixation['SacInAmpY'] = SacInAmpY
                            if saccIn.get('tx') != '.':
                                tempFixation['SacInX'] = saccIn.get('x')
                                tempFixation['SacInTX'] = saccIn.get('tx')
                                tempFixation['SacInY'] = saccIn.get('y')
                                tempFixation['SacInTY'] = saccIn.get('ty')
                                tempFixation['SacInDur'] = saccIn.get('dur')
                                tempFixation['SacInProg'] = 1 if float(saccIn.get('tx')) > float(saccIn.get('x')) else 0
                        SacOutAmpX = 0
                        SacOutAmpY = 0
                        tempFixation['SacOutAmp'] = saccOut.get('ampl')
                        if float(saccOut.get('dur')) != 0 and (saccOut.get('tx') != '.' or saccOut.get('ty') != '.'):
                            SacOutAmpX = (float(saccOut.get('tx')) - float(saccOut.get('x'))) / float(saccOut.get('dur'))
                            SacOutAmpY = (float(saccOut.get('tx')) - float(saccOut.get('x'))) / float(saccOut.get('dur'))
                        tempFixation['SacOutAmpX'] = SacOutAmpX
                        tempFixation['SacOutAmpY'] = SacOutAmpY
                        if saccOut.get('tx') != '.':
                            tempFixation['SacOutX'] = saccOut.get('x')
                            tempFixation['SacOutTX'] = saccOut.get('tx')
                            tempFixation['SacOutY'] = saccOut.get('y')
                            tempFixation['SacOutTY'] = saccOut.get('ty')
                            tempFixation['SacOutDur'] = saccOut.get('dur')
                            tempFixation['SacOutProg'] = 1 if float(saccOut.get('tx')) > float(saccOut.get('x')) else 0
                        fixVars.append(tempFixation.copy())
                else:
                    if isGaze:
                        isGaze = False
                        isFirstGaze = False
                        headings = "_G" + str(tempWord['GazeCount_W'])
                        RefixDur = GazeDur - firstFixDur
                        tempGaze['Gaze_Num'] = headings[2:]
                        tempGaze['GazeDur'] = GazeDur
                        tempGaze['GazeDur_sac'] = GazeDur_sac
                        tempGaze['FixCount_G'] = FixCount_G
                        tempGaze['GazePupil'] = GazePupil / FixCount_G
                        tempGaze['GazeBlinkDur'] = GazeBlinkDur
                        # tempGaze['BlinkCount_G'] = BlinkCount_G
                        tempGaze['RefixDur'] = RefixDur
                        tempGaze['Refixated'] = Refixated
                        tempGaze['RefixCount'] = RefixCount_G
                        # tempGaze['NxtWord_G'] = NxtWord_G
                        # tempGaze['PrevWord_G'] = PrevWord_G
                        tempGaze['LaunchDistBeg_G'] = LaunchDist[0]
                        tempGaze['LaunchDistBegDec_G'] = LaunchDist[1]
                        tempGaze['ReReading'] = ReReading_G
                        gazeVars.append(tempGaze.copy())
                    FixCount_G = 0
                    GazeDur = 0
                    GazeDur_sac = 0
                    BlinkCount_G = 0
                    GazePupil = 0
                    GazeBlinkDur = 0
                    firstFixDur = 0
                    Refixated = 0
                    RefixCount_G = 0
                    NxtWord_G = 0
                    PrevWord_G = 0
                    Blink = 0
                if isGaze and i == len(fixData) - 1:
                    headings = "_G" + str(tempWord['GazeCount_W'])
                    RefixDur = GazeDur - firstFixDur
                    tempGaze['Gaze_Num'] = headings[2:]
                    tempGaze['GazeDur'] = GazeDur
                    tempGaze['GazeDur_sac'] = GazeDur_sac
                    tempGaze['FixCount_G'] = FixCount_G
                    tempGaze['GazePupil'] = GazePupil / FixCount_G
                    tempGaze['GazeBlinkDur'] = GazeBlinkDur
                    tempGaze['BlinkCount_G'] = BlinkCount_G
                    tempGaze['RefixDur'] = RefixDur
                    tempGaze['Refixated'] = Refixated
                    tempGaze['RefixCount'] = RefixCount_G
                    # tempGaze['NxtWord_G'] = NxtWord_G
                    # tempGaze['PrevWord_G'] = PrevWord_G
                    tempGaze['LaunchDistBeg_G'] = LaunchDist[0]
                    tempGaze['LaunchDistBegDec_G'] = LaunchDist[1]
                    tempGaze['ReReading_G'] = ReReading_G
                    gazeVars.append(tempGaze.copy())

    tempData = [word['wordNum'], gazeVars.copy(), fixVars.copy()]
    return tempData


def getSaccade(fix, saccData):
    tempSaccade = {'eye': 'R', 'st': '0', 'et': '0', 'dur': '0', 'x': '0', 'y': '0',
                   'tx': '0', 'ty': '0', 'ampl': '0', 'pv': '0', 'id': '0', 'trial': 0}
    if fix != "":
        fixId = fix.get('id')
        for i in range(len(saccData)):
            if fixId == saccData[i].get('id'):
                tempSaccade = saccData[i]
    return tempSaccade


def getLandPos(wordInfo, fix):
    if fix != "":
        letterSizes = wordInfo.get('letterSizes')
        fixX = float(fix.get('x'))
        letterUnits = 0
        xWidth = float(wordInfo.get('x'))
        xStart = 0
        xEnd = 0
        isPast = False
        lastWidth = 0
        for i in range(len(letterSizes)):
            if math.floor(fixX) >= math.floor(xWidth):
                xStart = xWidth
                letterUnits += 1
            else:
                if not isPast:
                    isPast = True
                    xEnd = xWidth
            xWidth += letterSizes[i]
            lastWidth = letterSizes[i]

        fixX -= xStart
        xEnd -= xStart
        if wordInfo.get('text')[0] == ' ':
            letterUnits -= 1
        res = ((fixX / lastWidth) * 100) / 100
        letterUnitsDec = round(letterUnits + res - 1, 1)
        return [letterUnits, letterUnitsDec]
    return [-10, -10]


def getWordUnits(fix, currentWord, AOIData):
    if fix != "":
        fixX = float(fix.get('x'))
        fixY = float(fix.get('y'))
        tempWord = currentWord
        for i in AOIData:
            left = int(AOIData[i].get('left'))
            top = int(AOIData[i].get('top'))
            right = int(AOIData[i].get('right'))
            bottom = int(AOIData[i].get('bottom'))
            isFixated = ((left <= fixX <= right) and (top <= fixY <= bottom))
            if isFixated:
                tempWord = AOIData[i]
                break
        return [tempWord.get('wordNum') - currentWord.get('wordNum'), tempWord.get('row'), tempWord.get('wordNum') - currentWord.get('wordNum')]
    return [-10, -10]


def checkReRead(fix, checkedFixes):
    if fix != "":
        fixX = float(fix.get('x'))
        fixY = float(fix.get('y'))
        reRead = 0
        for i in checkedFixes:
            tempX = float(i.get('x'))
            tempY = float(i.get('y'))
            if tempX > fixX or tempY > fixY:
                reRead = 1
        return reRead
    return 0


def generateWordDict():
    return {'Fixated': 0, 'FixCount_W': 0, 'GazeCount_W': 0, 'BlinkCount_W': 0, 'TVDur_sac': 0, 'TVDur': 0,
            'BlinkDur_W': 0, 'ReReadDur': 0, 'FixStartTime_W': 0, 'FixEndTime_W': 0}


def generateGazeDict():
    return {'FixCount_G': 0, 'GazeDur': 0, 'GazeBlinkDur': 0, 'GazeDur_sac': 0, 'GazePupil': 0, 'BlinkCount_G': 0,
            'Refixated': 0, 'RefixCount': 0, 'RefixDur': 0, 'SacInAmp_G': 0, 'SacOutAmp_G': 0, 'NxtWord_G': 0,
            'PrevWord_G': 0, 'LaunchDistBeg_G': 0, 'LaunchDistBegDec_G': 0, 'SacInProg_G': 0, 'SacOutProg_G': 0,
            'ReReading': 0}


def generateFixDict():
    return {'Blink': 0, 'FixDur': 0, 'LandPos': 0, 'LandPosDec': 0, 'LaunchDistBeg': 0, 'LaunchDistBegDec': 0,
            'LineSwitch': 0, 'NxtWordFix': 0}
