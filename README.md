### Este proyecto constituye el trabajo practico final para la asignatura Sistemas Operativos de la carrera de Analista Universitario en Sistemas ###

# APLICACION "BOARDGAME DATABASE" (bgdb) #

## Descripcion general ##

La aplicacion esta desarrollada en Python y Flask, con un enfoque mas bien funcional, en virtud de la simplicidad de las funcionalidades requeridas. Para su rapido desarrollo fueron de inestimable ayuda los videos-tutoriales de Flask brindados por la catedra.

La misma consta de un panel inicial con un formulario donde el usuario puede realizar busquedas por los diferentes campos que describen cada
uno de los juegos. Desde el mismo formulario, ademas de realizar busquedas, se pueden actualizar y/o eliminar elementos encontrados (excepto que se encuentre mas de un elemento, en cuyo caso se da aviso al usuario). Desde el mismo panel, ademas, se puede acceder a otro formulario para agregar nuevos registros.

Los formularios poseen tanto validacion en el HTML como en el backend. Para el primero, solo validamos el tipo de dato numerico en los campos ID,
Minimo y Maximo de Jugadores, Edad minima y Precio. En el backend, creamos 2 funciones que filtran los datos del formulario (filtrarForm) y validan que no exista el ID o el Nombre del juego (validarForm). En caso de encontrar coincidencias, la funcion redireccionara a una pagina con el mensaje correspondiente.

La app cuenta tambien con un contador interno que oficia de registro para el autoincremento del ID durante la insercion de nuevos registros. Este
contador se almacena en la base de datos en una coleccion diferenciada de la coleccion principal, ya que .

### Base de Datos ###

La base de datos es MongoDB (no-SQL), y su conexion se inicia al comienzo del script "app.py". Dentro de dicha conexion, creamos una base de datos con 2 colecciones: "items" y "counter". La primera es la coleccion principal, donde se almacenan los documentos correspondientes a los juegos de mesa. La segunda, como adelantabamos, es el contador interno del ultimo ID asignado a un documento. Posee un unico par clave-valor, siendo el valor el unico que se modifica durante las inserciones de nuevos documentos.

De esta forma, al iniciar la app en determinado contexto, el contador traera consigo el ultimo ID asignado, para poder continuar desde alli almacenando IDs, evitando de esta manera que se multipliquen los errores de insercion por IDs repetidos.

Si la base de datos no trae la coleccion "counter", entonces el script la inicializa con: a) el valor 0, si la coleccion "items" tambien viene vacia, o b) el valor de ID mas alto de entre todos los documentos de dicha coleccion (lo cual trae aparejado un recorrido completo de la coleccion para determinar su maximo).

## Implementacion en contenedores virtuales Docker ##

### Introduccion ###
La aplicacion se corre en 2 contenedores diferentes, como se muestra en el grafico: uno con el el stack Apache-Python-Flask, y otro con la base de datos MongoDB. En el primero, ademas, se agrega el modulo WSGI, que oficia de intermediario necesario entre Apache y Python.
Los contenedores se comunican a través de la librería "pymongo" para hacer las consultas y escrituras en la base de datos.

### Docker Compose ###
El archivo docker-compose.yml define y orquesta dos servicios: flaskapp, que ejecuta la aplicación de Flask con Apache, y mongo-bgdb, que proporciona una base de datos MongoDB. La aplicación flaskapp se construye desde un Dockerfile, expone el puerto 80 y se conecta a MongoDB mediante MONGO_URI. El contenedor mongo-bgdb utiliza la imagen oficial de MongoDB, expone el puerto 27017 y almacena los datos en un volumen persistente. La directiva depends_on asegura que MongoDB se inicie antes que Flask. Con un solo comando (docker-compose up), se despliega todo el entorno sin necesidad de configuraciones manuales.

### Docker File ###
El archivo Dockerfile define la imagen para el servicio flaskapp, configurando un entorno basado en python con Apache y mod_wsgi para ejecutar la aplicación Flask. Instala las dependencias del sistema, habilita el módulo WSGI en Apache y copia el código de la aplicación en el directorio /app. Luego, instala los paquetes de Python desde el archivo requirements y configura Apache con el archivo apache-flask.conf para servir la aplicación. Finalmente, expone el puerto 80 y ejecuta Apache en primer plano, asegurando que la aplicación Flask esté accesible al iniciarse el contenedor.

### Apache-Flask (conf) ###
El archivo apache-flask.conf configura Apache para servir la aplicación Flask mediante mod_wsgi. Define un VirtualHost en el puerto 80, estableciendo /app como el directorio raíz y mapeando las solicitudes a la aplicación Flask a través de WSGIScriptAlias. Se crea un proceso WSGI llamado flaskapp, asegurando que Apache ejecute la aplicación correctamente. Además, se configuran los registros de errores y accesos, y se otorgan los permisos necesarios al directorio /app para permitir el acceso a los archivos de la aplicación.

### WSGI ###
El archivo app.wsgi actúa como el punto de entrada para que Apache, a través de mod_wsgi, ejecute la aplicación Flask. Configura la ruta de Python para incluir los paquetes necesarios y el directorio de la aplicación. Luego, importa el objeto app desde app.py y lo expone como application, que es el nombre requerido por mod_wsgi para ejecutar la aplicación. Esto permite que Apache sirva Flask correctamente, manejando las solicitudes HTTP entrantes.

Para finalizar y dejar claro el funcionamiento se adjunta un esquema que muestra el funcionamiento y la conexión entre los contedores.

