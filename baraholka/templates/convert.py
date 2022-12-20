#преобразует html, созданный в bootstrap studio, в формат flask-bootstrap

INPUT_FILE_NAME = 'test.html'

import os

def replace(string, replaceIn, replaceOut):
    modifiedString = string.replace(replaceIn, replaceOut)
    if string == modifiedString:
        print(f'WARNING: "{replaceIn}" was not found')
    return modifiedString

simpleReplacements = [
    ['<!DOCTYPE html>', ''],
    ['<html lang="en">', '{% block html_attribs %} lang="en" {% endblock %}'],
    ['</html>', ''],
    ['<title>', '{% block title %}'],
    ['</title>', '{% endblock %}'],
    ['<body>', '{% block content %}'],
    ['</body>', '{% endblock %}'],
    ['<head>', ''],
    ['</head>', '']
]






inFile = open(INPUT_FILE_NAME, 'r',  encoding='utf-8')
string = inFile.read()
inFile.close()






for rep in simpleReplacements:
    string = replace(string, rep[0], rep[1])





scriptsString = ''
searchStartPos = 0
while 1:
    scriptStartPos = string.find('<script', searchStartPos)
    if scriptStartPos == -1:
        break
    scriptEndPos = string.find('</script>', scriptStartPos + len('<script'))
    if scriptEndPos == -1:
        break
    scriptEndPos += len('</script>') - 1

    pathStartPos = string.find('src="', scriptStartPos + len('<script'))
    if pathStartPos == -1:
        break
    pathStartPos += + len('src="')
    pathEndPos = string.find('"', pathStartPos)
    if pathEndPos == - 1:
        break
    pathEndPos -= 1

    scriptsString += '    ' + string[scriptStartPos:pathStartPos] + '{{url_for(\'.static\', filename=\'' + string[pathStartPos:pathEndPos+1] + '\')}}' + string[pathEndPos+1:scriptEndPos+1] + '\n'
    string = string[:scriptStartPos] + string[scriptEndPos+1:]

    searchStartPos = scriptStartPos

if scriptsString != '':
    string = '{% block scripts %}\n' + scriptsString + '    {{super()}}\n{% endblock %}\n'  + string




linksString = ''
searchStartPos = 0
while 1:
    linkStartPos = string.find('<link', searchStartPos)
    if linkStartPos == -1:
        break
    linkEndPos = string.find('>', linkStartPos + len('<link'))
    if linkEndPos == -1:
        break

    pathStartPos = string.find('href="', linkStartPos + len('<link'))
    if pathStartPos == - 1:
        break
    pathStartPos += len('href="')
    pathEndPos = string.find('"', pathStartPos)
    if pathEndPos == - 1:
        break
    pathEndPos -= 1

    linksString += '    ' + string[linkStartPos:pathStartPos] + '{{url_for(\'.static\', filename=\'' + string[pathStartPos:pathEndPos+1] + '\')}}' + string[pathEndPos+1:linkEndPos+1] + '\n'
    string = string[:linkStartPos] + string[linkEndPos+1:]

    searchStartPos = linkStartPos

if linksString != '':
    string = '{% block styles %}\n    {{super()}}\n' + linksString + '{% endblock %}\n'  + string




metasString = ''
searchStartPos = 0
while 1:
    metaStartPos = string.find('<meta', searchStartPos)
    if metaStartPos == -1:
        break
    metaEndPos = string.find('>', metaStartPos + len('<meta'))
    if metaEndPos == -1:
        break

    metasString += '    ' + string[metaStartPos:metaEndPos+1] + '\n'
    string = string[:metaStartPos] + string[metaEndPos+1:]

    searchStartPos = metaStartPos


if metasString != '':
    string = '{% block metas %}\n' + metasString + '{% endblock %}\n' + string






searchStartPos = 0
while 1:
    imgStartPos = string.find('<img', searchStartPos)
    if imgStartPos == -1:
        break

    imgEndPos = string.find('>', imgStartPos + len('<img'))
    if imgEndPos == -1:
        break

    pathStartPos = string.find('src="', imgStartPos + len('<img'))
    if pathStartPos == -1:
        break
    pathStartPos += len('src="')
    pathEndPos = string.find('"', pathStartPos)
    if pathEndPos == - 1:
        break
    pathEndPos -= 1


    string = string[:pathStartPos] + '{{url_for(\'.static\', filename=\'' + string[pathStartPos:pathEndPos+1] + '\')}}' + string[pathEndPos+1:]
    searchStartPos = pathEndPos + len('{{url_for(\'.static\', filename=\'') + len('\')}}')





string = '{% extends "bootstrap/base.html" %}\n\n' + string







OUT_FILE_NAME = INPUT_FILE_NAME

rename = ''
dotPos = INPUT_FILE_NAME.rfind('.')
if dotPos == -1:
    rename = INPUT_FILE_NAME + '_'
else :
    rename = INPUT_FILE_NAME[:dotPos] + '_' + INPUT_FILE_NAME[dotPos:]


os.rename(INPUT_FILE_NAME, rename)
wordsFile = open(OUT_FILE_NAME, 'w',  encoding='utf-8')
wordsFile.write(string)
wordsFile.close()
