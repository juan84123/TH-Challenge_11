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

    # Verificamos que Juan NO se lo mandó a sí mismo
    socket_juan.send.assert_not_called()

    # Limpiamos después del test
    server.clientes_dict.clear()