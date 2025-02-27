import pymongo
from bson import ObjectId       # Libreria para trabajar con ObjectIDs de MongoDB
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

###################################################################################################

### DATABASE MANAGER ###

myClient = pymongo.MongoClient("mongodb://localhost:27017")     # Conexion
myDB = myClient["bgdb"]                                         # Base de datos
myCollection = myDB["items"]                                    # Coleccion

## Ingresa un nuevo documento a la coleccion ##
def insertNew(data):
    
    for k in data:
        if k in {"minPlayers", "maxPlayers", "minAge"}:
            data[k] = int(data[k])
        if k == "priceDollars":
            data[k] = float(data[k])
    
    insertion = myCollection.insert_one(data)
    print("ID insertado: " + str(insertion.inserted_id) + str(type(insertion.inserted_id)))
    result = myCollection.find_one(insertion.inserted_id)
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
def queryData(queryDict):
    # Creo un array con los elementos k:v del dict "filtrado"
    items = []
    for k in queryDict:
        if k == "_id":
            items.append({ k : ObjectId(queryDict[k]) })
        else:
            items.append({ k : queryDict[k] })
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

###################################################################################################

### FUNCIONES AUXILIARES ###

## Funcion para quitar campos vacios y corregir tipos numericos ##
def corregirDatosForm(datos):
    # Filtro el el documento por comprension
        filtrado = { k:v for k,v in datos.items() if v != '' }
        # Modifico el tipo de dato de los campos numericos (string a int o float)
        for k in filtrado:
            if k in {"minPlayers", "maxPlayers", "minAge"}:
                filtrado[k] = (int)(filtrado[k])
            if k == "priceDollars":
                filtrado[k] = (float)(filtrado[k])
        return filtrado

def validarForm(form):
    countEmptyFields = 0
    for k,v in form.items():
        if v == '':
            countEmptyFields += 1
            print(countEmptyFields)
    return countEmptyFields
                

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
        
        # Extraigo los datos del formulario a un diccionario
        datos = request.form.to_dict()
        # Aplico funcion para quitar campos vacios y corregir tipos numericos
        filtrado = corregirDatosForm(datos)
        # Quito y almaceno el campo "accion"
        accion = filtrado.pop("accion")
        
        # "filtrado" contiene los parametros de busqueda para la funcion "queryData"
        listaResultados = []
        if filtrado.items().__len__() != 0:
            # Si el "filtrado" posee elementos, lo pasamos como parametro de busqueda
            listaResultados = queryData(filtrado).to_list()
            print(listaResultados)
        else:
            # Si el "filtrado" esta vacio, retornara todos los documentos
            listaResultados = readAll().to_list()
            print(listaResultados)
            
        # Contamos la cantidad de elementos encontrados
        cantidad = len(listaResultados)
        print("Cantidad de elementos: " + str(cantidad))
        if cantidad == 0:
            # Si no encuentro elementos, paso solo el mensaje de error a la vista
            return render_template( "results.html", mensaje=4 )
        else:
            # Si encuentro 1 o mas elementos, lo paso a la vista correspondiente (y si corresponde, tambien el mensaje)
            if accion == "Buscar":
                return render_template( "results.html", items=listaResultados )
            if accion == "Actualizar":
                item = listaResultados.pop()
                return render_template( "actualizar.html", item=item )
            if accion == "Eliminar":
                return render_template( "results.html", items=listaResultados, mensaje=5 )
            
        
## Ruta formulario de insercion de registros a la BBDD ##
@app.route("/agregar")
def agregar():
    return render_template("agregar.html")

## Ruta intermedia del metodo POST activado desde formulario de "agregar.html" ##
@app.route("/agregando_item", methods=['GET', 'POST'])
def agregando_item():
    if request.method == 'POST':
        formInput = request.form
        
        # Aqui deberia hacerse la validacion de los campos del formulario y gestionar los errores
        #####################################
        vacios = validarForm(formInput)
        print(vacios)
        #####################################
        
        formInput = formInput.to_dict()
        filtrado = corregirDatosForm(formInput)
        resultado = queryData( {'name' : filtrado['name']} )
        listaEncontrados = resultado.to_list()
        cantidad = listaEncontrados.__len__()
        
        if cantidad == 0:
            # Insertamos los datos del nuevo juego
            agregado = insertNew(formInput)
            listaAgregados = []
            listaAgregados.append(agregado)
            
            if len(listaAgregados) > 0:
                return render_template("results.html", items=listaAgregados, mensaje=2)
            else:
                return render_template("results.html", mensaje=7)
        else:
            # No insertamos nada y avisamos que ya existe
            return render_template("results.html", items=listaEncontrados, nuevo=formInput, mensaje=1)
    else:
        return redirect("/")

## Ruta formulario de actualizacion de registros de la BBDD ##
@app.route("/actualizar")
def actualizar():
    return render_template("actualizar.html")

## Ruta intermedia del metodo POST activado desde formulario de "actualizar.html" ##
@app.route("/actualizando_item/<objID>/", methods=['GET', 'POST'])
def actualizando_item(objID):
    if request.method == 'POST':
        formInput = request.form
        formInput = formInput.to_dict()
        formInput = corregirDatosForm(formInput)        

        actualizado = updateDataKeyValue("_id", ObjectId(objID), formInput)
        return render_template("results.html", item=actualizado, mensaje=3)

## Ruta intermedia del metodo POST activado desde la vista "results.html" con accion "Eliminar" ##
@app.route("/eliminar/<objID>")
def eliminar(objID):
    print(objID)
    eliminado = deleteDataObjID(objID)
    print(eliminado)
    return render_template("results.html", item=eliminado, mensaje=6)

if __name__ == "__main__":
    app.run(debug=True)
    
################################################################################################
# Ruta destino del metodo GET (activado desde el formulario del "index") #
# def search():
#     if request.method == 'GET':
#         id = request.args['id']
#         print(id)
#         item = queryOneItem( {"id":int(id)} )
#         print(item['fromCountry'])
#         return redirect( url_for('results',
#                                  _id=item["_id"],
#                                  id=item["id"],
#                                  name=item["name"],
#                                  minPlayers=item["minPlayers"],
#                                  maxPlayers=item["maxPlayers"],
#                                  minAge=item["minAge"],
#                                  fromCountry=item["fromCountry"],
#                                  priceDollars=item["priceDollars"]
#                                  )
#                         )
#     else:
#         return redirect( "/" )
#
# Ruta destino de los resultados del metodo GET #
# @app.route("/results/<_id>/<id>/<name>/<minPlayers>/<maxPlayers>/<minAge>/<fromCountry>/<priceDollars>/")
# def results(_id, id, name, minPlayers, maxPlayers, minAge, fromCountry, priceDollars):
#     print(name)
#     return render_template( "results.html",
#                            _id=_id,
#                            id=id,
#                            name=name,
#                            minPlayers=minPlayers,
#                            maxPlayers=maxPlayers,
#                            minAge=minAge,
#                            fromCountry=fromCountry,
#                            priceDollars=priceDollars
#                            )
#
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

