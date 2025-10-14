import paramiko
import time
import threading

# --- Configuración ---
# Credenciales SSH para los puntos de acceso UniFi
USUARIO = "ubnt"
CONTRASENA = "ubnt"

# URL que probaste manualmente y funcionó
URL_FIRMWARE = "https://dl.ui.com/unifi/firmware/USMULTUSW16POE/7.2.120.16556/US.MULT.USW_16_POE_7.2.120+16556.250819.2354.bin"

# Nombre del archivo que contiene la lista de direcciones IP
ARCHIVO_IP = "ip_sw.txt"


def actualizar_unifi_ap(ip, usuario, contrasena, url_firmware):
    """
    Se conecta a un AP, envía el comando de actualización en segundo plano y se desconecta.
    Esta función está diseñada para ser ejecutada en un hilo separado por cada AP.
    """
    # El identificador del hilo actual ayuda a diferenciar la salida cuando se ejecutan en paralelo
    thread_name = threading.current_thread().name
    print(f"--- [Hilo: {thread_name}] Procesando {ip} ---")
    
    try:
        cliente_ssh = paramiko.SSHClient()
        cliente_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print(f"[{thread_name}] Conectando a {ip}...")
        cliente_ssh.connect(hostname=ip,
                            username=usuario,
                            password=contrasena,
                            timeout=30) 

        print(f"[{thread_name}] Conexión exitosa con {ip}. Enviando comando 'fire and forget'...")

        # --- Comando Robusto ---
        # Usamos syswrapper.sh que es el script real.
        # 'nohup' asegura que el proceso siga aunque cerremos sesión.
        # '> /dev/null 2>&1 &' envía toda la salida (normal y errores) a la "basura",
        # lo ejecuta en segundo plano y nos devuelve el control inmediatamente.
        comando_upgrade = f"nohup syswrapper.sh upgrade {url_firmware} > /dev/null 2>&1 &"
        
        # Ejecutamos el comando
        cliente_ssh.exec_command(comando_upgrade)
        
        print(f"[{thread_name}] Comando enviado a {ip}. El AP debería empezar a actualizarse por su cuenta.")
        # Damos un segundo para asegurar que el comando se ha procesado antes de cerrar
        time.sleep(2)

    except paramiko.AuthenticationException:
        print(f"!!!! [Hilo: {thread_name}] ERROR DE AUTENTICACIÓN en {ip}. Revisa las credenciales. !!!!")
    except Exception as e:
        print(f"!!!! [Hilo: {thread_name}] Ocurrió un error inesperado con {ip}: {e} !!!!")
    finally:
        # Cerramos la conexión nosotros mismos
        if 'cliente_ssh' in locals() and cliente_ssh.get_transport() and cliente_ssh.get_transport().is_active():
            cliente_ssh.close()
            print(f"[{thread_name}] Desconectado de {ip}.\n")


# --- Bloque Principal de Ejecución ---
if __name__ == "__main__":
    try:
        with open(ARCHIVO_IP, 'r') as f:
            direcciones_ip = [line.strip() for line in f if line.strip()]

        if not direcciones_ip:
            print(f"El archivo {ARCHIVO_IP} está vacío.")
        else:
            print(f"Iniciando proceso de actualización para {len(direcciones_ip)} APs en hilos paralelos.")
            
            hilos = [] # Lista para guardar los hilos
            
            # 1. Crear e iniciar un hilo por cada dirección IP
            for ip in direcciones_ip:
                # Creamos el hilo que ejecutará la función 'actualizar_unifi_ap'
                hilo = threading.Thread(target=actualizar_unifi_ap, args=(ip, USUARIO, CONTRASENA, URL_FIRMWARE))
                hilos.append(hilo)
                hilo.start() # Iniciamos el hilo

            # 2. Esperar a que todos los hilos terminen su ejecución
            for hilo in hilos:
                hilo.join() # El script principal espera aquí hasta que este hilo haya terminado

            print("="*40)
            print(">>> Proceso completado. Todos los comandos de actualización han sido enviados. <<<")
            print(">>> Por favor, espera 5-10 minutos y comprueba la versión de un AP manualmente. <<<")
            print("="*40)

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{ARCHIVO_IP}'.")