import pymongo
from bson import ObjectId       # Libreria para trabajar con ObjectIDs de MongoDB
from flask import Flask, render_template, request, redirect, url_for
from subprocess import call     # Libreria con funcion

app = Flask(__name__)

###################################################################################################
###################################################################################################

### DATABASE MANAGER ###

myClient = pymongo.MongoClient("mongodb://localhost:27017")             # Conexion
# myClient = pymongo.MongoClient("mongodb://mongo-bgdb:27017/bgdb")     # Conexion
myDB = myClient["bgdb"]                                                 # Base de datos
myCollection = myDB["items"]                                            # Coleccion
myCounter = myDB["counter"]

##########################################################################

## Inicializar Contador ##
items = myCollection.find().to_list()
valoresIDs = [ item['id'] for item in items ]
last_id = 0
if valoresIDs.__len__() != 0:
    last_id = max(valoresIDs)
        
contador01 = myCounter.find_one()
if contador01 == None :
    print("Contador no inicializado")
    insertado = myCounter.insert_one( {"lastID" : last_id} )
    print( "Inicializando contador // Default = 0 // " + str(insertado ))
else:
    print("Contador inicializado previamente: " + str(contador01))
    
##########################################################################

### FUNCIONES DE CRUD ###

## Ingresa un nuevo documento a la coleccion ##
def insertNew(data):
    insertion = myCollection.insert_one(data)
    result = myCollection.find_one(insertion.inserted_id)
    # Actualizamos contador de ultimo ID ingresado 
    currentIndex = myCounter.find_one()['lastID']
    myCounter.update_one({'lastID' : currentIndex} ,
                         {"$inc" : {'lastID' :  1 } }
                        )
    return result

## Trae solo el primer documento ##
def readOnce():
    result = myCollection.find_one()
    return result

## Trae todos los documentos ##
def readAll():
    result = myCollection.find()
    return result

## Busca todos los documentos filtrados por el criterio (expresado en los clave-valor del diccionario pasado como parametro) ##
def queryData(filtrado):
    # Creo un array con los elementos k:v del dict "filtrado"
    items = []
    for k in filtrado:
        if k == "_id":
            items.append({ k : ObjectId(filtrado[k]) })
        else:
            items.append({ k : filtrado[k] })
    result = myCollection.find({"$and": items})
    return result

## Busca el primer documento que satisfaga el criterio (expresado en los clave-valor del diccionario pasado como parametro) ##
def queryOneItem(queryDict):
    # Creo un array con los elementos k:v del dict "filtrado"
    items = []
    for k in queryDict:
        if k == "_id":
            items.append({ k : ObjectId(queryDict[k]) })
        else:
            items.append({ k : queryDict[k] })
    result = myCollection.find_one({"$and": items})
    return result

## Busca por ObjectID ##
def findByObjectID(_id):
    query = {"_id" : ObjectId(_id)}
    result = myCollection.find_one(query)
    return result
    
## Actualiza el documento con el ObjectID pasado por el 1er parametro, con los datos brindados en el diccionario pasado por el 2do parametro ##
def updateDataObjID(id, newData):
    query = {"_id" : ObjectId(id)}
    newValues = {"$set" : newData}                # $set --> actualiza solo los campos indicados por los pares clave-valor colocados a la derecha --> {"key":"value", "key":"value", ...}
    myCollection.update_one(query, newValues)
    actualizado = queryOneItem(query)
    return actualizado
    
## Actualizar el documento cuya clave (1er parametro) posee el valor indicado (2do parametro), con los nuevos valores del diccionario pasado en el 3er parametro ##
def updateDataKeyValue(key, value, newData):
    query = {key : value}
    newValues = {"$set" : newData}
    myCollection.update_one(query, newValues)
    actualizado = queryOneItem(query)
    return actualizado

## Eliminar documentos ##
def deleteDataObjID(id):
    query = {"_id" : ObjectId(id)}
    borrado = myCollection.delete_one(query)
    return borrado.raw_result

## Realizar un backup de la BBDD ##
def exportarMongo():
    call("mongoexport --uri=mongodb://localhost:27017 --db=bgdb --collection=items --jsonArray --pretty --out=backup/bgdb_backup.json")

###################################################################################################
###################################################################################################

### FUNCIONES AUXILIARES ###

## Funcion para quitar campos vacios y corregir tipos numericos ##
def filtrarForm(formInput):
    # Copiamos a un dict el formInput y le quitamos los campos vacios filtrandolo por comprension
    formDict = formInput.to_dict()
    filtrado = { k:v for k,v in formDict.items() if v != '' }
    # Modifico el tipo de dato de los campos numericos (string a int o float)
    for k in filtrado:
        if k in {"id", "minPlayers", "maxPlayers", "minAge"}:
            filtrado[k] = (int)(filtrado[k])
        if k == "priceDollars":
            filtrado[k] = (float)(filtrado[k])
    return filtrado

## Funcion para validar campos de Insercion/Actualizacion de registros ##
def validarForm(filtrado):
    retorno = []
    cantValidos = filtrado.items().__len__()
    # Campos vacios
    if cantValidos < 7:
        codValidacion = 10
        retorno.append(codValidacion)
        return retorno        
    # Validar campo 'id' #
    encontrados = myCollection.find( {'id' : filtrado['id']} )
    listaEncontrados = encontrados.to_list()
    cantidad = len(listaEncontrados)
    if cantidad > 0:
        # ID encontrado
        codValidacion = 11
        retorno.extend(listaEncontrados)
        retorno.append(codValidacion)
        print(retorno)
        return retorno
    # Validar campo 'name' #
    encontrados = myCollection.find( {'name' : filtrado['name']} )
    listaEncontrados = encontrados.to_list()
    cantidad = len(listaEncontrados)
    if cantidad > 0:
        # Nombre encontrado
        codValidacion = 12
        retorno.extend(listaEncontrados)
        retorno.append(codValidacion)
        print(retorno)
        return retorno

###################################################################################################
###################################################################################################

### RUTAS ###

## Ruta Home ##
@app.route("/")
def main():
    return render_template("index.html")

## Ruta intermedia del metodo POST activado desde formulario del "index.html" ##
@app.route("/search", methods=['GET', 'POST'])
def search():    
    if request.method == "POST":
        formInput = request.form
        # Aplico funcion para quitar campos vacios y corregir tipos numericos
        filtrado = filtrarForm(formInput)
        # Quito y almaceno el campo "accion"
        accion = filtrado.pop("accion")
        # Busqueda - "filtrado" --> parametro
        listaResultados = []
        if filtrado.items().__len__() != 0:
            # Si el "filtrado" posee elementos, lo pasamos como parametro de busqueda
            listaResultados = queryData(filtrado).to_list()
        else:
            # Si el "filtrado" esta vacio, retornara todos los documentos
            listaResultados = readAll().to_list()            
        # Contamos la cantidad de elementos encontrados
        cantidad = len(listaResultados)
        if cantidad == 0:
            # Si no encuentro elementos, paso solo el mensaje de error a la vista
            return render_template( "results.html", mensaje=0 )
        else:
            # Si encuentro 1 o mas elementos, lo paso a la vista correspondiente (y si corresponde, tambien el mensaje)
            if accion == "Buscar":
                return render_template( "results.html", items=listaResultados )
            if accion == "Actualizar":
                if cantidad == 1:
                    item = listaResultados.pop()
                    return render_template( "actualizar.html", item=item )
                else:
                    return render_template( "results.html", mensaje=3 )
            if accion == "Eliminar":
                if cantidad == 1:
                    return render_template( "results.html", items=listaResultados, mensaje=5 )
                else:
                    return render_template( "results.html", mensaje=6 )
        
## Ruta formulario de insercion de registros a la BBDD ##
@app.route("/agregar")
def agregar():
    currentIndex = myCounter.find_one()['lastID']
    nextIndex = currentIndex + 1
    return render_template("agregar.html", nextIndex=nextIndex)

## Ruta intermedia del metodo POST activado desde formulario de "agregar.html" ##
@app.route("/agregando_item", methods=['GET', 'POST'])
def agregando_item():
    if request.method == 'POST':
        formInput = request.form
        # Filtrado de campos vacios y correccion de tipos numericos
        filtrado = filtrarForm(formInput)
        # Validacion de los campos del formulario - Gestion de errores
        resultadoValidacion = validarForm(filtrado)
        if resultadoValidacion != None:
            codigoValidacion = resultadoValidacion.pop()
            if codigoValidacion in [11,12]:
                # mensaje == 1 --> Elemento encontrado por 'id' o 'name'
                return render_template("results.html", items=resultadoValidacion, mensaje=1)
            if codigoValidacion == 10:
                # mensaje == 8 --> Hay campos vacios
                return render_template("results.html", mensaje=8)
        else:
            # Insertamos los datos del nuevo juego
            agregado = insertNew(filtrado)
            listaAgregados = []
            listaAgregados.append(agregado)
            if len(listaAgregados) > 0:
                return render_template("results.html", items=listaAgregados, mensaje=2)
            else:
                return render_template("results.html", mensaje=9)
    else:
        return redirect("/")

## Ruta formulario de actualizacion de registros de la BBDD ##
@app.route("/actualizar")
def actualizar():
    return render_template("actualizar.html")

## Ruta intermedia - metodo POST desde formulario "actualizar.html" ##
@app.route("/actualizando_item/<objID>/", methods=['GET', 'POST'])
def actualizando_item(objID):
    if request.method == 'POST':
        formInput = request.form
        # Filtrado de campos vacios y correccion de tipos numericos
        filtrado = filtrarForm(formInput)
        # Validacion de los campos del formulario - Gestion de errores
        resultadoValidacion = validarForm(filtrado)
        codigoValidacion = resultadoValidacion.pop()
        if codigoValidacion == 10 :
            # mensaje == 8 --> Hay campos vacios
            return render_template("results.html", mensaje=8)
        elif codigoValidacion == 11 and resultadoValidacion[0]['_id'] != ObjectId(objID) :
            # mensaje == 1 --> Elemento encontrado por 'id
            return render_template("results.html", items=resultadoValidacion, mensaje=1)
        else:
            # Si no hay errores, actualizo el registro
            actualizado = updateDataKeyValue("_id", ObjectId(objID), filtrado)
            return render_template("results.html", item=actualizado, mensaje=4)
    else:
        return redirect("/")

## Ruta intermedia activada desde la vista "results.html" con accion "Eliminar" ##
@app.route("/eliminar/<objID>")
def eliminar(objID):
    eliminado = deleteDataObjID(objID)
    return render_template("results.html", item=eliminado, mensaje=7)

## Ruta Backup ##
@app.route("/backup")
def backup():
    exportarMongo()
    return render_template("results.html", mensaje=10)

if __name__ == "__main__":
    app.run(debug=True)
    
################################################################################################

################################################################################################
#
#   ## REGISTROS DE PRUEBA ##
#
# item01 = {"name" : "Saboteur",
#           "minPlayers" : 3,
#           "maxPlayers" : 10,
#           "minAge" : 8,
#           "fromCountry" : "Alemania",
#           "priceDollars" : 15.25
#           }
# item02 = {"name" : "Kremlin",
#           "minPlayers" : 2,
#           "maxPlayers" : 6,
#           "minAge" : 12,
#           "fromCountry" : "Switzerland",
#           "priceDollars" : 55.0
#           }
# item03 = {"name" : "Catan",
#           "minPlayers" : 3,
#           "maxPlayers" : 4,
#           "minAge" : 10,
#           "fromCountry" : "Alemania",
#           "priceDollars" : 25.0
#           }
# item04 = {"name" : "Rummy",
#           "minPlayers" : 2,
#           "maxPlayers" : 4,
#           "minAge" : 8,
#           "fromCountry" : "Inglaterra",
#           "priceDollars" : 20.50
#           }
# item05 = {"name": "Las cobras de Shanghai",
#           "minPlayers": "2",
#           "maxPlayers": "10",
#           "minAge": "6",
#           "fromCountry": "China",
#           "priceDollars": "12"
#           }
# item06 = {"name": "Magic: The Gathering",
#           "minPlayers": "2",
#           "maxPlayers": "2",
#           "minAge": "13",
#           "fromCountry": "EEUU",
#           "priceDollars": "19.99"
#           }
# item07 = {"name": " Vampire: The Eternal Struggle",
#           "minPlayers": "2",
#           "maxPlayers": "5",
#           "minAge": "13",
#           "fromCountry": "EEUU",
#           "priceDollars": "23"
#           }
# item08 = {"name": "Backgammon",
#           "minPlayers": "2",
#           "maxPlayers": "2",
#           "minAge": "8",
#           "fromCountry": "Irak",
#           "priceDollars": "24.45"
#           }
# item09 = {"name": "Go",
#           "minPlayers": "2",
#           "maxPlayers": "2",
#           "minAge": "10",
#           "fromCountry": "Japon",
#           "priceDollars": "30"
#           }
# item10 = {"name": "Generala",
#           "minPlayers": "2",
#           "maxPlayers": "10",
#           "minAge": "5",
#           "fromCountry": "Argentina",
#           "priceDollars": "9.99"
#           }
# item11 = {"id": 11,
#           "name": "Ajedrez Clasico",
#           "minPlayers": 2,
#           "maxPlayers": 2,
#           "minAge": 5,
#           "fromCountry": "Francia",
#           "priceDollars": 35.6
#           }
#
######################################################################################################
#
#   ## EJEMPLOS DE EJECUCION DE COMANDOS DEL CRUD ##
#
# insertData(item04)
# readAll()
# queryData({"name":"Kremlin"})
# queryData({"minPlayers":3})
# queryOneItem({"minPlayers":3})
# findByObjectID("67a19bf726f50c5f65dd85b3")

# datosCorregidos = { "minAge" : 8 }
# updateDataObjID( ObjectId("67a19bf726f50c5f65dd85b2"), datosCorregidos )

# datosCorregidos = {"fromCountry" : "Alemania", "priceDollars" : 15.25}
# updateDataKeyValue("name", "Saboteur", datosCorregidos)

# deleteDataObjID("67a19bf726f50c5f65dd85b2")

################################################################################################
