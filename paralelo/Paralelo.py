import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import time
from scipy.ndimage import convolve
from multiprocessing import Pool

S = 0
I = 1
R = 2

N = 1000
dias = 365
p_infeccion = 0.3
p_recuperacion = 0.1
p_muerte = 0.02

KERNEL = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]], dtype=np.int32)

R0_TEORICO = (p_infeccion * 8) / (p_recuperacion + p_muerte)


def crear_grid(n, semilla=42):
    rng = np.random.default_rng(semilla)
    grid = np.zeros((n, n), dtype=np.int8)
    pos = rng.choice(n * n, size=int(n * n * 0.01), replace=False)
    grid.flat[pos] = I
    return grid


def actualizar_bloque(args):
    bloque_ghost, tiene_top, tiene_bot, seed = args
    rng = np.random.default_rng(seed)
    vecinos_I = convolve(
        (bloque_ghost == I).astype(np.int32), KERNEL, mode="constant", cval=0
    )
    rand1 = rng.random(bloque_ghost.shape)
    rand2 = rng.random(bloque_ghost.shape)
    nueva = bloque_ghost.copy()
    nueva[(bloque_ghost == S) & (vecinos_I > 0) & (rand1 < p_infeccion)] = I
    nueva[(bloque_ghost == I) & (rand2 < p_muerte + p_recuperacion)] = R
    inicio = 1 if tiene_top else 0
    fin = -1 if tiene_bot else None
    return nueva[inicio:fin]


def contar_bloque(bloque):
    return (
        int(np.sum(bloque == S)),
        int(np.sum(bloque == I)),
        int(np.sum(bloque == R)),
    )


def preparar_bloques(grid, n_procesos, dia):
    """Divide el grid y agrega ghost cells a cada bloque."""
    bloques = np.array_split(grid, n_procesos, axis=0)
    args = []
    for idx, bloque in enumerate(bloques):
        tiene_top = idx > 0
        tiene_bot = idx < len(bloques) - 1
        partes = []
        if tiene_top:
            partes.append(bloques[idx - 1][-1:])
        partes.append(bloque)
        if tiene_bot:
            partes.append(bloques[idx + 1][:1])
        args.append(
            (np.vstack(partes), tiene_top, tiene_bot, 42 + idx + dia * n_procesos)
        )
    return args


def correr_paralelo(n_procesos):
    grid = crear_grid(N)
    hist_s, hist_i, hist_r, nuevas_inf, frames = [], [], [], [], []

    inicio = time.time()
    with Pool(processes=n_procesos) as pool:
        for dia in range(dias):

            bloques = np.array_split(grid, n_procesos, axis=0)
            conteos = pool.map(contar_bloque, bloques)
            s = sum(c[0] for c in conteos)
            i = sum(c[1] for c in conteos)
            r = sum(c[2] for c in conteos)
            hist_s.append(s)
            hist_i.append(i)
            hist_r.append(r)
            if dia > 0:
                nuevas_inf.append(hist_s[dia - 1] - s)
            print(f"[{n_procesos} cores] Dia {dia:>3}  S={s:>8,}  I={i:>7,}  R={r:>8,}")
            if dia % 7 == 0:
                frames.append(grid.copy())

            bloques_nuevos = pool.map(
                actualizar_bloque, preparar_bloques(grid, n_procesos, dia)
            )
            grid = np.vstack(bloques_nuevos)

    tiempo = time.time() - inicio

    r0_vals = [
        nuevas_inf[d] / hist_i[d]
        for d in range(min(20, len(nuevas_inf)))
        if hist_i[d] > 0
    ]
    r0_empirico = float(np.mean(r0_vals)) if r0_vals else 0.0

    print(f"\nTiempo paralelo ({n_procesos} cores): {tiempo:.2f} s")
    print(f"R0 teorico: {R0_TEORICO:.2f}  |  R0 empirico: {r0_empirico:.2f}")
    return hist_s, hist_i, hist_r, frames, tiempo, r0_empirico


if __name__ == "__main__":
    from guardar import guardar_paralelo, guardar_speedup, guardar_animacion_sidebyside
    from secuencial.Secuencial import correr as correr_seq

    print("Version secuencial (referencia)")
    hist_s_seq, hist_i_seq, hist_r_seq, frames_seq, tiempo_seq = correr_seq()

    tiempos = {"secuencial": tiempo_seq}
    frames_par_ref = None

    for cores in [1, 2, 4, 8]:
        print(f"\nParalelo con {cores} cores")
        hist_s, hist_i, hist_r, frames, tiempo, r0 = correr_paralelo(cores)
        guardar_paralelo(hist_s, hist_i, hist_r, frames, tiempo, r0, cores)
        tiempos[cores] = tiempo
        if cores == 4:
            frames_par_ref = frames

    guardar_speedup(tiempos)

    if frames_par_ref:
        guardar_animacion_sidebyside(frames_seq, frames_par_ref)
