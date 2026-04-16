import csv
import os
import matplotlib.pyplot as plt
import matplotlib.animation as animation


def guardar(hist_s, hist_i, hist_r, frames, tiempo):
    os.makedirs("resultados", exist_ok=True)

    # CSV estadisticas S/I/R por dia
    with open("resultados/estadisticas_secuencial.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dia", "S", "I", "R"])
        for d in range(dias):
            w.writerow([d, hist_s[d], hist_i[d], hist_r[d]])
    print("Guardado: estadisticas_secuencial.csv")

    # CSV tiempos para grafica de speedup
    existe = os.path.exists("resultados/tiempos.csv")
    with open("resultados/tiempos.csv", "a", newline="") as f:
        w = csv.writer(f)
        if not existe:
            w.writerow(["version", "cores", "tiempo_s"])
        w.writerow(["secuencial", 1, round(tiempo, 4)])
    print("Guardado: tiempos.csv")

    # Grafica curvas S, I, R
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
    print("Guardado: curvas_sir_secuencial.png")

    # GIF animado 1 frame por semana
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
