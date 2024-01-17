import json
import math
import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def calcular_distancia_maxima(v0, theta):
    g = 9.8  # Aceleración debida a la gravedad en m/s^2
    theta_rad = math.radians(theta)  # Convertir ángulo a radianes
    return (v0**2 * math.sin(2 * theta_rad)) / g

def calcular_altura_maxima(v0, theta):
    g = 9.8  # Aceleración debida a la gravedad en m/s^2
    theta_rad = math.radians(theta)  # Convertir ángulo a radianes
    return (v0**2 * math.sin(theta_rad)**2) / (2 * g)

def analizar_proyectil(v0, theta):
    g = 9.8  # Aceleración debida a la gravedad en m/s^2
    theta_rad = math.radians(theta)  # Convertir ángulo a radianes

    tiempo_vuelo = (2 * v0 * math.sin(theta_rad)) / g
    intervalo_tiempo = tiempo_vuelo / 100  # Dividir el tiempo de vuelo en 100 intervalos
    distancia_maxima = calcular_distancia_maxima(v0, theta)
    altura_maxima = calcular_altura_maxima(v0, theta)

    # Analizar y guardar datos en intervalos de tiempo
    datos_intervalo = []
    tiempo_actual = 0
    while tiempo_actual <= tiempo_vuelo:
        distancia_recorrida = v0 * math.cos(theta_rad) * tiempo_actual
        altura_actual = v0 * math.sin(theta_rad) * tiempo_actual - 0.5 * g * tiempo_actual**2
        datos_intervalo.append({
            "tiempo": tiempo_actual,
            "distancia": distancia_recorrida,
            "altura": altura_actual
        })
        tiempo_actual += intervalo_tiempo

    # Calcular la distancia total recorrida
    distancia_total = datos_intervalo[-1]["distancia"]

    return {
        "tiempo_vuelo": tiempo_vuelo,
        "distancia_maxima": distancia_maxima,
        "altura_maxima": altura_maxima,
        "distancia_total": distancia_total,
        "datos_intervalo": datos_intervalo
    }

def main():
    # Layout para la entrada de parámetros
    layout_entrada = [
        [sg.Text("Número de proyectiles:")],
        [sg.Input(key="-NUM_PROYECTILES-", size=(10, 1))],
        [sg.Button("Aceptar")]
    ]

    ventana_entrada = sg.Window("Entrada de Parámetros", layout_entrada)

    while True:
        event, values = ventana_entrada.read()

        if event == sg.WIN_CLOSED:
            break

        if event == "Aceptar":
            num_proyectiles = int(values["-NUM_PROYECTILES-"])
            ventana_entrada.close()
            break

    # Layout para la entrada de datos de cada proyectil
    layout_proyectiles = []
    for i in range(1, num_proyectiles + 1):
        layout_proyectiles.extend([
            [sg.Text(f"Proyectil {i}:")],
            [sg.Text("Velocidad inicial (m/s):"), sg.Input(key=f"-V0_{i}-", size=(10, 1))],
            [sg.Text("Ángulo inicial (grados):"), sg.Input(key=f"-THETA_{i}-", size=(10, 1))],
            [sg.Text("")],  # Espacio en blanco para separar los bloques
        ])

    layout_proyectiles.append([sg.Button("Analizar")])

    # Ventana principal
    layout_principal = [
        [sg.Column(layout_proyectiles, scrollable=True, vertical_scroll_only=True)],
        [sg.Canvas(key="-CANVAS-", size=(400, 400))],
        [sg.Button("Cerrar")]
    ]

    ventana_principal = sg.Window("Análisis de Proyectiles", layout_principal, resizable=True)

    while True:
        event, values = ventana_principal.read()

        if event == sg.WIN_CLOSED or event == "Cerrar":
            break

        if event == "Analizar":
            datos_proyectiles = []
            proyectiles_superaron_tiempo = []
            proyectil_max_altitud = {"id": None, "altura": -1}

            for i in range(1, num_proyectiles + 1):
                v0 = float(values[f"-V0_{i}-"])
                theta = float(values[f"-THETA_{i}-"])

                datos_proyectil = analizar_proyectil(v0, theta)
                datos_proyectiles.append(datos_proyectil)

                # Verificar si el proyectil supera los 100 metros de altura
                if datos_proyectil["altura_maxima"] > 100:
                    sg.popup(f"¡Felicidades! El Proyectil {i} superó los 100 metros de altura.")

                # Verificar si el tiempo de vuelo supera los 5 segundos
                if datos_proyectil["tiempo_vuelo"] > 5:
                    proyectiles_superaron_tiempo.append(i)

                # Verificar si alcanza máxima altitud
                if datos_proyectil["altura_maxima"] > proyectil_max_altitud["altura"]:
                    proyectil_max_altitud["id"] = i
                    proyectil_max_altitud["altura"] = datos_proyectil["altura_maxima"]

            # Mostrar gráfico en la ventana
            fig, ax = plt.subplots()
            for i, datos_proyectil in enumerate(datos_proyectiles, start=1):
                tiempos = [punto["tiempo"] for punto in datos_proyectil["datos_intervalo"]]
                distancias = [punto["distancia"] for punto in datos_proyectil["datos_intervalo"]]
                alturas = [punto["altura"] for punto in datos_proyectil["datos_intervalo"]]
                ax.plot(distancias, alturas, label=f"Proyectil {i}")

            ax.set_xlabel("Distancia (metros)")
            ax.set_ylabel("Altura (metros)")
            ax.set_title("Trayectorias de los Proyectiles")
            ax.legend()

            canvas_elem = ventana_principal["-CANVAS-"]
            canvas = FigureCanvasTkAgg(fig, master=canvas_elem.Widget)
            canvas.draw()
            canvas.get_tk_widget().pack(side='top', fill='both', expand=1)

            # Mostrar resultados adicionales
            sg.popup(f"Distancias totales recorridas:\n{', '.join([f'Proyectil {i}: {round(datos['distancia_total'], 2)} metros' for i, datos in enumerate(datos_proyectiles, start=1)])}\n"
                     f"Proyectil que alcanzó mayor altitud: {proyectil_max_altitud['id']} (Altura: {round(proyectil_max_altitud['altura'], 2)} metros)\n"
                     f"Proyectiles que superaron un tiempo de vuelo de 5 segundos: {', '.join(map(str, proyectiles_superaron_tiempo))}")

            # Guardar datos en un archivo JSON
            with open("analisis_proyectiles.json", "w") as file:
                json.dump(datos_proyectiles, file, indent=2)

    ventana_principal.close()

if __name__ == "__main__":
    main()
