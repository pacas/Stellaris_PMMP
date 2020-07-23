import files_const as pth


try:
    with open(pth.ini_file, 'r', encoding='UTF-8') as settings:
        data = settings.readlines()
        lang = data[1][5:]
except FileNotFoundError:
    lang = 'eng'
if lang == 'rus':
    import lang.rus as r
else:
    import lang.eng as r
