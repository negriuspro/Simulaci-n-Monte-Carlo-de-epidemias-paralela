import csv
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

dias = 365


def guardar_secuencial(hist_s, hist_i, hist_r, frames, tiempo):
    os.makedirs("resultados", exist_ok=True)

    with open("resultados/estadisticas_secuencial.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dia", "S", "I", "R"])
        for d in range(dias):
            w.writerow([d, hist_s[d], hist_i[d], hist_r[d]])
    print("Guardado: resultados/estadisticas_secuencial.csv")

    existe = os.path.exists("resultados/tiempos.csv")
    with open("resultados/tiempos.csv", "a", newline="") as f:
        w = csv.writer(f)
        if not existe:
            w.writerow(["version", "cores", "tiempo_s"])
        w.writerow(["secuencial", 1, round(tiempo, 4)])
    print("Guardado: resultados/tiempos.csv")

    plt.figure(figsize=(10, 4))
    plt.plot(hist_s, label="Susceptibles", color="steelblue")
    plt.plot(hist_i, label="Infectados", color="tomato")
    plt.plot(hist_r, label="Recuperados", color="seagreen")
    plt.xlabel("Dia")
    plt.ylabel("Personas")
    plt.title("Curvas SIR - secuencial")
    plt.legend()
    plt.tight_layout()
    plt.savefig("resultados/curvas_sir_secuencial.png", dpi=150)
    plt.close()
    print("Guardado: resultados/curvas_sir_secuencial.png")

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.axis("off")
    img = ax.imshow(frames[0], cmap="viridis", vmin=0, vmax=2, animated=True)
    titulo = ax.set_title("Dia 0")

    def animar(idx):
        img.set_data(frames[idx])
        titulo.set_text("Dia " + str(idx * 7))
        return img, titulo

    anim = animation.FuncAnimation(
        fig, animar, frames=len(frames), interval=150, blit=True
    )
    anim.save("resultados/brote_secuencial.gif", writer="pillow", fps=8)
    plt.close()
    print("Guardado: resultados/brote_secuencial.gif")


def guardar_paralelo(hist_s, hist_i, hist_r, frames, tiempo, r0_empirico, cores):
    os.makedirs("resultados", exist_ok=True)

    nombre = f"resultados/estadisticas_paralelo_{cores}cores.csv"
    with open(nombre, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dia", "S", "I", "R"])
        for d in range(dias):
            w.writerow([d, hist_s[d], hist_i[d], hist_r[d]])
    print(f"Guardado: {nombre}")

    existe = os.path.exists("resultados/tiempos.csv")
    with open("resultados/tiempos.csv", "a", newline="") as f:
        w = csv.writer(f)
        if not existe:
            w.writerow(["version", "cores", "tiempo_s", "r0_empirico"])
        w.writerow(["paralelo", cores, round(tiempo, 4), round(r0_empirico, 2)])
    print(f"Tiempo {cores} cores guardado en: resultados/tiempos.csv")


def guardar_speedup(tiempos):
    """tiempos = {"secuencial": t_seq, 1: t1, 2: t2, 4: t4, 8: t8}"""
    os.makedirs("resultados", exist_ok=True)
    t_base = tiempos.get("secuencial") or tiempos.get(1)

    cores_lista = [c for c in tiempos if c != "secuencial"]
    speedup_lista = [t_base / tiempos[c] for c in cores_lista]
    ideal_lista = [float(c) for c in cores_lista]

    plt.figure(figsize=(7, 5))
    plt.plot(cores_lista, speedup_lista, "o-", label="Speedup real", color="tomato")
    plt.plot(cores_lista, ideal_lista, "--", label="Speedup ideal", color="steelblue")
    plt.xlabel("Cores")
    plt.ylabel("Speedup")
    plt.title("Strong scaling: speedup vs cores")
    plt.xticks(cores_lista)
    plt.legend()
    plt.tight_layout()
    plt.savefig("resultados/speedup.png", dpi=150)
    plt.close()
    print("Guardado: resultados/speedup.png")

    with open("resultados/speedup.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cores", "tiempo_s", "speedup", "speedup_ideal"])
        for c, sp in zip(cores_lista, speedup_lista):
            w.writerow([c, round(tiempos[c], 4), round(sp, 3), float(c)])
    print("Guardado: resultados/speedup.csv")


def guardar_animacion_sidebyside(frames_seq, frames_par):
    os.makedirs("resultados", exist_ok=True)
    n = min(len(frames_seq), len(frames_par))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    ax1.axis("off")
    ax2.axis("off")
    img1 = ax1.imshow(frames_seq[0], cmap="viridis", vmin=0, vmax=2, animated=True)
    img2 = ax2.imshow(frames_par[0], cmap="viridis", vmin=0, vmax=2, animated=True)
    tit1 = ax1.set_title("Secuencial - Dia 0")
    tit2 = ax2.set_title("Paralelo (4 cores) - Dia 0")

    def animar(idx):
        img1.set_data(frames_seq[idx])
        img2.set_data(frames_par[idx])
        tit1.set_text(f"Secuencial - Dia {idx * 7}")
        tit2.set_text(f"Paralelo (4 cores) - Dia {idx * 7}")
        return img1, img2, tit1, tit2

    anim = animation.FuncAnimation(fig, animar, frames=n, interval=150, blit=True)
    anim.save("resultados/brote_comparacion.gif", writer="pillow", fps=8)
    plt.close()
    print("Guardado: resultados/brote_comparacion.gif")
