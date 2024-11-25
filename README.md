
### **README Completo de CloudBridge: Flask + AWS SQS + AWS SNS para Manejo de Notas**

# **CloudBridge: Flask + AWS SQS + AWS SNS para el Manejo de Notas**

CloudBridge es una aplicación desarrollada con **Flask** para facilitar la **gestión académica**, permitiendo que estudiantes ingresen sus notas a través de un formulario interactivo y moderno. Los datos se envían a **AWS SQS** en formato JSON, luego son procesados mediante una función **AWS Lambda**. Si la calificación ingresada es **reprobada**, el sistema envía automáticamente una notificación a través de **AWS SNS** o **SES** a los correos de las personas correspondientes (estudiantes, administración o tópicos suscritos).

---

## **Características Principales**
- **Flask**: Frontend y backend para el manejo de datos desde un formulario amigable.
- **AWS SQS**: Envío de los datos del formulario en formato JSON a una cola para su procesamiento.
- **AWS Lambda**: Procesamiento automático de los mensajes desde la cola SQS para verificar si la calificación es reprobada.
- **AWS SNS**: Notificaciones automáticas a través de un tópico SNS cuando se detectan notas reprobadas.
- **AWS SES**: Correos dinámicos directos a los estudiantes y la administración para gestionar los casos críticos.

---

## **Requisitos del Proyecto**
Este proyecto está diseñado para el **manejo de notas académicas**, en el cual un estudiante puede ingresar información relevante sobre su actividad académica y calificación. El flujo principal del sistema es:

1. **Ingreso de Información**:
   - **Código del Estudiante**.
   - **Código de la Asignatura**.
   - **Tipo de Actividad** (Seguimiento, Parcial, Final).
   - **Peso de la Actividad** en porcentaje.
   - **Calificación** del estudiante.
   - **Email del Estudiante** para notificaciones.
   
2. **Formato JSON para AWS SQS**:
   - Los datos ingresados son enviados a una cola SQS en **formato JSON** para ser procesados.
   - Ejemplo del mensaje JSON:
     ```json
     {
       "CodigoEstudiante": "1034986239",
       "CodigoAsignatura": "0001",
       "TipoActividad": "Final",
       "PesoActividad": 30.0,
       "Calificacion": 2.5,
       "Email": "estudiante@example.com"
     }
     ```

3. **Evaluación Automática**:
   - La función Lambda lee el mensaje de la cola SQS.
   - Si el peso de la actividad es mayor al 15% y la calificación es menor a 3.0 (considerada **reprobada**), se genera una **notificación automática**.
   - Las notificaciones se envían a un tópico SNS o por correo electrónico mediante SES.

---

## **Requisitos Previos**
- **AWS CLI configurado** con credenciales de usuario.
- **Python 3.x**.
- **Flask y boto3** como dependencias principales.
- **Cuenta de AWS** con acceso a **SQS**, **SNS**, y **Lambda**.

---

## **Instalación y Ejecución**

### **1. Clonar el Repositorio**
```bash
git clone https://github.com/tu-usuario/cloudbridge-flask-sqs.git
cd cloudbridge-flask-sqs
```

### **2. Configurar el Entorno Virtual**
```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

### **3. Instalar Dependencias**
```bash
pip install -r requirements.txt
```

### **4. Configurar la URL de la Cola SQS en `app.py`**
- Abre `app.py` y actualiza la variable `QUEUE_URL` con la URL de tu cola SQS creada en AWS.

---

## **Flujo Completo del Proyecto**

### **1. Envío de Notas a través del Formulario Flask**
- Los estudiantes ingresan su información en un **formulario web** creado con Flask.
- El formulario utiliza **Bootstrap** para hacerlo atractivo y fácil de usar.
- Los datos ingresados se envían a una **cola SQS** en formato JSON.

### **2. AWS SQS - Cola de Mensajes**
- **Amazon SQS** actúa como un buffer para almacenar las notas enviadas desde el formulario.
- Esto asegura que todos los datos ingresados se almacenen temporalmente y puedan ser procesados incluso si la infraestructura se encuentra ocupada.

### **3. Procesamiento con AWS Lambda**
- **AWS Lambda** se activa automáticamente cuando hay nuevos mensajes en la cola.
- Lee los datos del mensaje JSON y evalúa:
  - Si la **calificación** es menor a **3.0** y el **peso** de la actividad es mayor al 15%, considera la nota **reprobada**.
  - Si es reprobada, procede a enviar una notificación.

### **4. AWS SNS para Notificaciones**
- La función **Lambda** envía la notificación a un **tópico SNS** configurado con:
  - **Email de suscripción** para la administración o profesor.
  - **Notificación** de la actividad que fue reprobada.
- El tópico SNS permite una fácil **escalabilidad**, notificando a múltiples suscriptores al mismo tiempo.

### **5. AWS SES para Notificación Directa al Estudiante (Opcional)**
- También puede enviarse una notificación directa al **correo del estudiante** utilizando **Amazon SES**.
- Este correo incluye detalles como la calificación obtenida, el peso de la actividad y recomendaciones para mejorar.

---

## **Configuraciones de AWS**

### **1. Configuración de Amazon SQS**
- Crea una cola estándar:
  - **Nombre**: `notas-actividad`.
  - **URL**: Asegúrate de copiar la URL para integrarla en `app.py`.
  
### **2. Configuración de Amazon SNS**
- Crea un **tópico SNS** llamado `notas-actividad-advertencias`.
- Añade una suscripción al tópico:
  - **Protocolo**: `Email`.
  - **Endpoint**: El correo de la administración o profesor.
- **Confirma la suscripción** desde el correo recibido.

### **3. Configuración de AWS Lambda**
- **Lambda** se utiliza para procesar los mensajes de la cola.
- Conecta la Lambda a la cola SQS (`notas-actividad`) como desencadenador.
- Añade el siguiente **código de Lambda**:
  ```python
  import json
  import boto3

  sns = boto3.client('sns', region_name='us-east-1')
  TOPIC_ARN = 'arn:aws:sns:us-east-1:TU_ACCOUNT_ID:notas-actividad-advertencias'

  def lambda_handler(event, context):
      for record in event['Records']:
          mensaje = json.loads(record['body'])
          peso = mensaje['PesoActividad']
          calificacion = mensaje['Calificacion']
          email = mensaje['Email']

          if peso > 15 and calificacion < 3.0:
              enviar_notificacion(email, mensaje)

  def enviar_notificacion(email, mensaje):
      sns.publish(
          TopicArn=TOPIC_ARN,
          Subject="Advertencia sobre Actividad Reprobada",
          Message=f"Su actividad con calificación {mensaje['Calificacion']} y peso {mensaje['PesoActividad']}% está reprobada."
      )
  ```
- **Configuración de Permisos IAM**:
  - La Lambda necesita permisos para acceder a SQS, SNS y (opcionalmente) SES.

---

## **Ejecución del Proyecto**

### **1. Iniciar la Aplicación Flask**
```bash
python app.py
```

### **2. Acceso al Formulario**
- Abre `http://127.0.0.1:5000/` en tu navegador.
- Completa el formulario con los datos del estudiante y envíalos.

### **3. Procesamiento Automático**
- Los datos se envían a la **cola SQS** y luego son procesados por la **Lambda**.
- Si la calificación es reprobada, el estudiante, el profesor y/o la administración reciben una notificación.

---

## **Capturas de Pantalla**

### **Formulario de Ingreso**
![image](https://github.com/user-attachments/assets/9676642a-eb37-4fca-a095-cb7787ad19a6)

### **Notificación Exitosa**
![image](https://github.com/user-attachments/assets/901949d6-addb-4fb6-9367-763d31fc78c2)


---

## **Conclusiones**
Este proyecto muestra cómo integrar múltiples servicios de AWS para automatizar el manejo de notas académicas, generando notificaciones automáticas cuando se cumplen condiciones específicas. Es una demostración práctica del uso de **Flask** y **servicios en la nube** para construir aplicaciones robustas y escalables.

---
