import csv
import os
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def guardar(hist_s, hist_i, hist_r, frames, tiempo, version="secuencial", cores=1):
    os.makedirs("resultados", exist_ok=True)

    nombre_csv = f"resultados/estadisticas_{version}_{cores}cores.csv"

    with open(nombre_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dia", "S", "I", "R"])
        for d in range(len(hist_s)):
            w.writerow([d, hist_s[d], hist_i[d], hist_r[d]])

    print(f"Guardado: {nombre_csv}")

    tiempos_path = "resultados/tiempos.csv"
    existe = os.path.exists(tiempos_path)

    with open(tiempos_path, "a", newline="") as f:
        w = csv.writer(f)
        if not existe:
            w.writerow(["version", "cores", "tiempo_s"])

        w.writerow([version, cores, round(tiempo, 4)])

    print("Guardado: tiempos.csv")

    plt.figure(figsize=(10, 4))
    plt.plot(hist_s, label="Susceptibles")
    plt.plot(hist_i, label="Infectados")
    plt.plot(hist_r, label="Recuperados")

    plt.xlabel("Dia")
    plt.ylabel("Personas")
    plt.title(f"Curvas SIR - {version} ({cores} cores)")
    plt.legend()
    plt.tight_layout()

    nombre_png = f"resultados/curvas_sir_{version}_{cores}cores.png"
    plt.savefig(nombre_png, dpi=150)
    plt.close()

    print(f"Guardado: {nombre_png}")

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.axis("off")

    img = ax.imshow(frames[0], cmap="viridis", vmin=0, vmax=2, animated=True)
    titulo = ax.set_title("Dia 0")

    def animar(idx):
        img.set_data(frames[idx])
        titulo.set_text(f"Dia {idx * 7}")
        return img, titulo

    anim = animation.FuncAnimation(
        fig, animar, frames=len(frames), interval=150, blit=True
    )

    nombre_gif = f"resultados/brote_{version}_{cores}cores.gif"
    anim.save(nombre_gif, writer="pillow", fps=8)
    plt.close()

    print(f"Guardado: {nombre_gif}")

    generar_speedup()


def generar_speedup():
    path = "resultados/tiempos.csv"

    if not os.path.exists(path):
        return

    data = []
    t_secuencial = None  #Inicializar

    with open(path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["version"] == "paralelo":
                data.append((int(row["cores"]), float(row["tiempo_s"])))

            if row["version"] == "secuencial":
                t_secuencial = float(row["tiempo_s"])

  
    if not data or t_secuencial is None:
        return

    data.sort()
    cores = [x[0] for x in data]
    tiempos = [x[1] for x in data]

    speedup = [t_secuencial / t for t in tiempos]

    plt.figure()
    plt.plot(cores, speedup, marker="o")
    plt.xlabel("Cores")
    plt.ylabel("Speed-up")
    plt.title("Speed-up paralelo")
    plt.grid()

    plt.savefig("resultados/speedup.png")
    plt.close()

    print("Guardado: speedup.png")