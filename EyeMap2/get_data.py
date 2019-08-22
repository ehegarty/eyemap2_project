from bs4 import BeautifulSoup


def html_to_text(html):
    text_info = get_text_info(html)
    words = get_words_unprocessed(html, text_info)
    texts = [text_info, words]
    return texts


def get_text_info(html):
    info = []
    soup = BeautifulSoup(html, "lxml")

    trials = len(soup.find_all('p'))
    info.append(trials)

    page = soup.find('style')
    temp = str(page.get_text().strip()).split('\n')
    temp = temp[2:-1]
    for i in temp:
        x = i.strip()
        y = i.split(':')
        info.append(y[1].strip()[:-1])
    page = soup.find('x')
    temp = str(page.get_text().strip())
    info.append(temp)
    page = soup.find('y')
    temp = str(page.get_text().strip())
    info.append(temp)
    page = soup.find('sep')
    if page is not None:
        temp = str(page.get_text().strip())
        info.append(temp)
    return info


def get_words_unprocessed(html, text_info):
    temp = get_trial_texts(html)
    result = []
    x = 0
    for i in temp:
        trial = temp[x]
        x += 1
        if len(text_info) < 8:
            words = separate_words_eng(trial)
        else:
            words = separate_words_other(trial, text_info[7])
        result.append(words)

    return result


def get_trial_texts(text):
    soup = BeautifulSoup(text, "lxml")
    page = soup.find_all('p')
    trials = len(soup.find_all('p'))
    text = []
    for i in range(trials):
        text.append(page[i].get_text())

    return text


def separate_words_eng(text):
    result = []
    word_list = text.split('\n')
    x = 0
    for line in word_list:
        temp = line.split()
        words = []
        for i in temp:
            words.append(" " + i)
        result.append(words)
        result[x].append(u'\n')
        x += 1
    temp = sum(result, [])

    while temp[0] == "\n" or temp[0] == "":
        temp = temp[1:]
    while temp[len(temp)-1] == "\n" or temp[0] == "":
        temp = temp[:-1]
    return temp


def separate_words_other(text, sep):
    result = []
    word_list = text.split('\n')
    x = 0
    for line in word_list:
        temp = line.split(sep)
        while "" in temp:
            temp.remove("")
        result.append(temp)
        result[x].append(u'\n')
        x += 1
    temp = sum(result, [])

    temp[:] = [item for item in temp if item != "\r"]
    for i in range(len(temp)):
        if temp[i] == "\n" and i > 1:
            tempWord = temp[i - 1][-1:len(temp[i - 1])]
            if tempWord == "\r":
                temp[i - 1] = temp[i - 1][0:-2]

    while temp[0] == "\n" or temp[0] == "":
        temp = temp[1:]
    while temp[len(temp)-1] == "\n" or temp[len(temp)-1] == "":
        temp = temp[:-1]
    return temp


def get_num_trials(xml):
    root = xml.getroot()
    trials_id = []
    for i in range(0, len(root.getchildren())):
        nodes = root.getchildren()[i]
        trials_id.append(nodes.attrib['id'])

    return trials_id
