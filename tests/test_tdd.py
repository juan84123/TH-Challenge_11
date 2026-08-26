import server


def test_mensaje_valido_rechaza_vacio():
    # Un mensaje vacio no deberia ser valido
    assert server.mensaje_valido(b"") is False


def test_mensaje_valido_rechaza_solo_espacios():
    # Espacios solos tampoco son validos
    assert server.mensaje_valido(b"   ") is False


def test_mensaje_valido_acepta_texto_normal():
    # Un mensaje con contenido real si es valido
    assert server.mensaje_valido(b"Juan: hola") is True


def test_mensaje_valido_acepta_texto_con_espacios_alrededor():
    # Espacios de mas alrededor de un mensaje real no lo invalidan
    assert server.mensaje_valido(b"  hola  ") is True