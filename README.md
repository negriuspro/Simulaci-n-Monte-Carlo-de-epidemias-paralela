# Simulacion de epidemias SIR

Este proyecto simula como se propaga una enfermedad en una poblacion de 1 millon de personas durante 365 dias usando el modelo SIR.

## Que es el modelo SIR

Cada persona puede estar en uno de estos 3 estados:
- S = sana (puede contagiarse)
- I = infectada (puede contagiar a sus vecinos)
- R = recuperada (ya no se enferma ni contagia)

Cada dia el programa revisa cada persona y aplica estas reglas:
- Si esta sana y tiene un vecino infectado, se puede infectar con 30% de probabilidad
- Si esta infectada, puede recuperarse o morir con 12% de probabilidad

## Antes de correrlo instala las librerias

```
pip install -r requirements.txt
```

Esto instala numpy, scipy, matplotlib y pillow que son las librerias que usa el proyecto.

## Como correrlo

Para correr solo la version secuencial:
```
python secuencial/Secuencial.py
```

Para correr la version paralela completa (incluye experimentos con 1, 2, 4 y 8 cores):
```
python paralelo/Paralelo.py
```

## Archivos del proyecto

- secuencial/Secuencial.py - codigo de la simulacion secuencial
- paralelo/Paralelo.py - codigo de la simulacion paralela
- guardar.py - guarda todos los resultados
- requirements.txt - librerias necesarias

## Que genera al correr

En la carpeta resultados/ se guardan:
- estadisticas_secuencial.csv - cuantos S, I y R hay cada dia
- tiempos.csv - cuanto tardo cada version
- speedup.csv y speedup.png - grafica de que tan rapido fue el paralelo vs el secuencial
- curvas_sir_secuencial.png - grafica de como evoluciono la enfermedad
- brote_secuencial.gif - animacion del brote dia a dia
- brote_comparacion.gif - animacion comparando secuencial vs paralelo

## Como funciona la version paralela

La grilla se divide en bloques horizontales y cada core del procesador trabaja en un bloque al mismo tiempo. Se usan ghost cells que son filas prestadas de los bloques vecinos para que los bordes entre bloques funcionen correctamente. Las estadisticas como cantidad de infectados y R0 se calculan en paralelo y se suman al final.
