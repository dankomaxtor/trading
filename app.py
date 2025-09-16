from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)

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

def calcular_resumen(operaciones):
    total_ganado_perdido = 0
    total_invertido = 0
    
    for op in operaciones:
        if op.get('estado') == 'Cerrada':
            total_ganado_perdido += op.get('ganado_perdido', 0)
            total_invertido += op.get('importe_invertido', 0)
            
    if total_invertido > 0:
        rentabilidad_total = (total_ganado_perdido / total_invertido) * 100
    else:
        rentabilidad_total = 0
        
    return {
        'total_ganado_perdido': round(total_ganado_perdido, 2),
        'rentabilidad_total': round(rentabilidad_total, 2)
    }

@app.route("/", methods=["GET", "POST"])
def index():
    operaciones = cargar_operaciones()
    if request.method == "POST":
        nueva_operacion = {
            "fecha": request.form["fecha"],
            "activo": request.form["activo"],
            "precio": float(request.form["precio"]),
            "precio_objetivo": float(request.form["precio_objetivo"]),
            "stop_loss": float(request.form["stop_loss"]),
            "comentario_apertura": request.form["comentario_apertura"],
            "importe_invertido": float(request.form["importe_invertido"]),
            "estado": "Abierta"
        }
        operaciones.append(nueva_operacion)
        guardar_operaciones(operaciones)
        return redirect(url_for('index'))
    
    resumen = calcular_resumen(operaciones)
    return render_template("index.html", operaciones=operaciones, resumen=resumen)

@app.route("/editar_operacion/<int:index>", methods=["GET", "POST"])
def editar_operacion(index):
    operaciones = cargar_operaciones()
    if 0 <= index < len(operaciones):
        if request.method == "POST":
            operacion_a_editar = operaciones[index]
            operacion_a_editar["fecha"] = request.form["fecha"]
            operacion_a_editar["activo"] = request.form["activo"]
            operacion_a_editar["precio"] = float(request.form["precio"])
            operacion_a_editar["precio_objetivo"] = float(request.form["precio_objetivo"])
            operacion_a_editar["stop_loss"] = float(request.form["stop_loss"])
            operacion_a_editar["comentario_apertura"] = request.form["comentario_apertura"]
            operacion_a_editar["importe_invertido"] = float(request.form["importe_invertido"])
            
            # También edita el comentario y valor de cierre si existen
            operacion_a_editar["comentario_cierre"] = request.form.get("comentario_cierre", operacion_a_editar.get("comentario_cierre", "Sin comentario de cierre"))
            operacion_a_editar["valor_cierre"] = float(request.form.get("valor_cierre", operacion_a_editar.get("valor_cierre", operacion_a_editar["precio"])))

            # Recalcula si la operación estaba cerrada
            if operacion_a_editar.get("estado") == "Cerrada":
                valor_cierre = operacion_a_editar.get("valor_cierre", operacion_a_editar["precio"])
                precio_entrada = operacion_a_editar["precio"]
                importe_invertido = operacion_a_editar["importe_invertido"]
                
                if precio_entrada != 0:
                    ganado_perdido = importe_invertido * ((valor_cierre / precio_entrada) - 1)
                    rentabilidad = (ganado_perdido / importe_invertido) * 100
                else:
                    ganado_perdido = 0
                    rentabilidad = 0
                    
                operacion_a_editar["ganado_perdido"] = round(ganado_perdido, 2)
                operacion_a_editar["rentabilidad"] = round(rentabilidad, 2)
            
            guardar_operaciones(operaciones)
            return redirect(url_for('index'))
        else:
            return render_template("editar.html", operacion=operaciones[index], index=index)
    return redirect(url_for('index'))

@app.route("/borrar_operacion/<int:index>", methods=["POST"])
def borrar_operacion(index):
    operaciones = cargar_operaciones()
    if 0 <= index < len(operaciones):
        del operaciones[index]
        guardar_operaciones(operaciones)
    return redirect(url_for('index'))

@app.route("/cerrar_operacion/<int:index>", methods=["POST"])
def cerrar_operacion(index):
    operaciones = cargar_operaciones()
    if 0 <= index < len(operaciones):
        comentario_cierre = request.form.get("comentario_cierre", "Sin comentario de cierre")
        valor_cierre = float(request.form.get("valor_cierre"))
        
        operacion_a_cerrar = operaciones[index]
        operacion_a_cerrar["estado"] = "Cerrada"
        operacion_a_cerrar["comentario_cierre"] = comentario_cierre
        operacion_a_cerrar["valor_cierre"] = valor_cierre
        
        # Realiza los cálculos con el importe invertido
        precio_entrada = operacion_a_cerrar.get("precio", 0)
        importe_invertido = operacion_a_cerrar.get("importe_invertido", 0)
        
        if precio_entrada != 0:
            ganado_perdido = importe_invertido * ((valor_cierre / precio_entrada) - 1)
            rentabilidad = (ganado_perdido / importe_invertido) * 100
        else:
            ganado_perdido = 0
            rentabilidad = 0
        
        operacion_a_cerrar["ganado_perdido"] = round(ganado_perdido, 2)
        operacion_a_cerrar["rentabilidad"] = round(rentabilidad, 2)
        
        guardar_operaciones(operaciones)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)