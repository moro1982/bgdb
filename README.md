# Este proyecto constituye el trabajo practico final para la asignatura Sistemas Operativos de la carrera de Analista Universitario en Sistemas #

### APLICACION "BOARDGAME DATABASE" (bgdb) ###

# Descripcion general

La aplicacion esta desarrollada en Python y Flask, con un enfoque mas bien funcional, en virtud de la simplicidad de las funcionalidades requeridas.

La misma consta de un panel inicial con un formulario donde el usuario puede realizar busquedas por los diferentes campos que describen cada
uno de los juegos. Desde el mismo formulario, ademas de realizar busquedas, se pueden actualizar y/o eliminar elementos encontrados (excepto que se
encuentre mas de un elemento, en cuyo caso se da aviso al usuario). Desde el mismo panel, ademas, se puede acceder a otro formulario para agregar
nuevos registros.

Los formularios poseen tanto validacion en el HTML como en el backend. Para el primero, solo validamos el tipo de dato numerico en los campos ID,
Minimo y Maximo de Jugadores, Edad minima y Precio. En el backend, creamos 2 funciones que filtran los datos del formulario (filtrarForm) y validan
que no exista el ID o el Nombre del juego (validarForm). En caso de encontrar coincidencias, la funcion redireccionara a una pagina con el mensaje
correspondiente.

La app cuenta tambien con un contador interno que oficia de registro para el autoincremento del ID durante la insercion de nuevos registros. Este
contador se almacena en la base de datos en una coleccion diferenciada de la coleccion principal, ya que posee un unico par clave-valor.

