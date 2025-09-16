from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)

# Rutas de los archivos
ARCHIVO_OPERACIONES = 'operaciones.json'

def cargar_operaciones():
    try:
        with open(ARCHIVO_OPERACIONES, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def guardar_operaciones(operaciones):
    with open(ARCHIVO_OPERACIONES, 'w') as file:
        json.dump(operaciones, file, indent=4)

@app.route("/", methods=["GET", "POST"])
def index():
    operaciones = cargar_operaciones()
    if request.method == "POST":
        nueva_operacion = {
            "fecha": request.form["fecha"],
            "activo": request.form["activo"],
            "precio": request.form["precio"],
            "precio_objetivo": request.form["precio_objetivo"],
            "stop_loss": request.form["stop_loss"],
            "comentario_apertura": request.form["comentario_apertura"],
            "estado": "Abierta"
        }
        operaciones.append(nueva_operacion)
        guardar_operaciones(operaciones)
        return redirect(url_for('index'))
    return render_template("index.html", operaciones=operaciones)

@app.route("/cerrar_operacion/<int:index>", methods=["POST"])
def cerrar_operacion(index):
    operaciones = cargar_operaciones()
    if 0 <= index < len(operaciones):
        comentario_cierre = request.form.get("comentario_cierre", "Sin comentario de cierre")
        operaciones[index]["estado"] = "Cerrada"
        operaciones[index]["comentario_cierre"] = comentario_cierre
        guardar_operaciones(operaciones)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)