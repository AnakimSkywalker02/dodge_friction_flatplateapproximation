# Applicazione dell'analogia della lastra piana sulla centerline bidimensionale di un modello 3D

Questo progetto utilizza un modello 3D in Blender ispirato a una dodge challenger srt hellcat per estrarre le lunghezze del dorso e del ventre dell'auto riferite al frame della centerline e calcolare il coefficiente di attrito CF e la resistenza di attrito tramite l'analogia della lastra piana per diverse condizioni dello strato limite.

## Contenuto
- `estrai_lunghezze.py`: script da eseguire in Blender
- `centerlineanalysis.py`: script Python con calcoli e grafico
- `dodgechallenger2D2.blend`: file contenente la centerline isolata con distinzione fra oggetto dorso e oggetto ventre
- `dodgechallenger.blend`: file contenente il modello 3D completo dell'auto da cui viene estratta la centerline

## Uso
1. Apri `dodgechallenger2D2.blend` in Blender e lancia `estrai_lunghezze.py` dalla sezione Scripting, verranno forniti come risultati 2 file di testo contenenti la lunghezza del dorso e del ventre.
2. Apri `centerlineanalysis.py` in un editor Python (Spyder consigliato) e esegui il programma seguendo le richieste, una  richiesta in particolare sarà scegliere di analizzare il dorso come wet-length o il ventre.
