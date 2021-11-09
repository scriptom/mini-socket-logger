# mini-socket-logger
Aplicación sencilla de sockets con Python, para la materia de Sistemas Distribuidos de la UCAB

## Ejecución
1. Clonar el repositorio: 
```shell
git clone https://github.com/scriptom/mini-socket-logger
```
1. Ejecutar el servidor en una terminal: 
```shell
python server.py --protocol=UDP
```
1. Ejecutar en otra terminal el cliente: 
```shell
python client.py --protocol=UDP
```
1. En el cliente, autenticar usando alguno de los nombres que estén en el archivo `users.txt` usando el comando `helloiam`, Ej: `helloiam tomas`
1. ¡Enviar mensajes! Para cerrar la conexión escriba `EXIT`.

Durante la ejecución, o luego de esta, puede revisar el archivo log.txt, para ver los mensajes enviados.
*Nota*: La app no contempla mensajes autenticados. Es decir, no recuerda qué usuario se autentica luego de que presenta su nombre por primera vez.

## Opciones
Tanto el servidor como el cliente únicamente cuentan con una opción
- `-p, <protocol> --protocol=<protocol>` que especifica el protocolo de comunicación de la aplicación a levantar. Puede ser UDP o TCP. Si los protocolos no coinciden, la comunicación no se va a poder establecer.
