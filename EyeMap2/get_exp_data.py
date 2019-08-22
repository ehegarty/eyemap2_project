import pandas as pd
from .get_data import get_num_trials


def build_drift_frame(xml):
    root = xml.getroot()
    trials = get_num_trials(xml)
    df = pd.DataFrame(columns=('id', 'trial', 'eye', 'x', 'y', 'off', 'sx', 'sy'))

    for i in trials:
        obj = root.getchildren()[int(i)].getchildren()[0]
        for j in range(0, len(obj)):
            temp = obj.getchildren()
            row = dict(zip(['id', 'trial', 'eye', 'x', 'y', 'off', 'sx', 'sy'],
                           [i, i, temp[0].text, temp[1].text, temp[2].text, temp[3].text, temp[4].text, temp[5].text]))
            row_s = pd.Series(row)
            df = df.append(row_s, ignore_index=True)

    return df


def build_saccade_frame(xml):
    root = xml.getroot()
    trials = get_num_trials(xml)
    sf = pd.DataFrame(columns=('trial', 'eye', 'st', 'et', 'dur', 'x', 'y', 'tx', 'ty', 'ampl', 'pv', 'id'))

    for i in trials:
        for j in range(0, len(root.getchildren()[int(i)].getchildren())):
            obj = root.getchildren()[int(i)].getchildren()[j]
            if obj.tag == 'sacc':
                temp = obj.getchildren()
                row = dict(zip(['trial', 'eye', 'st', 'et', 'dur', 'x', 'y', 'tx', 'ty', 'ampl', 'pv', 'id'],
                               [i, temp[0].text, temp[1].text, temp[2].text, temp[3].text, temp[4].text,
                                temp[5].text, temp[6].text, temp[7].text, temp[8].text, temp[9].text, temp[10].text]))
                row_s = pd.Series(row)
                sf = sf.append(row_s, ignore_index=True)

    return sf
