import socket #permite crear comunicación entre computadoras (cliente-servidor).
import threading #permite manejar múltiples clientes al mismo tiempo (concurrencia).

#localhost: Dirección de loopback que permite que la comunicación no salga de mi propia tarjeta de red
HOST = "127.0.0.1" 
PORT = 55555

#Definimos la familia de direcciones (IPv4) y el tipo de socket (TCP).
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

"""server.setsockopt(...): Significa "Set Socket Option" (Configurar opción del socket). 
Es para cambiar las reglas de juego de ese socket específico.

socket.SOL_SOCKET: Le dice a Python que la configuración que vamos a cambiar es a nivel de Socket general (no algo específico de un protocolo raro).

socket.SO_REUSEADDR: Esta es la clave. Significa "Socket Option: Reuse Address" (Reutilizar dirección). Le da permiso al servidor para "robarle" el puerto al sistema operativo aunque este crea que todavía está ocupado por una conexión anterior.

1: Es un valor booleano (True). Significa "activar esta opción"."""
#Permite reutilizar el puerto aunque esté en estado TIME_WAIT.
#cuando reinicias el servidor rápido.
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#Asocia el socket a una interfaz de red específica (localhost) y un puerto.
server.bind((HOST,PORT))
#Pone el socket en modo escucha
server.listen()
print(f"Server running on {HOST}:{PORT}")

# Diccionario { socket: nombre }
# La clave es un objeto de la clase socket
"""Este objeto es un paquete que contiene:
Atributos (Datos): El fd (File Descriptor), la IP del cliente, el puerto que está usando, el protocolo (TCP), etc.
Métodos (Funciones): Las capacidades de ese objeto, como .send(), .recv() o .close()."""
clientes_dict = {}

def broadcast(mensaje, cliente_actual):
    for cliente_socket in clientes_dict:
        if cliente_socket != cliente_actual: #para cuando se envie el mensaje, no se envie tambien al cliente que envio el mensaje
            try:
                cliente_socket.send(mensaje)
            except:
                # Si falla, aprovechamos para limpiar
                cliente_desconectado(cliente_socket)
            

def cliente_desconectado(cliente_socket):
    if cliente_socket in clientes_dict:
        nombre_cliente = clientes_dict[cliente_socket]

        # Avisamos a los demás
        """"Usamos UTF-8 porque es el estándar universal de codificación. Nos permite manejar caracteres especiales, 
            acentos y símbolos de cualquier idioma, asegurando que los bytes que viajan por el socket se traduzcan 
            correctamente en cualquier computadora, sin importar su configuración regional."""""
        mensaje_desconexion = f"Server: {nombre_cliente} se ha desconectado".encode('utf-8')
        broadcast(mensaje_desconexion, cliente_socket)

        # Se borra el usuario del diccionario
        del clientes_dict[cliente_socket]
        # Cierra la conexión
        cliente_socket.close()        
        print(f"{nombre_cliente} se ha deconectado")

def handle_message(cliente): #espera el mensaje del cliente
    while True:
        try:
            mensaje = cliente.recv(1024) # bytes del mensaje, tamaño de buffer estandar
            broadcast(mensaje, cliente)
        except:
            cliente_desconectado(cliente)
            break

def coneccion_recibida(): #espera la coneccion del clinte y crea el thread
    while True:
        #Retorna una tupla (cliente_socket (socket del cliente), address(IP y puerto del cliente)), 
        # cliente_socket es un nuevo objeto socket, se genera el Three-way Handshake
        cliente_socket, addres = server.accept()

        # Protocolo de nombre
        cliente_socket.send("nombre".encode("utf-8"))
        nombre_cliente = cliente_socket.recv(1024).decode("utf-8")

        # Se guarda en el diccionario
        clientes_dict[cliente_socket] = nombre_cliente

        print(f"{nombre_cliente} se ha conectado...{addres}")

        mensaje = f"Server: {nombre_cliente} se ha unido al chat!".encode("utf-8")
        broadcast(mensaje, cliente_socket)

        cliente_socket.send("Te conectaste al servidor". encode("utf-8"))

        #Crea el hilo, hilo de ejecución independiente para cada cliente, 
        # target dice cual es la funcion que se va a crear por cada usuario y 
        # args es argumentos que necesita la funcion
        thread = threading.Thread(target=handle_message, args=(cliente_socket,)) 
        # Si el servidor se apaga, los hilos de clientes mueren
        thread.daemon = True
        #Inicia el hilo
        thread.start()

coneccion_recibida()

