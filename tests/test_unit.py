from unittest.mock import Mock
import server

def test_broadcast_envia_a_todos_menos_al_emisor():
    # Limpiamos el diccionario antes de empezar
    server.clientes_dict.clear()

    # Creamos dos sockets falsos
    socket_juan = Mock()
    socket_majo = Mock()

    # Los registramos en el diccionario como si estuvieran conectados
    server.clientes_dict[socket_juan] = "Juan"
    server.clientes_dict[socket_majo] = "Majo"

    # Juan manda un mensaje
    server.broadcast(b"hola", socket_juan)

    # Verificamos que Majo lo recibió
    socket_majo.send.assert_called_once_with(b"hola")

    # Se corrobora que no se le llame al socket
    # AssertionError si es llamado, metodo de Mock()
    socket_juan.send.assert_not_called()

    # Limpiamos después del test
    server.clientes_dict.clear()


def test_broadcast_no_envia_nada_si_solo_hay_un_cliente():
    # Limpio el diccionario
    server.clientes_dict.clear()

    # Solo hay un cliente conectado
    socket_juan = Mock()
    server.clientes_dict[socket_juan] = "Juan"

    # Juan manda un mensaje
    server.broadcast(b"hola", socket_juan)

    # Se corrobora que no se le llame al socket
    socket_juan.send.assert_not_called()

    # Limpio
    server.clientes_dict.clear()

# Error de en brodcast por intentar borrar cosas del dicciones mientras se recorria
def test_broadcast_limpia_cliente_si_el_envio_falla():
    # Limpio el diccionario
    server.clientes_dict.clear()

    socket_juan = Mock()
    socket_roto = Mock()

    # Hago que el send de socket_roto tire una excepcion
    # como si ese cliente se hubiera desconectado
    # Es la forma de simular que el cliente se cayó
    # cuando un cliente se desconecta y el servidor intenta mandarle algo, 
    # el sistema operativo tira un OSError
    # simular que el socket envio esto
    socket_roto.send.side_effect = OSError("conexion perdida")

    server.clientes_dict[socket_juan] = "Juan"
    server.clientes_dict[socket_roto] = "Roto"

    # Juan manda un mensaje
    server.broadcast(b"hola", socket_juan)

    # Corroboramos que el socket fue eliminado
    assert socket_roto not in server.clientes_dict

    # Limpio
    server.clientes_dict.clear()

def test_cliente_desconectado_lo_saca_del_diccionario():
    server.clientes_dict.clear()

    socket_juan = Mock()
    server.clientes_dict[socket_juan] = "Juan"

    server.cliente_desconectado(socket_juan)

    # Corroboramos que el socket fue eliminado
    assert socket_juan not in server.clientes_dict

    server.clientes_dict.clear()


def test_cliente_desconectado_avisa_a_los_demas():
    server.clientes_dict.clear()

    socket_juan = Mock()
    socket_majo = Mock()
    server.clientes_dict[socket_juan] = "Juan"
    server.clientes_dict[socket_majo] = "Majo"

    server.cliente_desconectado(socket_juan)

    # Corrobora si el socket fue llamado 1 vez con un mensaje en especifico
    socket_majo.send.assert_called_once_with(
        "Server: Juan se ha desconectado".encode("utf-8")
    )

    server.clientes_dict.clear()


def test_cliente_desconectado_cierra_el_socket():
    server.clientes_dict.clear()

    socket_juan = Mock()
    server.clientes_dict[socket_juan] = "Juan"

    server.cliente_desconectado(socket_juan)

    # Se corrobora si fue llamado 1 vez
    socket_juan.close.assert_called_once()

    server.clientes_dict.clear()


def test_handle_message_reenvia_el_mensaje_recibido():
    server.clientes_dict.clear()

    socket_juan = Mock()
    socket_majo = Mock()
    server.clientes_dict[socket_juan] = "Juan"
    server.clientes_dict[socket_majo] = "Majo"

    # Sin el OSError al final el loop nunca terminaría 
    # recv() seguiría devolviendo valores indefinidamente y el test se colgaría
    # es recv porque es lo que escucha que juan escriba algo
    socket_juan.recv.side_effect = [b"Juan: hola", OSError("cortado")]

    server.handle_message(socket_juan)

    # si alguna vez se llamo a ese socket con un mensaje en especifico
    socket_majo.send.assert_any_call(b"Juan: hola")

    server.clientes_dict.clear()


def test_handle_message_desconecta_si_recv_falla():
    server.clientes_dict.clear()

    socket_juan = Mock()
    server.clientes_dict[socket_juan] = "Juan"

    # recv() falla desde el primer intento — simula que el cliente se cayo antes de mandar nada
    socket_juan.recv.side_effect = OSError("cortado")

    server.handle_message(socket_juan)

    # Corroboramos que el socket fue eliminado
    assert socket_juan not in server.clientes_dict

    server.clientes_dict.clear()