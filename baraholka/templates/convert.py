#преобразует html, созданный в bootstrap studio, в формат flask-bootstrap

import os
import sys


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



inputFileName=''
if len(sys.argv) > 1:
    inputFileName = sys.argv[1]

    try:
        inFile = open(inputFileName, 'r',  encoding='utf-8')
    except FileNotFoundError:
        print(f'ERROR: file "{inputFileName}" not found')
        exit()

    string = inFile.read()
    inFile.close()

    fileName = inputFileName
    dotPos = inputFileName.rfind('.')
    if dotPos != -1:
        fileName = inputFileName[:dotPos]
        
else:
    print(f'ERROR: input file not specified')
    exit()


inFile = open(inputFileName, 'r',  encoding='utf-8')
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

    scriptsString += '    ' + string[scriptStartPos:pathStartPos] + '{{url_for(\'.static\', filename=\'' + f'{fileName}/' + string[pathStartPos:pathEndPos+1] + '\')}}' + string[pathEndPos+1:scriptEndPos+1] + '\n'
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

    linksString += '    ' + string[linkStartPos:pathStartPos] + '{{url_for(\'.static\', filename=\''  + f'{fileName}/' + string[pathStartPos:pathEndPos+1] + '\')}}' + string[pathEndPos+1:linkEndPos+1] + '\n'
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


    string = string[:pathStartPos] + '{{url_for(\'.static\', filename=\''  + f'{fileName}/'+ string[pathStartPos:pathEndPos+1] + '\')}}' + string[pathEndPos+1:]
    searchStartPos = pathEndPos + len('{{url_for(\'.static\', filename=\'' + f'{fileName}/') + len('\')}}')





string = '{% extends "bootstrap/base.html" %}\n\n' + string







OUT_FILE_NAME = inputFileName

rename = ''
dotPos = inputFileName.rfind('.')
if dotPos == -1:
    rename = inputFileName + '_'
else :
    rename = inputFileName[:dotPos] + '_' + inputFileName[dotPos:]


os.rename(INPUT_FILE_NAME, rename)
wordsFile = open(OUT_FILE_NAME, 'w',  encoding='utf-8')
wordsFile.write(string)
wordsFile.close()
