import json
import pandas as pd
import xmltodict
import io
from EyeMap2.models import UserProfile, ExpVariable, Experiment, Participant, Fonts
from EyeMap2.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse, StreamingHttpResponse
from django.shortcuts import render, redirect
from .get_data import html_to_text, get_text_info
from .word_report import prepWordData
from .fixation_report import fixation_report
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404


# def upload_file(request):
#     if request.method == 'POST':
#         form = FontsForm(request.POST, request.FILES)
#         if form.is_valid():
#             # file is saved
#             form.save()
#             return HttpResponseRedirect('/success/url/')
#     else:
#         form = ModelFormWithFileField()
#     return render(request, 'upload.html', {'form': form})

def index(request):
    if request.user.is_authenticated():
        if 'exp' in request.GET:
            exp = request.GET.get('exp', None)
            request.session['sel_exp'] = exp
            fields = ('exp')
            part = request.GET.get('part', None)
            request.session['sel_part'] = part
            return HttpResponse('ok')

        elif 'deleteExp' in request.POST:
            exp_name = request.POST.get('exp_name1')

            Experiment.objects.filter(owner=UserProfile.objects.get(id=request.user.id)).get(exp_name=exp_name).delete()
            exp_list = Experiment.objects.filter(owner=UserProfile.objects.get(id=request.user.id))
            # gets all the experiments of the user
            allexp = exp_list
            context_dict = {'experiments': exp_list}
            participantNumber = []
            emptyExp = []

            # loops through experiment list and gets all the participants of that experiment
            for exp in exp_list:
                partList = Participant.objects.filter(experiment=exp).values('part_id').distinct()
                x = 0
                for person in partList:
                    temp = Participant.objects.filter(experiment=exp).filter(part_id=person['part_id']).order_by(
                        '-version')
                    participantNumber.append(temp[0])
                    x = x + 1
                if x == 0:
                    emptyExp.append(exp)

            context_dict['emptyExp'] = emptyExp
            context_dict['participantNumber'] = participantNumber
            context_dict['allexp'] = allexp
            return render(request, 'EyeMap2/index.html', context_dict)

        elif 'delete' in request.POST:
            exp_name = request.POST.get('exp_name')
            part_name = request.POST.get('part_name')
            exp = Experiment.objects.get(exp_name=exp_name)
            Participant.objects.get(part_id=part_name, experiment_id=exp).delete()

            exp_list = Experiment.objects.filter(owner=UserProfile.objects.get(id=request.user.id))
            # gets all the experiments of the user
            allexp = exp_list
            context_dict = {'experiments': exp_list}
            participantNumber = []
            emptyExp = []

            # loops through experiment list and gets all the participants of that experiment
            for exp in exp_list:
                partList = Participant.objects.filter(experiment=exp).values('part_id').distinct()
                x = 0
                for person in partList:
                    temp = Participant.objects.filter(experiment=exp).filter(part_id=person['part_id']).order_by(
                        '-version')
                    participantNumber.append(temp[0])
                    x = x + 1
                if x == 0:
                    emptyExp.append(exp)

            context_dict['emptyExp'] = emptyExp
            context_dict['participantNumber'] = participantNumber
            context_dict['allexp'] = allexp
            return render(request, 'EyeMap2/index.html', context_dict)
        else:
            # gets the selected option
            name = request.POST.get('exp_name')

            # main menu
            # shows all the experiments of the user if user selects "SHOW ALL" option
            if name is None or name == "SHOW ALL":
                # gets an experiment list
                exp_list = Experiment.objects.filter(owner=UserProfile.objects.get(id=request.user.id))
                # gets all the experiments of the user
                allexp = exp_list
                context_dict = {'experiments': exp_list}
                participantNumber = []
                emptyExp = []

                # loops through experiment list and gets all the participants of that experiment
                for exp in exp_list:
                    partList = Participant.objects.filter(experiment=exp).values('part_id').distinct()
                    x = 0
                    for person in partList:
                        temp = Participant.objects.filter(experiment=exp).filter(part_id=person['part_id']).order_by(
                            '-version')
                        participantNumber.append(temp[0])
                        x = x + 1
                    if x == 0:
                        emptyExp.append(exp)

                context_dict['emptyExp'] = emptyExp
                context_dict['participantNumber'] = participantNumber
                context_dict['allexp'] = allexp
                return render(request, 'EyeMap2/index.html', context_dict)

            # displays all participants of the experiment
            else:
                # gets an experiment list
                exp_list = Experiment.objects.filter(owner=UserProfile.objects.get(id=request.user.id), exp_name=name)
                # gets all the experiments of the user
                allexp = Experiment.objects.filter(owner=UserProfile.objects.get(id=request.user.id))
                context_dict = {'experiments': exp_list}
                participants = []
                # loops through experiment list and gets all the participants of that experiment
                for exp in exp_list:
                    partList = Participant.objects.filter(experiment=exp).values('part_id').distinct()
                    for person in partList:
                        temp = Participant.objects.filter(experiment=exp).filter(part_id=person['part_id']).order_by(
                            '-version')
                        participants.append(temp[0])
                context_dict['participants'] = participants
                context_dict['allexp'] = allexp
                return render(request, 'EyeMap2/index.html', context_dict)

    else:
        return render(request, 'EyeMap2/index.html')


def visualise(request):
    if request.user.is_authenticated():
        if request.session.get('sel_exp') and request.session.get('sel_part'):
            context_dict = {}

            # Get the trial Data
            name = request.session.get('sel_exp')
            page = Experiment.objects.get(exp_name=name)
            context_dict['aoiData'] = page.trial_data

            # Get the Participant data
            partId = request.session.get('sel_part')
            participants = Participant.objects.filter(experiment=page).filter(part_id=partId).order_by('-version')
            participant = participants[0]
            context_dict['driftData'] = participant.drift_data
            context_dict['fixData'] = participant.fix_data
            context_dict['saccData'] = participant.sacc_data

            return render(request, 'EyeMap2/visualise.html', context_dict)
        else:
            exp_list = Experiment.objects.filter(owner=UserProfile.objects.get(id=request.user.id))
            context_dict = {'experiments': exp_list}
            participants = []
            for exp in exp_list:
                partList = Participant.objects.filter(experiment=exp).values('part_id').distinct()
                for person in partList:
                    temp = Participant.objects.filter(experiment=exp).filter(part_id=person['part_id']).order_by(
                        '-version')
                    participants.append(temp[0])
            context_dict['participants_list'] = participants
            return render(request, 'EyeMap2/index.html', context_dict)
    else:
        return render(request, 'EyeMap2/index.html')


# Analysis
def analysis(request):
    if request.user.is_authenticated():
        if request.session.get('sel_exp') and request.session.get('sel_part'):
            var_list = ExpVariable.objects.all()
            context_dict = {'variables': var_list}
            variableList = []
            for var in var_list:
                temp = {"name": var.var_name, "level": var.var_cat, "fix": var.var_fix_rep, "word": var.var_word_rep}
                variableList.append(temp)

            context_dict['variableList'] = json.dumps(variableList)
            # Get the trial Data
            name = request.session.get('sel_exp')
            page = Experiment.objects.get(exp_name=name)
            context_dict['aoiData'] = page.trial_data

            # Get the Participant data
            partId = request.session.get('sel_part')
            participants = Participant.objects.filter(experiment=page).filter(part_id=partId).order_by('-version')
            participant = participants[0]
            context_dict['driftData'] = participant.drift_data
            context_dict['fixData'] = participant.fix_data
            context_dict['saccData'] = participant.sacc_data

            return render(request, 'EyeMap2/analysis.html', context_dict)
        else:
            return render(request, 'EyeMap2/index.html')
    else:
        return render(request, 'EyeMap2/index.html')


# Upload Experiment
def new_experiment(request):
    if 'load' in request.GET:
        exp_list = Experiment.objects.filter(owner=UserProfile.objects.get(id=request.user.id))
        context_dict = {'experiments': exp_list}
        participants = []
        for exp in exp_list:
            partList = Participant.objects.filter(experiment=exp).values('part_id').distinct()
            for person in partList:
                temp = Participant.objects.filter(experiment=exp).filter(part_id=person['part_id']).order_by(
                    '-version')
                participants.append(temp[0])
        context_dict['participants_list'] = participants
        return HttpResponseRedirect('../../EyeMap2/', context_dict)
        # return render(request, 'EyeMap2/index.html', context_dict)
    else:
        context_dict = {}
        return render(request, 'EyeMap2/newExperiment.html', context_dict)


# Save New Experiment
def check_font(request):
    if request.is_ajax():
        textInfo = get_text_info(request.POST['trialData'])
        msg = " "
        try:
            Fonts.objects.get(font_title=textInfo[2])
            msg = "fontFound"
        except ObjectDoesNotExist:
            msg = "fontNotFound"
        return HttpResponse(msg)


# Save New Experiment
def save_new_experiment(request):
    if request.is_ajax():
        expName = request.POST['expName']
        expDesc = request.POST['expDesc']

        trialData = html_to_text(request.POST['trialData'])
        font = Fonts.objects.get(font_title=trialData[0][2]).font_file_name
        trialData[0].append(font)
        trialnum = trialData[0][0]
        trialData = json.dumps(trialData)
        configData = json.dumps(xmltodict.parse(request.POST['configData']))

        partData = request.POST.getlist('partData[]')
        current_user = UserProfile.objects.get(id=request.user.id)
        exp_font = Fonts.objects.get(font_file_name=font)

        Experiment.objects.get_or_create(owner=current_user, exp_name=expName, exp_desc=expDesc,
                                         config_messages=configData, trial_data=trialData,
                                         num_participants=len(partData))

        exp = Experiment.objects.get(exp_name=expName)
        fileNames = request.POST.getlist('fileNames[]')
        for i in range(len(partData)):
            data = part_data(partData[i])
            driftData = sort_drift(data[0], trialnum)
            fixData = sort_fixes(data[1], trialnum)
            saccData = sort_sacc(data[2], trialnum)
            part_id = fileNames[i][:2]
            Participant.objects.get_or_create(part_id=part_id, experiment=exp, drift_data=driftData,
                                              fix_data=fixData, sacc_data=saccData, version=1.0, has_report=False)

        return HttpResponseRedirect('../new_experiment/' + '?load')


def sort_drift(data, dataLen):
    newDriftData = []
    temp = []
    for x in range(dataLen):
        temp.append(data.loc[data['trial'] == x].to_dict('records'))
        newDriftData.append(temp[0])
        temp = []
    return json.dumps(newDriftData)


def sort_fixes(data, dataLen):
    newfixData = []
    temp = []
    for x in range(dataLen):
        temp.append(data.loc[data['trial'] == x].to_dict('records'))
        newfixData.append(temp[0])
        temp = []
    return json.dumps(newfixData)


def sort_sacc(data, dataLen):
    newSaccData = []
    temp = []
    for x in range(dataLen):
        temp.append(data.loc[data['trial'] == x].to_dict('records'))
        newSaccData.append(temp[0])
        temp = []
    return json.dumps(newSaccData)


def part_data(partData):
    doc = xmltodict.parse(partData)
    trials = []
    fixes = []
    saccs = []
    drift = []

    for trial in doc['root']['trial']:
        trials.append(trial)

    for i in range(len(trials)):
        ff = pd.DataFrame(trials[i]['fix'])
        ff['trial'] = i
        fixes.append(ff)

        if 'drift' in trials[i]:
            df = pd.DataFrame(trials[i]['drift'], index=[0])
            df['trial'] = i
            drift.append(df)
        else:
            dummyData = {'eye': 'LR', 'x': 0, 'y': 0, 'off': 0, 'sx': 0, 'sy': 0, 'trial': i}
            df = pd.DataFrame(dummyData, index=[0])
            drift.append(df)

        sf = pd.DataFrame(trials[i]['sacc'])
        sf['trial'] = i
        saccs.append(sf)

    result = [pd.concat(drift), pd.concat(fixes), pd.concat(saccs)]
    return result


# Register
def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'avatar' in request.FILES:
                profile.avatar = request.FILES['avatar']

            profile.save()
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    return render(request, 'EyeMap2/register.html',
                  {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})


def user_login(request):
    logged_error = False
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect('../')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            # print("Invalid login details: {0}, {1}".format(username, password))
            # return HttpResponse("Invalid login details supplied.")
            logged_error = True
            return render(request, 'EyeMap2/index.html', {'logged_error': logged_error})
    else:
        return render(request, 'EyeMap2/index.html', {'logged_error': logged_error})


def user_logout(request):
    logout(request)
    return redirect('../../EyeMap2')


def update_data(request):
    fix_data = request.POST['newFixData']
    sacc_data = request.POST['newSaccData']
    drift_data = request.POST['newDriftData']
    name = request.session.get('sel_exp')
    page = Experiment.objects.get(exp_name=name)

    fix_data = organise_fixes(fix_data)
    sacc_data = organise_saccades(sacc_data)
    # Get the Participant data
    partId = request.session.get('sel_part')
    partList = Participant.objects.filter(experiment=page).filter(part_id=partId).order_by('-version')
    person = partList[0]

    if person.version == 1:
        Participant.objects.get_or_create(part_id=partId, experiment=page, drift_data=drift_data,
                                          fix_data=fix_data, sacc_data=sacc_data, version=2, has_report=False)
    else:
        person.drift_data = drift_data
        person.fix_data = fix_data
        person.sacc_data = sacc_data
        person.save()

    return HttpResponse('ok')


def organise_fixes(data):
    data = json.loads(data)
    trialnum = 0
    newfixData = []
    temp = []
    for i in range(len(data)):
        if data[i] != "":
            if data[i].get('trial') == trialnum:
                temp.append(data[i])
            if data[i].get('trial') > trialnum:
                trialnum = data[i].get('trial')
                newfixData.append(temp)
                temp = [data[i]]
        else:
            temp.append(data[i])

    newfixData.append(temp)
    return json.dumps(newfixData)


def organise_saccades(data):
    data = json.loads(data)
    trialnum = 0
    newsaccData = []
    temp = []
    for i in range(len(data)):
        if data[i] != "":
            if data[i].get('trial') == trialnum:
                temp.append(data[i])
            if data[i].get('trial') > trialnum:
                trialnum = data[i].get('trial')
                newsaccData.append(temp)
                temp = [data[i]]
        else:
            temp.append(data[i])

    newsaccData.append(temp)
    return json.dumps(newsaccData)


def gen_report(request):
    if request.method == 'POST':
        whichRep = request.POST.get('reportRadios')
        whichParts = request.POST.get('partRadios')
        whichEye = request.POST.get('eyeRadios')
        whichAOI = request.POST.get('aoiRadios')
        numAllowedGaze = request.POST.get('numAllowedGaze')
        numAllowedFix = request.POST.get('numAllowedFix')
        varList = request.POST.get('varList')
        AOIData = json.loads(request.POST.get('AOIData'))
        name = request.session.get('sel_exp')
        partId = request.session.get('sel_part')
        info = {
            'name': name,
            'partId': partId,
            'eye': whichEye,
            'AOIData': AOIData,
            'aoiType': whichAOI,
            'varList': varList,
            'numAllowedGaze': numAllowedGaze,
            'numAllowedFix': numAllowedFix,
            'reportType': whichRep
        }
        df = ""
        if whichParts == 'currentPart':
            df = report_current_part(info)
        else:
            df = report_all_parts(info)

        if ' ' in name:
            name = name.replace(" ", "")

        filename = name + '_' + whichAOI + '_' + whichRep + '_' + '.xlsx'
        bytIO = io.BytesIO()
        writer = pd.ExcelWriter(bytIO, engine='xlsxwriter')
        df.to_excel(writer, sheet_name=partId)
        writer.save()

        bytIO.seek(0)
        workbook = bytIO.read()
        response = HttpResponse(workbook, content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

    return response


def report_current_part(info):
    name = info['name']
    partId = info['partId']
    eye = info['eye']
    aoiType = info['aoiType']
    numAllowedGaze = info['numAllowedGaze']
    numAllowedFix = info['numAllowedFix']
    varList = info['varList']
    AOIData = info['AOIData']
    reportType = info['reportType']

    exp = Experiment.objects.filter(exp_name=name)
    participants = Participant.objects.filter(experiment=exp).filter(part_id=partId).order_by('-version')
    participant = participants[0]
    fixData = json.loads(participant.fix_data)
    saccData = json.loads(participant.sacc_data)

    basicInfo = {
        "name": name,
        "partId": partId,
        "eye": eye,
        "aoiType": aoiType,
        "numAllowedGaze": numAllowedGaze,
        "numAllowedFix": numAllowedFix
    }
    df = ""
    if eye == 'B':
        frames = []
        if checkEyes(fixData, "R"):
            basicInfo['eye'] = "R"
            temp = ''
            if reportType == 'wordRep':
                temp = prepWordData(varList, AOIData, fixData, saccData, basicInfo)
            else:
                temp = fixation_report(varList, AOIData, fixData, saccData, basicInfo)
            frames.append(temp)
        if checkEyes(fixData, "L"):
            basicInfo['eye'] = "L"
            temp = ''
            if reportType == 'wordRep':
                temp = prepWordData(varList, AOIData, fixData, saccData, basicInfo)
            else:
                temp = fixation_report(varList, AOIData, fixData, saccData, basicInfo)
            frames.append(temp)
        if len(frames) == 2:
            df = pd.concat(frames)
        else:
            df = temp
    else:
        if reportType == 'wordRep':
            df = prepWordData(varList, AOIData, fixData, saccData, basicInfo)
        else:
            df = fixation_report(varList, AOIData, fixData, saccData, basicInfo)
    return df


def checkEyes(fixData, eye):
    for trial in fixData:
        for fix in trial:
            if fix['eye'] == eye:
                return True
    return False


def report_all_parts(info):
    name = info['name']
    eye = info['eye']
    aoiType = info['aoiType']
    numAllowedGaze = info['numAllowedGaze']
    numAllowedFix = info['numAllowedFix']
    varList = info['varList']
    AOIData = info['AOIData']
    reportType = info['reportType']

    exp = Experiment.objects.filter(exp_name=name)
    partList = Participant.objects.filter(experiment=exp).values('part_id').distinct()
    x = 0
    masterdf = 0
    basicInfo = {
        "name": name,
        "eye": eye,
        "aoiType": aoiType,
        "numAllowedGaze": numAllowedGaze,
        "numAllowedFix": numAllowedFix
    }
    for person in partList:
        temp = Participant.objects.filter(experiment=exp).filter(part_id=person['part_id']).order_by('-version')
        part = temp[0]
        fixData = json.loads(part.fix_data)
        saccData = json.loads(part.sacc_data)
        basicInfo['partId'] = part.part_id
        if eye == 'B':
            if x == 0:
                frames = []
                if checkEyes(fixData, "R"):
                    basicInfo['eye'] = "R"
                    temp = prepWordData(varList, AOIData, fixData, saccData, basicInfo)
                    frames.append(temp)
                if checkEyes(fixData, "L"):
                    basicInfo['eye'] = "L"
                    temp = prepWordData(varList, AOIData, fixData, saccData, basicInfo)
                    frames.append(temp)
                if len(frames) == 2:
                    masterdf = pd.concat(frames)
                else:
                    masterdf = temp
            else:
                frames = []
                if checkEyes(fixData, "R"):
                    basicInfo['eye'] = "R"
                    temp = prepWordData(varList, AOIData, fixData, saccData, basicInfo)
                    frames.append(temp)
                if checkEyes(fixData, "L"):
                    basicInfo['eye'] = "L"
                    temp = prepWordData(varList, AOIData, fixData, saccData, basicInfo)
                    frames.append(temp)
                if len(frames) == 2:
                    df = pd.concat(frames)
                else:
                    df = temp
            if x > 0:
                tempFrames = [masterdf, df]
                result = pd.concat(tempFrames)
                masterdf = result
            x = x + 1
        else:
            if x == 0:
                masterdf = prepWordData(varList, AOIData, fixData, saccData, basicInfo)
            else:
                df = prepWordData(varList, AOIData, fixData, saccData, basicInfo)
            if x > 0:
                frames = [masterdf, df]
                result = pd.concat(frames)
                masterdf = result
            x = x + 1

    masterdf.fillna("", inplace=True)
    return masterdf


def frcp(info):
    name = info['name']
    partId = info['partId']
    eye = info['eye']
    varList = info['varList']
    AOIData = info['AOIData']


def frap(info):
    name = info['name']
    eye = info['eye']
    varList = info['varList']
    AOIData = info['AOIData']


def generate_file(request):
    # HTML information
    if request.method == 'POST':
        reportType = request.POST.get('reportType')
        # varList = json.loads(request.POST.get('varList'))
        varList = 0
        basicInfo = json.loads(request.POST.get('basicInfo'))
        AOIData = json.loads(request.POST.get('AOIData'))

        exp_name = basicInfo[0]
        exp = Experiment.objects.filter(exp_name=exp_name)
        # participants = Participant.objects.filter(experiment=exp).filter(part_id=basicInfo[1]).order_by('-version')
        participants = Participant.objects.filter(experiment=exp).filter(part_id=basicInfo[1])
        participant = participants[0]
        fixData = json.loads(participant.fix_data)
        saccData = json.loads(participant.sacc_data)

        df = prepWordData(varList, AOIData, fixData, saccData, basicInfo)
        filename = basicInfo[0] + '.xlsx'

        bytIO = io.BytesIO()
        writer = pd.ExcelWriter(bytIO, engine='xlsxwriter')
        df.to_excel(writer, sheet_name=basicInfo[1])
        writer.save()

        bytIO.seek(0)
        workbook = bytIO.read()
        response = HttpResponse(workbook, content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

    return response
