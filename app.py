from flask import Flask, request, render_template_string
import boto3
import json

app = Flask(__name__)

# Configuración de SQS
sqs = boto3.client('sqs', region_name='us-east-1')  # Cambia la región si es necesario
QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/565393027941/notas-actividad'

@app.route('/')
def formulario():
    # HTML del formulario con estilos
    formulario_html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Publicador SQS</title>
        <!-- Bootstrap CSS -->
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f8f9fa; /* Fondo claro */
                padding: 20px;
            }
            .form-container {
                max-width: 600px;
                margin: 50px auto;
                padding: 20px;
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .form-container h1 {
                text-align: center;
                color: #0080c3; /* Azul institucional */
                margin-bottom: 20px;
            }
            .btn-primary {
                background-color: #0080c3; /* Azul institucional */
                border: none;
            }
            .btn-primary:hover {
                background-color: #006aa1; /* Azul más oscuro */
            }
            label {
                color: #343a40; /* Texto oscuro */
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="form-container">
            <h1>Publicador de Mensajes</h1>
            <form action="/enviar" method="post">
                <div class="mb-3">
                    <label for="codigo_estudiante" class="form-label">Código Estudiante:</label>
                    <input type="text" class="form-control" id="codigo_estudiante" name="codigo_estudiante" required>
                </div>
                <div class="mb-3">
                    <label for="codigo_asignatura" class="form-label">Código Asignatura:</label>
                    <input type="text" class="form-control" id="codigo_asignatura" name="codigo_asignatura" required>
                </div>
                <div class="mb-3">
                    <label for="tipo_actividad" class="form-label">Tipo de Actividad:</label>
                    <select class="form-select" id="tipo_actividad" name="tipo_actividad" required>
                        <option value="Seguimiento">Seguimiento</option>
                        <option value="Parcial">Parcial</option>
                        <option value="Final">Final</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label for="peso_actividad" class="form-label">Peso de Actividad (%):</label>
                    <input type="number" class="form-control" id="peso_actividad" name="peso_actividad" required>
                </div>
                <div class="mb-3">
                    <label for="calificacion" class="form-label">Calificación:</label>
                    <input type="number" step="0.1" class="form-control" id="calificacion" name="calificacion" required>
                </div>
                <div class="mb-3">
                    <label for="email" class="form-label">Email del Estudiante:</label>
                    <input type="email" class="form-control" id="email" name="email" required>
                </div>
                <button type="submit" class="btn btn-primary w-100">Enviar</button>
            </form>
        </div>

        <!-- Bootstrap JS -->
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    '''
    return render_template_string(formulario_html)

@app.route('/enviar', methods=['POST'])
def enviar_a_sqs():
    # Obtener datos del formulario
    datos = {
        "CodigoEstudiante": request.form['codigo_estudiante'],
        "CodigoAsignatura": request.form['codigo_asignatura'],
        "TipoActividad": request.form['tipo_actividad'],
        "PesoActividad": float(request.form['peso_actividad']),
        "Calificacion": float(request.form['calificacion']),
        "Email": request.form['email']
    }

    # Enviar mensaje en formato JSON a SQS
    response = sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps(datos)
    )
    message_id = response['MessageId']
    
    # HTML de la respuesta con estilos
    response_html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mensaje Enviado</title>
        <!-- Bootstrap CSS -->
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f8f9fa; /* Fondo claro */
                padding: 20px;
            }}
            .response-container {{
                max-width: 600px;
                margin: 50px auto;
                padding: 20px;
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                text-align: center;
            }}
            .response-container h1 {{
                color: #0080c3; /* Azul institucional */
                margin-bottom: 20px;
            }}
            .response-container p {{
                font-size: 18px;
                color: #343a40;
            }}
            .btn-primary {{
                background-color: #0080c3; /* Azul institucional */
                border: none;
            }}
            .btn-primary:hover {{
                background-color: #006aa1; /* Azul más oscuro */
            }}
        </style>
    </head>
    <body>
        <div class="response-container">
            <h1>¡Mensaje Enviado!</h1>
            <p>Su mensaje ha sido enviado correctamente a la cola SQS.</p>
            <p><strong>ID del Mensaje:</strong></p>
            <div class="alert alert-success" role="alert">
                {message_id}
            </div>
            <a href="/" class="btn btn-primary">Volver al formulario</a>
        </div>

        <!-- Bootstrap JS -->
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    '''
    return render_template_string(response_html)

if __name__ == '__main__':
    app.run(debug=True)
