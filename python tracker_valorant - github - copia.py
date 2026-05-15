import os
import base64
import requests
import urllib3
import time
from collections import Counter
import traceback
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

REGION = "eu"
SHARD = "eu"
HENRIK_API_KEY = "pega entre estas comillas tu clave API"

CLIENT_PLATFORM = "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIkludGVsIg0KfQ=="

def obtener_version_cliente():
    try:
        res = requests.get("https://valorant-api.com/v1/version", timeout=5)
        return res.json()['data']['riotClientVersion']
    except:
        return "release-08.04-shipping-9-234567"

def obtener_agente_mas_usado(riot_id):
    try:
        nombre, tag = riot_id.split('#')
    except ValueError:
        return "ID inválido"

    url_henrik = f"https://api.henrikdev.xyz/valorant/v3/matches/{REGION}/{nombre}/{tag}"
    headers = {"Authorization": HENRIK_API_KEY}
    
    try:
        res = requests.get(url_henrik, headers=headers, timeout=5)
        if res.status_code == 200:
            agentes = []
            for partida in res.json().get('data', []):
                jugadores = partida.get('players', {}).get('all_players', [])
                for jugador in jugadores:
                    if jugador.get('name', '').lower() == nombre.lower() and jugador.get('tag', '').lower() == tag.lower():
                        agente = jugador.get('character')
                        if agente:
                            agentes.append(agente)
                        break 
            if agentes:
                return Counter(agentes).most_common(1)[0][0]
    except Exception:
        pass 
    return "Desconocido"

def imprimir_datos(nombres_aliados, bando, nombres_enemigos=None):
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    salida = f"\n==================================================\n"
    salida += f" PARTIDA ENCONTRADA - {fecha_actual}\n"
    salida += f" TU LADO: {bando.upper()}\n"
    salida += f"==================================================\n"
    
    salida += f" --- TU EQUIPO ---\n"
    for jugador in nombres_aliados:
        nombre_completo = f"{jugador['GameName']}#{jugador['TagLine']}"
        main = obtener_agente_mas_usado(nombre_completo)
        salida += f"> {nombre_completo.ljust(25)} | Main: {main}\n"
        
    if nombres_enemigos:
        salida += f"\n --- EQUIPO ENEMIGO ---\n"
        for jugador in nombres_enemigos:
            nombre_completo = f"{jugador['GameName']}#{jugador['TagLine']}"
            main = obtener_agente_mas_usado(nombre_completo)
            salida += f"> {nombre_completo.ljust(25)} | Main: {main}\n"
            
    salida += f"=================================================="
    
    print(salida)

def monitorizar_partida():
    print("[*] Buscando Valorant...")
    ruta_lock = os.path.expandvars(r"%LOCALAPPDATA%\Riot Games\Riot Client\Config\lockfile")
    
    while not os.path.exists(ruta_lock):
        time.sleep(3)
        
    with open(ruta_lock, 'r') as f:
        datos = f.read().split(':')
        puerto, password = datos[2], datos[3]

    base_url = f"https://127.0.0.1:{puerto}"
    auth = base64.b64encode(f"riot:{password}".encode()).decode()
    headers_locales = {"Authorization": f"Basic {auth}"}

    client_version = obtener_version_cliente()

    try:
        tokens = requests.get(f"{base_url}/entitlements/v1/token", headers=headers_locales, verify=False).json()
        sesion = requests.get(f"{base_url}/chat/v1/session", headers=headers_locales, verify=False).json()
        
        mi_puuid = sesion['puuid']
        headers_remotos = {
            "Authorization": f"Bearer {tokens['accessToken']}",
            "X-Riot-Entitlements-JWT": tokens['token'],
            "X-Riot-ClientVersion": client_version,
            "X-Riot-ClientPlatform": CLIENT_PLATFORM,
            "Content-Type": "application/json"
        }
        print(f"[+] Conectado y monitorizando...")
    except Exception as e:
        print(f"[!] Error de conexión local: {e}")
        return

    url_pregame = f"https://glz-{REGION}-1.{SHARD}.a.pvp.net/pregame/v1/players/{mi_puuid}"
    url_coregame = f"https://glz-{REGION}-1.{SHARD}.a.pvp.net/core-game/v1/players/{mi_puuid}"
    url_nombres = f"https://pd.{SHARD}.a.pvp.net/name-service/v2/players"

    while True:
        # Pre-Game (Solo Aliados)
        res_pre = requests.get(url_pregame, headers=headers_remotos)
        if res_pre.status_code == 200 and res_pre.json().get('MatchID'):
            match_id = res_pre.json()['MatchID']
            match_info = requests.get(f"https://glz-{REGION}-1.{SHARD}.a.pvp.net/pregame/v1/matches/{match_id}", headers=headers_remotos).json()
            
            equipo = match_info.get('AllyTeam', {})
            bando = "Defensa" if "Blue" in equipo.get('TeamID', '') else "Ataque"
            puuids_aliados = [j['Subject'] for j in equipo.get('Players', [])]
            
            nombres_aliados = requests.put(url_nombres, headers=headers_remotos, json=puuids_aliados).json()
            imprimir_datos(nombres_aliados, bando)

            while requests.get(url_pregame, headers=headers_remotos).status_code == 200:
                time.sleep(5)

        # Core-Game (Aliados y Enemigos)
        res_core = requests.get(url_coregame, headers=headers_remotos)
        if res_core.status_code == 200 and res_core.json().get('MatchID'):
            match_id = res_core.json()['MatchID']
            match_info = requests.get(f"https://glz-{REGION}-1.{SHARD}.a.pvp.net/core-game/v1/matches/{match_id}", headers=headers_remotos).json()
            
            mi_equipo_id = next((p['TeamID'] for p in match_info['Players'] if p['Subject'] == mi_puuid), "Blue")
            bando = "Defensa" if mi_equipo_id == "Blue" else "Ataque"
            
            puuids_aliados = [p['Subject'] for p in match_info['Players'] if p['TeamID'] == mi_equipo_id]
            puuids_enemigos = [p['Subject'] for p in match_info['Players'] if p['TeamID'] != mi_equipo_id]

            nombres_aliados = requests.put(url_nombres, headers=headers_remotos, json=puuids_aliados).json()
            nombres_enemigos = requests.put(url_nombres, headers=headers_remotos, json=puuids_enemigos).json()
            
            imprimir_datos(nombres_aliados, bando, nombres_enemigos)

            while requests.get(url_coregame, headers=headers_remotos).status_code == 200:
                time.sleep(10)

        time.sleep(3)

if __name__ == "__main__":
    print("=" * 60)
    print("   Script by pabloinfo1 // Creado con ayuda de Gemini")
    print("=" * 60 + "\n")
    
    try:
        monitorizar_partida()
    except Exception as e:
        print("\n[!!!] EL SCRIPT HA CRASHEADO. DETALLE DEL ERROR:")
        print("-" * 50)
        traceback.print_exc()
        print("-" * 50)
    
    input("\nPresiona ENTER para cerrar la ventana...")