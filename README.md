EbalQuiz

EbalQuiz es una aplicación web construida con Streamlit que permite a los usuarios autenticarse, cargar documentos PDF y realizar preguntas sobre su contenido utilizando un sistema RAG (Retrieval-Augmented Generation) combinado con un modelo VLM (Vision Language Model, GPT-4 Vision).

Tabla de Contenidos:

Arquitectura General
Instalación y Configuración
Flujo de Autenticación y Registro
Flujo de Procesamiento de PDFs y Consulta
Estructura de Archivos
Variables de Entorno
Notas de Seguridad y Escalabilidad

//Arquitectura General//

El sistema sigue este flujo:

Autenticación de usuario:
Registro y login mediante email, código de verificación y contraseña.
Envío de código de verificación por email usando SMTP.
Carga y procesamiento de PDFs:
El usuario sube uno o varios PDFs.
El sistema extrae el texto de cada página y lo indexa usando embeddings (OpenAI + FAISS).
Consulta y respuesta:
El usuario realiza preguntas en una interfaz tipo chat.
El sistema busca la página más relevante usando RAG.
Convierte la página relevante en imagen y la envía, junto con la pregunta, a GPT-4 Vision (VLM).
Muestra la respuesta y la imagen de la página relevante en formato de chat.

Instalación y Configuración


//Instala las dependencias//

pip install -r requirements.txt

2. Configura las variables de entorno

Crea un archivo .env en la raíz del proyecto con el siguiente contenido (ajusta los valores):
Apply to .env

OPENAI_API_KEY=tu_clave_openai
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_mail@gmail.com
SMTP_PASS=tu_contraseña_de_aplicacion
SMTP_FROM=tu_mail@gmail.com

> Para Gmail, debes crear una “contraseña de aplicación” (ver instrucciones en el README).

3. Ejecuta la aplicación

streamlit run app.py

//Flujo de Autenticación y Registro//

a_Registro de usuario

El usuario elige “Registrarse”, ingresa su email y solicita un código de verificación.
El sistema envía un código de 6 dígitos al email proporcionado.
El usuario ingresa el código recibido y define su contraseña.
El usuario ya puede iniciar sesión con su email y contraseña.

b_Login

El usuario ingresa su email y contraseña.
Si las credenciales son correctas, accede a la app.

c_Gestión de usuarios

Los usuarios se almacenan en el archivo users.json con el email y la contraseña hasheada (SHA-256).
El sistema es modular y puede migrar fácilmente a una base de datos real si se requiere.

//Flujo de Procesamiento de PDFs y Consulta//

Carga de PDFs
El usuario sube uno o varios archivos PDF desde la interfaz.
Extracción y Embedding
El sistema extrae el texto de cada página usando PyMuPDF.
Cada página se convierte en un documento con metadatos (número de página, nombre de archivo).
Se generan embeddings de cada página usando OpenAI y se indexan en FAISS.
Consulta (RAG + VLM)
El usuario escribe una pregunta en la interfaz de chat.
El sistema busca la página más relevante usando FAISS (RAG).
Convierte la página relevante en imagen PNG.
Envía la imagen y la pregunta a GPT-4 Vision (VLM) usando la API de OpenAI.
El modelo responde basándose en la imagen y el texto de la pregunta.
La respuesta y la imagen se muestran en la interfaz tipo chat.

//Estructura de Archivos//

├── app.py                # Interfaz principal Streamlit y lógica de chat
├── backend.py            # Extracción de texto, embeddings y retrieval
├── vision_api.py         # Renderizado de página como imagen y consulta a VLM
├── login.py              # Registro, login y gestión de usuarios
├── email_utils.py        # Envío de emails vía SMTP
├── users.json            # Base de datos de usuarios (email + hash de contraseña)
├── requirements.txt      # Dependencias del proyecto
├── .env                  # Variables de entorno (no subir al repo)
├── 1673777935481.jpg     # Logo de la empresa
└── chest_xray_medical_students.pdf # PDF de ejemplo

//Variables de Entorno//

OPENAI_API_KEY: Tu clave de OpenAI para embeddings y GPT-4 Vision.

SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM: Configuración SMTP para el envío de correos automáticos.

//Notas de Seguridad y Escalabilidad//

Las contraseñas de los usuarios se almacenan hasheadas (SHA-256) en users.json.
El sistema de emails es modular y puede adaptarse a cualquier proveedor SMTP.
El almacenamiento de usuarios puede migrarse fácilmente a una base de datos real.
El sistema es compatible con cualquier PDF y pregunta, no solo documentos médicos.
El prompt del VLM es genérico y puede adaptarse a otros dominios.
Créditos
Desarrollado por EBAL para soluciones de RAG + VLM en análisis documental.

----------------------------------------------------------------------------

Para cuando utilicemos un mail en producción que envíe el token para la creación de cuentas (users) :

Cómo generar una “contraseña de aplicación” en Gmail
Para que el sistema pueda enviar correos automáticos desde una cuenta de Gmail (por ejemplo, para producción), debes crear una contraseña de aplicación siguiendo estos pasos:

Activa la verificación en dos pasos (2FA) en la cuenta de Gmail
Ve a: https://myaccount.google.com/security
Activa “Verificación en dos pasos”.

Accede a la página de contraseñas de aplicación
Ve a: https://myaccount.google.com/apppasswords

Crea una nueva contraseña de aplicación
En “Seleccionar la aplicación”, elige “Correo”.
En “Seleccionar el dispositivo”, elige “Otro (nombre personalizado)” y escribe, por ejemplo, EbalQuiz.
Haz clic en “Generar”.
Google te mostrará una contraseña de 16 caracteres.

Cópiala y pégala en el archivo .env como SMTP_PASS.

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_cuenta@gmail.com
SMTP_PASS=la_contraseña_de_aplicacion_generada
SMTP_FROM=tu_cuenta@gmail.com
