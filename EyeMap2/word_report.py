import pandas as pd
import sys
import regex
import math

HEADINGS = ['Expt', 'Trial', 'Word']
WordNum_E = 1


def prepWordData(varList, AOIData, fixData, saccData, basicInfo):
    # columns = []

    # for i in range(len(varList)):
    #    if varList[i].get('level') in HEADINGS:
    #        columns.append(varList[i].get('name'))

    exp = {}
    exp.update(exptLevel(basicInfo))
    print("START Word Report")
    masterResult = 0
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
        wordTemp = wordLevel(AOIData[i], fixData[int(i)], saccData[int(i)], i, exp, trialVars, basicInfo)
        if int(i) == 0:
            masterResult = pd.DataFrame(wordTemp)
        else:
            df = pd.DataFrame(wordTemp)
        if int(i) > 0:
            frames = [masterResult, df]
            result = pd.concat(frames)
            masterResult = result

    masterResult.fillna("", inplace=True)
    print("END Word Report")
    return masterResult


def exptLevel(basicInfo):
    return {'EXP': basicInfo['name'], 'Subject': basicInfo['partId'], 'Eye': basicInfo['eye']}


def trialLevel(data, fixData, trialNum, eye):
    tempData = {'TrialNum': int(trialNum) + 1}
    LineCount_T = 0
    WordCount_T = 0
    SentenceCount_T = 0

    for i in data:
        if data[i].get('row') > LineCount_T:
            LineCount_T = data[i].get('row')
        if data[i].get('wordNum') > WordCount_T:
            WordCount_T = data[i].get('wordNum')
        tempWord = data[i].get('text')
        if checkSentenceEnd(tempWord):
            SentenceCount_T += 1

    startTime = sys.maxsize
    endTime = 0
    for i in range(len(fixData)):
        if fixData[i] != "":
            if fixData[i].get('eye') == eye:
                if int(fixData[i].get('st')) < startTime:
                    startTime = int(fixData[i].get('st'))
                if int(fixData[i].get('et')) > endTime:
                    endTime = int(fixData[i].get('et'))

    TrialDur = endTime - startTime
    tempData['SentenceCount_T'] = SentenceCount_T
    tempData['LineCount_T'] = LineCount_T
    tempData['WordCount_T'] = WordCount_T
    tempData['TrialDur'] = TrialDur
    return tempData


def wordLevel(data, fixData, saccData, trialNum, expVars, trialVars, basicInfo):
    LineCount_T = data.get(str(len(data) - 1)).get('row')
    lineWordCounts = []
    for i in range(LineCount_T):
        lineWordCounts.append(0)
    for i in data:
        lineWordCounts[data[i].get('row') - 1] += 1
    varResults = []
    wordInfo = {}
    WordNum_S = 1
    SentenceNum_T = 1
    sentenceCounts = getSentenceCounts(data)
    senX = 0
    downSen = sentenceCounts[senX]
    level = basicInfo['aoiType']
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
        wordInfo['TrialNum'] = int(trialNum) + 1
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
            if senX < len(sentenceCounts) - 1:
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

        if len(tempText) > 0:
            if checkSentenceEnd(tempText):
                WordNum_S = 1
                SentenceNum_T += 1
        wordInfo['WordLocX'] = data[i].get('x')
        wordInfo['WordLocY'] = data[i].get('y')
        tempResults = []
        gazeAndFixationLevel = checkFixated(data[i], fixData, saccData, data, basicInfo)
        tempDict = {**wordInfo, **gazeAndFixationLevel[0]}
        tempResults.append(expVars)
        tempResults.append(trialVars)
        tempResults.append(tempDict)
        for j in range(len(gazeAndFixationLevel[1])):
            tempResults.append(gazeAndFixationLevel[1][j])
        for j in range(len(gazeAndFixationLevel[2])):
            tempResults.append(gazeAndFixationLevel[2][j])
        results = {}
        for j in tempResults:
            results.update(j)
        varResults.append(results)
        wordInfo = {}

    return varResults


def checkSentenceEnd(word):
    ENDINGS = ['.', '!', '?', '。', '！', '？']
    QUOTES = ['＂', '"']
    isEnd = False
    if word[len(word) - 1] in ENDINGS:
        isEnd = True
    elif word[len(word) - 1] in QUOTES:
        if word[len(word) - 2] in ENDINGS:
            isEnd = True

    return isEnd


def getSentenceCounts(data):
    counts = []
    tempCount = 0
    for i in data:
        tempText = data[i].get('text')
        tempCount += 1
        if checkSentenceEnd(tempText):
            counts.append(tempCount)
            tempCount = 0
        elif int(i) == len(data)-1:
            counts.append(tempCount)
    return counts


def checkFixated(word, fixData, saccData, AOIData, basicInfo):
    gazeVars = []
    fixVars = []
    left = int(word.get('left'))
    top = int(word.get('top'))
    right = int(word.get('right'))
    bottom = int(word.get('bottom'))
    eye = basicInfo['eye']
    numAllowedGaze = basicInfo['numAllowedGaze']
    numAllowedFix = basicInfo['numAllowedFix']

    # Word Level Variables

    # Gaze Level Variables
    # Fixation Level Variables
    Blink = 0
    LaunchDistBegDec = 0
    NxtWordFix = 0

    # Saccade Level Variables
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
    # {'eye', 'st', 'et', 'dur', 'x', 'y', 'pupil', 'raw', 'id', 'blink', 'trial'}
    for i in range(len(fixData)):
        if fixData[i] != "":
            if fixData[i].get('eye') == eye:
                currentFix = fixData[i]
                if i > 2:
                    tFixid = int(currentFix.get('id')) - 2
                    for f in fixData:
                        if f != "":
                            if int(f.get('id')) == tFixid:
                                oldFix = f
                else:
                    oldFix = currentFix
                if i < len(fixData) - 2:
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
                        saccIn = getSaccade(currentFix, saccData)
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
                        saccOut = getSaccade(nextFix, saccData)
                        NxtWord_G = getWordUnits(nextFix, word, AOIData)[0]
                        if not(str(oldFix.get('blink')) == 'nan' or oldFix.get('blink') is None):
                            Blink = -1
                        if not(str(nextFix.get('blink')) == 'nan' or nextFix.get('blink') is None):
                            Blink = 1
                        if not(str(nextFix.get('blink')) == 'nan' or nextFix.get('blink') is None) and not(str(oldFix.get('blink')) == 'nan' or oldFix.get('blink') is None):
                            Blink = 0
                        LaunchDistBeg = left - float(oldFix.get('x'))
                        LineSwitch = word.get('row') - PrevWord_G
                        if str(tempWord['GazeCount_W']) <= numAllowedGaze and str(FixCount_G) <= numAllowedFix:
                            Fixheadings = "_G" + str(tempWord['GazeCount_W']) + "F" + str(FixCount_G)
                            tempFixation['fixID' + Fixheadings] = fixID
                            tempFixation['isFixation_Blink' + Fixheadings] = 0 if str(currentFix.get('blink')) == 'nan' or currentFix.get('blink') is None else 1
                            # tempFixation['Blink' + Fixheadings] = Blink
                            tempFixation['FixDur' + Fixheadings] = fixDur
                            tempFixation['LandPos' + Fixheadings] = LaunchDist[0]
                            tempFixation['LandPosDec' + Fixheadings] = LaunchDist[1]
                            tempFixation['LaunchDistBeg' + Fixheadings] = math.floor(LaunchDistBeg)
                            tempFixation['LaunchDistBegDec' + Fixheadings] = round(LaunchDistBegDec, 1)
                            tempFixation['LineSwitch' + Fixheadings] = LineSwitch
                            tempFixation['NxtWordFix' + Fixheadings] = NxtWordFix
                            fixVars.append(tempFixation)
                else:
                    if isGaze:
                        isGaze = False
                        isFirstGaze = False
                        if str(tempWord['GazeCount_W']) <= numAllowedGaze:
                            headings = "_G" + str(tempWord['GazeCount_W'])
                            RefixDur = GazeDur - firstFixDur
                            tempGaze['GazeDur' + headings] = GazeDur
                            tempGaze['GazeDur_sac' + headings] = GazeDur_sac
                            tempGaze['FixCount_G' + headings] = FixCount_G
                            tempGaze['GazePupil' + headings] = GazePupil / FixCount_G
                            tempGaze['GazeBlinkDur' + headings] = GazeBlinkDur
                            tempGaze['BlinkCount_G' + headings] = BlinkCount_G
                            tempGaze['RefixDur' + headings] = RefixDur
                            tempGaze['Refixated' + headings] = Refixated
                            tempGaze['RefixCount_G' + headings] = RefixCount_G
                            tempGaze['SacInAmp_G' + headings] = saccIn.get('ampl')
                            tempGaze['SacOutAmp_G' + headings] = saccOut.get('ampl')
                            # tempGaze['NxtWord_G' + headings] = NxtWord_G
                            # tempGaze['PrevWord_G' + headings] = PrevWord_G
                            tempGaze['LaunchDistBeg_G' + headings] = LaunchDist[0]
                            tempGaze['LaunchDistBegDec_G' + headings] = LaunchDist[1]
                            tempGaze['ReReading_G' + headings] = ReReading_G
                            gazeVars.append(tempGaze)
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
                if isGaze and i == len(fixData) - 1:
                    if str(tempWord['GazeCount_W']) <= numAllowedGaze:
                        headings = "_G" + str(tempWord['GazeCount_W'])
                        RefixDur = GazeDur - firstFixDur
                        tempGaze['GazeDur' + headings] = GazeDur
                        tempGaze['GazeDur_sac' + headings] = GazeDur_sac
                        tempGaze['FixCount_G' + headings] = FixCount_G
                        tempGaze['GazePupil' + headings] = GazePupil / FixCount_G
                        tempGaze['GazeBlinkDur' + headings] = GazeBlinkDur
                        tempGaze['BlinkCount_G' + headings] = BlinkCount_G
                        tempGaze['RefixDur' + headings] = RefixDur
                        tempGaze['Refixated' + headings] = Refixated
                        tempGaze['RefixCount_G' + headings] = RefixCount_G
                        tempGaze['SacInAmp_G' + headings] = saccIn.get('ampl')
                        tempGaze['SacOutAmp_G' + headings] = saccOut.get('ampl')
                        # tempGaze['NxtWord_G' + headings] = NxtWord_G
                        # tempGaze['PrevWord_G' + headings] = PrevWord_G
                        tempGaze['LaunchDistBeg_G' + headings] = LaunchDist[0]
                        tempGaze['LaunchDistBegDec_G' + headings] = LaunchDist[1]
                        tempGaze['ReReading_G' + headings] = ReReading_G
                        gazeVars.append(tempGaze)

    tempData = [tempWord, gazeVars, fixVars]
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

        return [tempWord.get('wordNum') - currentWord.get('wordNum'), tempWord.get('row')]
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
            'Refixated': 0, 'RefixCount_G': 0, 'RefixDur': 0, 'SacInAmp_G': 0, 'SacOutAmp_G': 0, 'NxtWord_G': 0,
            'PrevWord_G': 0, 'LaunchDistBeg_G': 0, 'LaunchDistBegDec_G': 0, 'SacInProg_G': 0, 'SacOutProg_G': 0,
            'ReReading_G': 0}


def generateFixDict():
    return {'Blink': 0, 'FixDur': 0, 'LandPos': 0, 'LandPosDec': 0, 'LaunchDistBeg': 0, 'LaunchDistBegDec': 0,
            'LineSwitch': 0, 'NxtWordFix': 0}
