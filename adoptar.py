import paramiko
import time
import threading

# --- Configuración ---
# Credenciales SSH para los puntos de acceso UniFi
USUARIO = "ubnt"
CONTRASENA = "ubnt"

# --- URL DE INFORM ---
# La dirección de tu nuevo controlador
URL_INFORM = ""

# Nombre del archivo que contiene la lista de direcciones IP
ARCHIVO_IP = "ip_sw.txt"


def cambiar_inform_url(ip, usuario, contrasena, url_inform):
    """
    Se conecta a un AP, envía el comando 'set-inform' en segundo plano y se desconecta.
    Esta función está diseñada para ser ejecutada en un hilo separado por cada AP.
    """
    # El identificador del hilo actual ayuda a diferenciar la salida
    thread_name = threading.current_thread().name
    print(f"--- [Hilo: {thread_name}] Procesando {ip} ---")
    
    try:
        cliente_ssh = paramiko.SSHClient()
        # Acepta automáticamente el fingerprint del host la primera vez
        cliente_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print(f"[{thread_name}] Conectando a {ip}...")
        cliente_ssh.connect(hostname=ip,
                            username=usuario,
                            password=contrasena,
                            timeout=30) 

        print(f"[{thread_name}] Conexión exitosa con {ip}. Enviando comando 'set-inform'...")

        # --- COMANDO MODIFICADO ---
        # Usamos el comando 'set-inform' con la nueva URL.
        # Lo ejecutamos en segundo plano para asegurar que se complete.
        comando_set_inform = f"syswrapper.sh set-inform {url_inform} > /dev/null 2>&1 &"

        # Ejecutamos el comando
        cliente_ssh.exec_command(comando_set_inform)
        
        print(f"[{thread_name}] Comando enviado a {ip}. El AP ahora apuntará al nuevo controlador.")
        time.sleep(2) # Pausa breve para asegurar que el comando se procese

    except paramiko.AuthenticationException:
        print(f"!!!! [Hilo: {thread_name}] ERROR DE AUTENTICACIÓN en {ip}. Revisa las credenciales. !!!!")
    except Exception as e:
        print(f"!!!! [Hilo: {thread_name}] Ocurrió un error inesperado con {ip}: {e} !!!!")
    finally:
        # Nos aseguramos de cerrar la conexión
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
            print(f"Iniciando proceso de cambio de URL de inform para {len(direcciones_ip)} APs en paralelo.")
            
            hilos = [] # Lista para guardar los hilos que creemos

            # 1. Crear e iniciar un hilo por cada dirección IP
            for ip in direcciones_ip:
                # Creamos el objeto Hilo
                hilo = threading.Thread(target=cambiar_inform_url, args=(ip, USUARIO, CONTRASENA, URL_INFORM))
                hilos.append(hilo)
                # Iniciamos la ejecución de la función en un hilo separado
                hilo.start()

            # 2. Esperar a que todos los hilos terminen su ejecución
            for hilo in hilos:
                # El método .join() bloquea el script principal hasta que el hilo haya terminado
                hilo.join()

            print("="*40)
            print(">>> Proceso completado. Todos los APs han recibido la nueva URL. <<<")
            print(">>> Revisa tu nuevo controlador para adoptar los dispositivos. <<<")
            print("="*40)

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{ARCHIVO_IP}'.")