import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
import time
from scipy.ndimage import convolve

S = 0
I = 1
R = 2

N = 1000
dias = 365
p_infeccion = 0.3
p_recuperacion = 0.1
p_muerte = 0.02

KERNEL = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]], dtype=np.int32)


def crear_grid(n, semilla=42):
    rng = np.random.default_rng(semilla)
    grid = np.zeros((n, n), dtype=np.int8)
    pos = rng.choice(n * n, size=int(n * n * 0.01), replace=False)
    grid.flat[pos] = I
    return grid


def actualizar(grid, rng):
    n = len(grid)
    vecinos_I = convolve((grid == I).astype(np.int32), KERNEL, mode="constant", cval=0)
    rand1 = rng.random((n, n))
    rand2 = rng.random((n, n))
    nueva = grid.copy()
    nueva[(grid == S) & (vecinos_I > 0) & (rand1 < p_infeccion)] = I
    nueva[(grid == I) & (rand2 < p_muerte + p_recuperacion)] = R
    return nueva


def contar(grid):
    return int(np.sum(grid == S)), int(np.sum(grid == I)), int(np.sum(grid == R))


def validar():
    print("Validacion con 400 personas, 10 dias")
    n, total = 20, 400
    g = crear_grid(n, semilla=0)
    rng = np.random.default_rng(0)
    s_ant = total
    for d in range(10):
        s, i, r = contar(g)
        assert s + i + r == total, f"ERROR dia {d}: total={s+i+r}"
        assert s <= s_ant, f"ERROR dia {d}: S subio"
        print(f"  Dia {d}: S={s:4d}  I={i:4d}  R={r:4d}  OK")
        s_ant = s
        g = actualizar(g, rng)
    print("Validacion terminada\n")


def correr():
    grid = crear_grid(N)
    rng = np.random.default_rng(42)
    hist_s, hist_i, hist_r, frames = [], [], [], []

    inicio = time.time()
    for dia in range(dias):
        s, i, r = contar(grid)
        hist_s.append(s)
        hist_i.append(i)
        hist_r.append(r)
        print(f"Dia {dia:>3}  S={s:>8,}  I={i:>7,}  R={r:>8,}")
        if dia % 7 == 0:
            frames.append(grid.copy())
        grid = actualizar(grid, rng)

    tiempo = time.time() - inicio
    print(f"\nTiempo secuencial: {tiempo:.2f} s")
    return hist_s, hist_i, hist_r, frames, tiempo


if __name__ == "__main__":
    from guardar import guardar_secuencial

    validar()
    hist_s, hist_i, hist_r, frames, tiempo = correr()
    guardar_secuencial(hist_s, hist_i, hist_r, frames, tiempo)
