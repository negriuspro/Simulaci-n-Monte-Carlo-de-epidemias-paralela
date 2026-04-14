import numpy as np
import time
from scipy.ndimage import convolve

# Estados
S = 0  # sano
I = 1  # infectado
R = 2  # recuperado

# Parametros
N = 1000
dias = 365
p_infeccion = 0.3
p_recuperacion = 0.1
p_muerte = 0.02

# Suma los 8 vecinos de cada celda
KERNEL = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]], dtype=np.int32)


def crear_grid(n, semilla=42):
    rng = np.random.default_rng(semilla)
    grid = np.zeros((n, n), dtype=np.int8)
    # 1% de la poblacion infectada al inicio
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
    s = int(np.sum(grid == S))
    i = int(np.sum(grid == I))
    r = int(np.sum(grid == R))
    return s, i, r


# valida que el codigo funcione correctamente
def validar():
    print("=== Validacion con 400 personas, 10 dias ===")
    n = 20
    g = crear_grid(n, semilla=0)
    rng = np.random.default_rng(0)
    total = n * n
    s_ant = total

    for d in range(10):
        s, i, r = contar(g)
        assert s + i + r == total, f"ERROR dia {d}: S+I+R={s+i+r} != {total}"
        assert s <= s_ant, f"ERROR dia {d}: S subio de {s_ant} a {s}"
        print(f"  Dia {d}: S={s:4d}  I={i:4d}  R={r:4d}  total={s+i+r}  OK")
        s_ant = s
        g = actualizar(g, rng)

    print("Validacion terminada\n")


def correr():
    grid = crear_grid(N)
    rng = np.random.default_rng(42)

    hist_s, hist_i, hist_r = [], [], []
    frames = []

    inicio = time.time()
    for dia in range(dias):
        s, i, r = contar(grid)
        hist_s.append(s)
        hist_i.append(i)
        hist_r.append(r)
        print(f"Dia {dia:>3}  S={s:>8,}  I={i:>7,}  R={r:>8,}")

        if dia % 7 == 0:
            frames.append(grid.copy())  # 1 frame por semana para el GIF

        grid = actualizar(grid, rng)

    tiempo = time.time() - inicio
    print(f"\nTiempo secuencial: {tiempo:.2f} s")

    return hist_s, hist_i, hist_r, frames, tiempo


if __name__ == "__main__":
    from guardar import guardar

    validar()  # primero valida
    hist_s, hist_i, hist_r, frames, tiempo = correr()  # luego simula
    guardar(hist_s, hist_i, hist_r, frames, tiempo)  # luego guarda
