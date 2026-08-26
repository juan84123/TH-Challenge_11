import socket
import threading
import time

import server


def crear_servidor_de_prueba():
    # Creo el socket del servidor igual que en server.py
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Puerto 0: el sistema operativo elige uno libre automaticamente
    servidor.bind(("127.0.0.1", 0))
    servidor.listen()
    # Pregunto cual puerto eligio
    puerto = servidor.getsockname()[1]
    return servidor, puerto


def conectar_cliente(puerto, nombre):
    # Creo un socket de cliente y me conecto al servidor de prueba
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect(("127.0.0.1", puerto))
    # Si recv() no recibe nada en 3 segundos, tira excepcion
    # en vez de colgarse para siempre
    cliente.settimeout(3)

    # El servidor pide el nombre, respondo con el nombre
    cliente.recv(1024)
    cliente.send(nombre.encode("utf-8"))

    # Espero la confirmacion del servidor
    cliente.recv(1024)

    return cliente


def test_mensaje_llega_a_los_demas_clientes():
    # Limpio el diccionario
    server.clientes_dict.clear()

    # Creo el servidor de prueba
    servidor, puerto = crear_servidor_de_prueba()

    # Lo lanzo en un hilo de background
    hilo = threading.Thread(target=server.coneccion_recibida, args=(servidor,))
    hilo.daemon = True
    hilo.start()

    # Le doy un instante para que quede escuchando
    time.sleep(0.1)

    # Conecto dos clientes reales
    cliente_juan = conectar_cliente(puerto, "Juan")
    cliente_majo = conectar_cliente(puerto, "Majo")

    # Descarto el aviso de bienvenida que le llega a Juan cuando Majo se conecta
    cliente_juan.recv(1024)

    # Juan manda un mensaje
    cliente_juan.send(b"Juan: hola")

    # Majo deberia recibirlo
    mensaje = cliente_majo.recv(1024)
    assert mensaje == b"Juan: hola"

def test_emisor_no_recibe_su_propio_mensaje():
    server.clientes_dict.clear()

    servidor, puerto = crear_servidor_de_prueba()

    hilo = threading.Thread(target=server.coneccion_recibida, args=(servidor,))
    hilo.daemon = True
    hilo.start()

    time.sleep(0.1)

    cliente_juan = conectar_cliente(puerto, "Juan")
    cliente_majo = conectar_cliente(puerto, "Majo")

    # Descarto el aviso de bienvenida de Majo
    cliente_juan.recv(1024)

    # Juan manda un mensaje
    cliente_juan.send(b"Juan: hola")

    # Majo lo recibe
    cliente_majo.recv(1024)

    # Juan no deberia recibir nada
    # settimeout(3) hace que si no llega nada en 3 segundos tire excepcion
    try:
        cliente_juan.recv(1024)
        # Si llega algo, el test falla
        assert False, "Juan recibio su propio mensaje"
    except TimeoutError:
        # Si hay timeout, es correcto — Juan no recibio nada
        pass

def test_servidor_sigue_funcionando_tras_desconexion():
    server.clientes_dict.clear()

    servidor, puerto = crear_servidor_de_prueba()

    hilo = threading.Thread(target=server.coneccion_recibida, args=(servidor,))
    hilo.daemon = True
    hilo.start()

    time.sleep(0.1)

    # Conecto tres clientes
    cliente_juan = conectar_cliente(puerto, "Juan")
    cliente_majo = conectar_cliente(puerto, "Majo")
    cliente_pedro = conectar_cliente(puerto, "Pedro")

    # Le doy tiempo al servidor para que envíe todos los avisos
    time.sleep(0.3)

    # Descarto todos los avisos pendientes de Juan en un solo recv
    cliente_juan.recv(4096)
    # Descarto el aviso de Pedro para Majo
    cliente_majo.recv(4096)

    # Majo se desconecta de golpe
    cliente_majo.close()
    time.sleep(0.2)

    # Descarto el aviso de desconexion de Majo
    cliente_juan.recv(4096)
    cliente_pedro.recv(4096)

    # Juan y Pedro deberian seguir funcionando
    cliente_juan.send(b"Juan: sigo aca")
    mensaje = cliente_pedro.recv(1024)
    assert b"Juan: sigo aca" in mensaje

    cliente_juan.close()
    cliente_pedro.close()
    servidor.close()
    server.clientes_dict.clear()