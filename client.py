import socket # Biblioteca para la comunicación por red (sockets).
import threading  # Biblioteca para manejar hilos (ejecutar tareas en paralelo).
import time

HOST = "127.0.0.1" 
PORT = 55555

def conectar_al_servidor():
    #Intenta conectar hasta que el servidor aparezca.
    # Bucle infinito hasta que se logre la conexión.
    while True:
        try:
            # Crea un objeto socket nuevo (IPv4, TCP) en cada intento.
            nuevo_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Intenta realizar el "Three-way Handshake" de TCP.
            nuevo_socket.connect((HOST, PORT))
            print("Conectado al servidor.")
            # Retorna el socket listo y sale de la función.
            return nuevo_socket
        except:
            # Si falla (server apagado), avisa y espera antes de reintentar.
            print("Servidor no encontrado. Reintentando en 3 segundos...")
            time.sleep(3)

def mensaje_recibido(client_socket, nombre):
    while True:
        try:
            # Se bloquea esperando recibir hasta 1024 bytes del servidor.
            data = client_socket.recv(1024)
            # Si el servidor cierra la conexión, data estará vacío.
            if not data:
                # Sale del bucle para cerrar este hilo.
                break
            # Traduce los bytes recibidos a texto.
            mensaje = data.decode("utf-8")
            if mensaje == "nombre":
                # Responde al protocolo inicial del servidor enviando el nombre.
                client_socket.send(nombre.encode("utf-8"))
            else:
                # \r mueve el cursor al inicio para no ensuciar el input del usuario.
                print(f"\r{mensaje}")
                # Redibuja el indicador "> " para que el usuario sepa que puede seguir escribiendo.
                print("> ", end="", flush=True)
        except:
            break
    
    print("\nConexión perdida. Presioná ENTER para intentar reconectar...")
    # Libera el socket del lado del cliente.
    client_socket.close()

# Pide el nombre una sola vez al iniciar el programa.
nombre_usuario = input("Cual es tu nombre: ")

# Bucle de vida superior: permite reconectar infinitamente.
while True:
    # Llama a la función que se queda intentando conectar.
    client = conectar_al_servidor()
    
    # Crea el hilo de escucha pasándole el socket actual y el nombre.
    """Hilo Principal: Maneja lo que VOS hacés (teclado).Está atrapado en el input()
        Hilo Secundario: Maneja lo que los DEMÁS hacen (red). Está atrapado en el recv()"""
    thread_escucha = threading.Thread(target=mensaje_recibido, args=(client, nombre_usuario))
    # El hilo morirá automáticamente si el programa principal se cierra.
    thread_escucha.daemon = True
    # Inicia el hilo de escucha en segundo plano.
    thread_escucha.start()

    # Bucle de escritura (Hilo Principal).
    while True:
        try:
            # Se queda bloqueado esperando que el usuario escriba algo.
            texto = input("") 

            # Si el servidor cayó, el hilo de escucha ya cerró el socket.
            # Al intentar enviar, esto dará error y saldrá al bucle de reconexión.
            mensaje_a_enviar = f"{nombre_usuario}: {texto}"
            client.send(mensaje_a_enviar.encode("utf-8"))
        except:
            # Si el envío falla, sale de este bucle interno para volver a 'conectar_al_servidor'.
            print("Reiniciando sistema de conexión...")
            break 
    # Asegura que el socket viejo esté bien cerrado antes de reiniciar.
    client.close()