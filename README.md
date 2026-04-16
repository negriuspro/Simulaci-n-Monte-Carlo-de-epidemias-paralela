Simulacion Monte Carlo de epidemias paralela

Simulacion de propagacion de enfermedades usando el modelo SIR en una grilla 2D de 1000x1000 celdas 1 millon de personas durante 365 dias.

Modelo SIR

Cada persona esta en uno de tres estados:

S (Susceptible): sana, puede contagiarse
I (Infectado): enferma, puede contagiar a sus vecinos
R (Recuperado): ya no participa en el contagio

Cada dia se aplican estas reglas a todas las personas:
Una persona S se infecta si tiene al menos un vecino infectado con probabilidad 0.3
Una persona I se recupera o muere con probabilidad 0.12 y pasa a R

Instalacion de requisitos

Antes de correr el programa hay que instalar las librerias necesarias.

Instala las librerias con este comando:

pip install -r requirements.txt

Eso instala automaticamente: numpy, scipy, matplotlib y pillow.

Como correrlo

python Secuencial.py

Eso ejecuta la simulacion completa y guarda todos los resultados.

Archivos

Secuencial.py

Contiene la logica de la simulacion:
Crea la grilla con 5 personas infectadas al inicio
Cada dia actualiza el estado de todas las personas usando NumPy
Al terminar llama automaticamente a guardar.py

guardar.py

Guarda los resultados en la carpeta resultados:

Archivo

estadisticas_secuencial.csv: cantidad de S, I, R por cada dia

tiempos.csv: tiempo total de ejecucion

curvas_sir_secuencial.png: grafica de las 3 curvas a lo largo del tiempo

brote_secuencial.gif: animacion del brote con 1 frame por semana

requirements.txt

Lista de librerias necesarias para correr el proyecto.


Paralelización

Paralelización de la simulación

Se implementó una versión paralela del modelo SIR utilizando multiprocessing en Python para aprovechar múltiples núcleos del CPU.

La estrategia utilizada fue dividir la grilla 2D en bloques horizontales, donde cada bloque es procesado por un proceso independiente.

Cada proceso ejecuta la actualización diaria del modelo sobre su bloque, aplicando las mismas reglas del modelo SIR:
- Contagio basado en vecinos infectados
- Recuperación o muerte con cierta probabilidad

Luego, los bloques actualizados se combinan nuevamente para formar la grilla completa del siguiente día.

Para evitar problemas de aleatoriedad, cada proceso utiliza una semilla diferente en el generador de números aleatorios.

Experimentos de rendimiento (Strong Scaling)

Se realizaron pruebas ejecutando la simulación con diferentes cantidades de núcleos:

- 1 core (secuencial)
- 2 cores
- 4 cores
- 8 cores

Resultados:

El tiempo de ejecución disminuye a medida que se incrementa el número de cores, demostrando el beneficio del paralelismo.

Ejemplo de resultados obtenidos:

- Secuencial (1 core): ~8.5 segundos
- Paralelo (2 cores): ~5.7 segundos

Se generó una gráfica de speed-up que muestra la mejora de rendimiento al aumentar los núcleos.

Limitaciones

La implementación actual no incluye ghost cells completas entre bloques, lo que puede generar pequeñas diferencias en los bordes de cada bloque.

Además, el uso de multiprocessing introduce overhead que limita la eficiencia en algunos casos.

Estas limitaciones son comunes en implementaciones paralelas básicas.

