import pandas as pd
import sys
import regex
import math

HEADINGS = ['Expt', 'Trial', 'Word']
WordNum_E = 1


def prep_report(varList, AOIData, fixData, saccData, basicInfo):
    """

    @param varList: The variables to be used in the report
    @param AOIData: The Area of interest Data for all trials
    @param fixData: The fixation data for all trials
    @param saccData: The saccades data for all trials
    @param basicInfo: The Basic Information about the experiment.
    @return: The word report as a Pandas Dataframe
    """
    # columns = []

    # for i in range(len(varList)):
    #    if varList[i].get('level') in HEADINGS:
    #        columns.append(varList[i].get('name'))

    exp = {'EXP': basicInfo['name'], 'Subject': basicInfo['partId'], 'Eye': basicInfo['eye']}

    masterResult = 0
    for i in AOIData:
        trialVars = trialLevel(AOIData[i], fixData[int(i)], i, basicInfo['eye'])
        words = wordVars(AOIData[i], i, basicInfo)
        for word in words:




        if int(i) == 0:
            masterResult = pd.DataFrame(wordTemp)
        else:
            df = pd.DataFrame(wordTemp)
        if int(i) > 0:
            frames = [masterResult, df]
            result = pd.concat(frames)
            masterResult = result

    masterResult.fillna("", inplace=True)
    return masterResult


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


def wordVars(data, basicInfo):
    global WordNum_E
    LineCount_T = data.get(str(len(data) - 1)).get('row')
    lineWordCounts = []
    for i in range(LineCount_T):
        lineWordCounts.append(0)
    for i in data:
        lineWordCounts[data[i].get('row') - 1] += 1
    varResults = []
    # left, top, right, bottom, text, x, y, row, col, wordNum
    wordInfo = {}
    WordCount_S = 1
    WordNum_S = 1
    SentenceNum_T = 1
    level = basicInfo['aoiType']
    tempWords = {}
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
        wordInfo['WordCount_S'] = WordCount_S
        WordCount_S += 1
        wordInfo['WordNum_E'] = WordNum_E
        WordNum_E += 1
        wordInfo['WordNum_T'] = data[i].get('wordNum')
        wordInfo['WordNum_L'] = data[i].get('col')
        wordInfo['WordNum_S'] = WordNum_S
        WordNum_S += 1
        wordInfo['SentenceNum_T'] = SentenceNum_T

        if len(tempText) > 0:
            if checkSentenceEnd(tempText):
                WordCount_S = 1
                WordNum_S = 1
                SentenceNum_T += 1
        wordInfo['WordLocX'] = data[i].get('x')
        wordInfo['WordLocY'] = data[i].get('y')
        tempWords[data[i].get('text')] = wordInfo.copy()

    return tempWords
