import numpy as np
import time
from scipy.ndimage import convolve
from multiprocessing import Pool, cpu_count

# Estados
S = 0
I = 1
R = 2

# Parametros
N = 1000
dias = 365
p_infeccion = 0.3
p_recuperacion = 0.1
p_muerte = 0.02

# Kernel vecinos
KERNEL = np.array([[1, 1, 1],
                   [1, 0, 1],
                   [1, 1, 1]], dtype=np.int32)


def crear_grid(n, semilla=42):
    rng = np.random.default_rng(semilla)
    grid = np.zeros((n, n), dtype=np.int8)
    pos = rng.choice(n * n, size=int(n * n * 0.01), replace=False)
    grid.flat[pos] = I
    return grid


# Esta funcion procesa solo un bloque
def actualizar_bloque(args):
    bloque, seed = args
    rng = np.random.default_rng(seed)

    vecinos_I = convolve((bloque == I).astype(np.int32),
                         KERNEL, mode="constant", cval=0)

    rand1 = rng.random(bloque.shape)
    rand2 = rng.random(bloque.shape)

    nueva = bloque.copy()

    nueva[(bloque == S) & (vecinos_I > 0) & (rand1 < p_infeccion)] = I
    nueva[(bloque == I) & (rand2 < p_muerte + p_recuperacion)] = R

    return nueva


# Divide la grilla en bloques horizontales
def dividir_grid(grid, n_procesos):
    return np.array_split(grid, n_procesos, axis=0)


# Junta los bloques nuevamente
def unir_grid(bloques):
    return np.vstack(bloques)


def contar(grid):
    s = int(np.sum(grid == S))
    i = int(np.sum(grid == I))
    r = int(np.sum(grid == R))
    return s, i, r


def correr_paralelo(n_procesos):
    grid = crear_grid(N)

    hist_s, hist_i, hist_r = [], [], []
    frames = []

    inicio = time.time()

    with Pool(processes=n_procesos) as pool:
        for dia in range(dias):
            s, i, r = contar(grid)
            hist_s.append(s)
            hist_i.append(i)
            hist_r.append(r)

            print(f"[{n_procesos} cores] Dia {dia:>3}  S={s:>8,}  I={i:>7,}  R={r:>8,}")

            if dia % 7 == 0:
                frames.append(grid.copy())

            bloques = dividir_grid(grid, n_procesos)

            # cada bloque con semilla diferente
            args = [(bloques[i], 42 + i + dia) for i in range(n_procesos)]

            bloques_actualizados = pool.map(actualizar_bloque, args)

            grid = unir_grid(bloques_actualizados)

    tiempo = time.time() - inicio
    print(f"\nTiempo paralelo ({n_procesos} cores): {tiempo:.2f} s")

    return hist_s, hist_i, hist_r, frames, tiempo


if __name__ == "__main__":
    from guardar import guardar

    # probar con diferentes cores
    for cores in [1, 2, 4, 8]:
        hist_s, hist_i, hist_r, frames, tiempo = correr_paralelo(cores)
        guardar(hist_s, hist_i, hist_r, frames, tiempo, version="paralelo", cores=cores)