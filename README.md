# Sock-it-to-me Chat

Chat por terminal usando sockets TCP en Python. Sin librerías externas para el manejo de red, solo `socket` y `threading` de la librería estándar.

## Qué hace

Un servidor acepta conexiones de varios clientes al mismo tiempo y reenvía cada mensaje que llega a todos los demás conectados (broadcast). Cada cliente que se conecta corre en su propio hilo del lado del servidor, así uno no bloquea a los demás.

Del lado del cliente hay dos hilos: uno escuchando lo que llega del servidor y otro esperando que el usuario escriba, para poder mandar y recibir mensajes sin que uno tape al otro.

## Cómo está armado

**server.py**

- Al arrancar, crea el socket, hace `bind` en `127.0.0.1:55555` y se pone a escuchar.
- `clientes_dict` es un diccionario `{socket: nombre}` que guarda quién está conectado. Es la única fuente de verdad sobre los clientes activos.
- `coneccion_recibida()` es el loop principal: por cada conexión nueva pide el nombre del cliente, lo guarda en el diccionario y lanza un hilo (`handle_message`) dedicado a ese cliente.
- `broadcast(mensaje, cliente_actual)` recorre el diccionario y le manda el mensaje a todos menos al que lo escribió.
- `cliente_desconectado(cliente_socket)` se encarga de sacar al cliente del diccionario, cerrar su socket y avisarle al resto que se fue.

**client.py**

- `conectar_al_servidor()` intenta conectar y, si el servidor no está arriba, reintenta cada 3 segundos.
- `mensaje_recibido()` corre en un hilo aparte y se queda escuchando lo que manda el servidor.
- El hilo principal se queda en un loop leyendo `input()` y mandando lo que el usuario escribe.
- Hay un protocolo mínimo al conectar: el servidor manda el string `"nombre"` como señal de que espera el nombre de usuario, y el cliente responde con eso.

## Requisitos

Python 3, sin dependencias externas.

## Cómo correrlo

Levantar el servidor:

```bash
python3 server.py
```

En otra terminal (una por cada cliente que quieras simular):

```bash
python3 client.py
```

Te va a pedir el nombre y después ya podés escribir mensajes.

## Manejo de errores

Cuando falla un `recv()` o un `send()` (por ejemplo porque el cliente cerró la terminal), el servidor lo toma como una desconexión: limpia el diccionario, cierra el socket y sigue funcionando con el resto de los clientes normalmente. No hay reintentos ni recuperación del lado del servidor, ahí simplemente se da de baja al cliente.

Del lado del cliente, si se corta la conexión, el hilo de escucha detecta el `recv()` vacío o el error, cierra el socket local y el programa vuelve a entrar en el loop de reconexión.

## Cosas que sé que le faltan

- `clientes_dict` se lee y escribe desde varios hilos al mismo tiempo sin ningún lock. Nunca me dio un problema en las pruebas que hice, pero es una condición de carrera real si dos clientes se conectan o desconectan en el mismo instante.
- No hay validación de mensajes: se puede mandar un mensaje vacío o gigante y el servidor lo reenvía igual.
- No hay manejo de nombres de usuario repetidos, dos clientes se pueden conectar con el mismo nombre sin problema.
- El protocolo es texto plano sin ningún tipo de framing. Si un mensaje llega partido en dos paquetes TCP, no lo estoy reconstruyendo, asumo que `recv(1024)` siempre trae el mensaje completo.
- No tiene tests. Es justamente lo que estoy armando ahora en el challenge siguiente.

## Preguntas del challenge

**¿Quién sos después de este reto?**

(completar)

**¿Cómo sobrevivió tu aplicación?**

(completar)

**¿Qué aprendiste cuando todo se rompió?**

(completar)
