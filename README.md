# Valorant Match Monitor 🎮
Este script en Python monitoriza en tiempo real tus partidas de Valorant. Se conecta al cliente local de Riot para obtener información de los jugadores en la fase de selección (Pre-Game) y durante la partida (Core-Game), consultando automáticamente el agente más utilizado (Main) de cada jugador mediante la API de HenrikDev.

# 🚀 Características
- Detección Automática: Encuentra el proceso de Valorant mediante el lockfile del sistema.
- Modo Pre-Game: Identifica a tus aliados antes de que empiece la partida.
- Modo Core-Game: Muestra información detallada de aliados y enemigos una vez dentro del mapa.
- Estadísticas de Agentes: Consulta el "Main" de cada jugador para anticipar estrategias.

# 🛠️ Requisitos previos
1. Python 3
2. Librerías necesarias urllib3
```pip install requests urllib3```
3. HenrikDev API Key: Necesitas una clave de API (puedes obtener una en el Discord de HenrikDev)

# ⚙️ Configuración y Uso
1. Configurar la API Key
Para que el script funcione, debes editar el archivo main.py (o como hayas nombrado al script) y buscar la línea donde se define la clave:
Busca esta línea y sustituye el valor por tu clave real
```HENRIK_API_KEY = "TU_API_KEY_AQUI"```
2. Ejecución
  1. Abre el cliente de Valorant
  2. Ejecuta el script
  3. El script entrará en modo espera hasta que el juego esté activo y detecte una partida

# ⚠️ Aviso Legal y Seguridad
Este proyecto se ha desarrollado con fines educativos y personales. Es importante destacar lo siguiente respecto a la seguridad de la cuenta:
- Uso de Vanguard: El script no es motivo de baneo por el sistema antitrampas Vanguard.
- Sin Modificaciones: A diferencia de los hacks o herramientas prohibidas, este script no edita, no modifica ni inyecta código en los archivos del juego ni en su memoria en tiempo real.
- Lectura de archivos locales: Su funcionamiento se basa únicamente en leer el archivo lockfile, un archivo de texto temporal que el cliente de Riot genera automáticamente al iniciarse para permitir la comunicación entre sus propios módulos.
- APIs Estándar: El script utiliza las mismas vías de comunicación que emplean aplicaciones de terceros populares (como trackers o gestores de inventario) para consultar estadísticas de forma externa.
- Usa este script bajo tu propia responsabilidad y siempre de manera justa para no entorpecer la experiencia de otros jugadores.
