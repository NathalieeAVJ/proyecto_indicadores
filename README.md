Sistema de Gestión de Incidencias

Autor: Nathaliee Vargas Nathalex000@gmail.com

Este proyecto es una solución integral para la gestión y seguimiento de incidencias de líneas telefónicas, diseñado para optimizar los tiempos de respuesta y organizar el flujo de trabajo técnico.

🚀 Tecnologías Utilizadas
Backend: Django (Python) - REST API.

Frontend: Vue.js con Vuetify (Material Design Components).

Base de Datos: PostgreSQL / SQLite.

Herramientas: Debian 12 (Entorno de desarrollo), Git.

✨ Características Principales
Panel de Control (Dashboard): Visualización de métricas de incidencias en tiempo real.

Gestión de Tickets: Registro, asignación y seguimiento de estados de fallas en líneas.

Interfaz Responsiva: Diseñada con Vuetify para una experiencia fluida en cualquier dispositivo.

Autenticación y Roles: Manejo de usuarios según niveles de acceso.

🛠️ Instalación y Configuración
Prerrequisitos: Python 3.x, Node.js y npm.

Clonar el repositorio:

Bash
git clone https://github.com/tu-usuario/tu-repositorio.git
cd tu-repositorio
Configuración del Backend (Django):

Bash
cd backend
python -m venv venv
source venv/bin/activate # En Linux/Debian
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
Configuración del Frontend (Vue.js):

Bash
cd frontend
npm install
npm run serve
