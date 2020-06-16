try:
    with open('launcher-settings.ini', 'r', encoding='UTF-8') as settings:
        data = settings.readlines()
        lang = data[1][5:]
except FileNotFoundError:
    lang = 'eng'
if lang == 'rus':
    import lang.rus as r
else:
    import lang.eng as r
