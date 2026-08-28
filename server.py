#permite manejar múltiples clientes al mismo tiempo (concurrencia).
import threading 

#permite crear comunicación entre computadoras (cliente-servidor).
import socket  

#localhost: Dirección de loopback que permite que la comunicación no salga de mi propia tarjeta de red
HOST = "127.0.0.1" 
PORT = 55555
#Diccionario { socket: nombre }
#La clave es un objeto de la clase socket
clientes_dict = {}
    
#Este objeto es un paquete que contiene:
#Atributos (Datos): El fd (File Descriptor), la IP del cliente, el puerto que está usando, 
#el protocolo (TCP), etc.
#Métodos (Funciones): Las capacidades de ese objeto, como .send(), .recv() o .close()."""


def broadcast(mensaje, cliente_actual):
    #list(clientes_dict) hace una copia de las claves en ese momento. 
    #El for recorre esa copia, así aunque el diccionario cambie en el medio, no explota
    for cliente_socket in list(clientes_dict):
        if cliente_socket != cliente_actual: #para cuando se envie el mensaje, no se envie tambien al cliente que envio el mensaje
            try:
                cliente_socket.send(mensaje)
            except:
                # Limpieza directa sin llamar a cliente_desconectado
                # para evitar recursion infinita
                if cliente_socket in clientes_dict:
                    del clientes_dict[cliente_socket]
                cliente_socket.close()
            

def cliente_desconectado(cliente_socket):
    if cliente_socket in clientes_dict:
        nombre_cliente = clientes_dict[cliente_socket]
        # Avisamos a los demás
        #Usamos UTF-8 porque es el estándar universal de codificación. Nos permite manejar caracteres especiales, 
        #acentos y símbolos de cualquier idioma, asegurando que los bytes que viajan por el socket se traduzcan 
        #correctamente en cualquier computadora, sin importar su configuración regional.
        mensaje_desconexion = f"Server: {nombre_cliente} se ha desconectado".encode('utf-8')
        broadcast(mensaje_desconexion, cliente_socket)
        # Verificamos de nuevo antes de borrar porque otro hilo
        # pudo haberlo borrado entre el if de arriba y esta linea
        if cliente_socket in clientes_dict:
            # Se borra el usuario del diccionario
            del clientes_dict[cliente_socket]
        # Cierra la conexión
        cliente_socket.close()        
        print(f"{nombre_cliente} se ha deconectado")

def mensaje_valido(mensaje):
    # Decodifico y saco espacios, si no queda nada el mensaje no sirve
    texto = mensaje.decode("utf-8")
    if texto.strip() == "":
        return False
    return True


def handle_message(cliente): #espera el mensaje del cliente
    while True:
        try:
            mensaje = cliente.recv(1024)
            if mensaje == b"":
                cliente_desconectado(cliente)
                break
            if not mensaje_valido(mensaje):
                continue
            broadcast(mensaje, cliente)
        except:
            cliente_desconectado(cliente)
            break

def coneccion_recibida(server): #espera la coneccion del clinte y crea el thread
    while True:
        try:
            #Retorna una tupla (cliente_socket (socket del cliente), address(IP y puerto del cliente)), 
            #cliente_socket es un nuevo objeto socket, se genera el Three-way Handshake
            # Recibe el servidor como parametro en vez de usar la variable global
            # para que los tests puedan pasarle su propio servidor de prueba
            cliente_socket, address = server.accept()

            # Protocolo de nombre
            cliente_socket.send("nombre".encode("utf-8"))
            nombre_cliente = cliente_socket.recv(1024).decode("utf-8")

            # Se guarda en el diccionario
            clientes_dict[cliente_socket] = nombre_cliente

            print(f"{nombre_cliente} se ha conectado...{address}")

            mensaje = f"Server: {nombre_cliente} se ha unido al chat!".encode("utf-8")
            broadcast(mensaje, cliente_socket)

            cliente_socket.send("Te conectaste al servidor".encode("utf-8"))

            #Crea el hilo, hilo de ejecución independiente para cada cliente, 
            # target dice cual es la funcion que se va a crear por cada usuario y 
            # args es argumentos que necesita la funcion
            thread = threading.Thread(target=handle_message, args=(cliente_socket,)) 
            # Si el servidor se apaga, los hilos de clientes mueren
            thread.daemon = True
            #Inicia el hilo
            thread.start()
        #OSError es la clase base de todos los errores de red y sockets en Python
        except OSError:
            # El servidor fue cerrado, terminamos el loop limpiamente
            break

# Movemos el arranque del servidor a este bloque para que sea "importable".
# Cuando Python ejecuta un archivo directamente, __name__ vale "__main__".
# Cuando otro archivo lo importa (como los tests), __name__ vale "server".
# Sin este bloque, importar server.py abria un socket real y llamaba a
# coneccion_recibida() que es un loop infinito, colgando pytest para siempre.
# Asi, los tests pueden hacer "import server" y acceder a las funciones
# sin que se ejecute nada de red.
if __name__ == "__main__":
    #Definimos la familia de direcciones (IPv4) y el tipo de socket (TCP).
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #server.setsockopt(...): Significa "Set Socket Option" (Configurar opción del socket). 
    #Es para cambiar las reglas de juego de ese socket específico.
    #socket.SOL_SOCKET: Le dice a Python que la configuración que vamos a cambiar es a nivel de 
    #Socket general (no algo específico de un protocolo raro).
    #socket.SO_REUSEADDR: Esta es la clave. Significa "Socket Option: Reuse Address" 
    #(Reutilizar dirección). Le da permiso al servidor para "robarle" el puerto al sistema 
    #operativo aunque este crea que todavía está ocupado por una conexión anterior.
    #1: Es un valor booleano (True). Significa "activar esta opción".
    #Permite reutilizar el puerto aunque esté en estado TIME_WAIT.
    #cuando reinicias el servidor rápido.
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #Asocia el socket a una interfaz de red específica (localhost) y un puerto.
    server.bind((HOST, PORT))
    #Pone el socket en modo escucha
    server.listen()
    print(f"Server running on {HOST}:{PORT}")
    coneccion_recibida(server)
