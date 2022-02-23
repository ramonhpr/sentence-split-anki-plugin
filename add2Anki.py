import os
import requests
import sys
import re


input_path = sys.argv[1]
regex = r"\#+(?P<deckName>[\w\s-]+)\#+\s*|(?P<front>.+)$\n\n|(?P<back>.+\n)"

with open(input_path) as fd:
    lines = fd.read()

    matches = re.finditer(regex, lines, re.MULTILINE)
    notes = []
    lastDeckName = ''
    lastFront = ''
    accBack = ''
    for match in matches:
        deckName, front, back = match.groups()
        if deckName:
            lastDeckName = deckName
        if front:
            lastFront = front
        if back and '=' not in back:
            accBack += back
        if back and '=' in back:
            notes.append({
                "deckName": lastDeckName,
                "modelName": "Básico",
                "fields": {
                    "Frente": lastFront,
                    "Verso": accBack.replace("\n", "<br />")
                },
                "audio": [{
                    "path": os.path.abspath(f'./{lastFront}.mp3'),
                    "filename": f"{lastFront}.mp3",
                    "skipHash": "7e2c2f954ef6051373ba916f000168dc",
                    "fields": [
                        "Verso"
                    ]
                }],
                "options": {
                    "allowDuplicate": False,
                    "duplicateScope": "deck",
                    "duplicateScopeOptions": {
                        "deckName": "Default",
                        "checkChildren": False,
                        "checkAllModels": False
                    }
                },
                "tags": [
                    "generated"
                ],
            })
            accBack = ''
    print(notes)


    r = requests.post('http://127.0.0.1:8765', json={
        "action": "addNotes",
        "version": 6,
        "params": {
            "notes": notes
        }
    })

    print(r.json())
