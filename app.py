import pymongo
from bson import ObjectId       # Libreria para trabajar con ObjectIDs de MongoDB
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

###################################################################################################

## DATABASE MANAGER ##

# Conexion
myClient = pymongo.MongoClient("mongodb://localhost:27017")
myDB = myClient["bgdb"]         # Base de datos
myCollection = myDB["items"]    # Coleccion

# Ingresa un nuevo documento a la coleccion
def insertNew(data):
    index = myCollection.count_documents({})
    idValue = index + 1
    anyDoc = myCollection.find_one( {"id" : idValue} )
    
    if anyDoc :
        print("El id del elemento insertado ya existe.")
        return None
    else:
        data['id'] = idValue
        print(data)
        insertion = myCollection.insert_one(data)
        print(insertion)
        result = myCollection.find_one(insertion.inserted_id)
        print(result)
        return result

def insertData(item):
    idValue = item["id"]
    anyDoc = myCollection.find_one( {"id" : idValue} )
    
    if (anyDoc != None):
        print("El id del elemento insertado ya existe. Desea actualizarlo con los datos brindados? (Y/N)")
        wannaUpdate = input()
        if (wannaUpdate.capitalize() == "Y"):
            updateDataKeyValue("id", idValue, item)
        else:
            print("Item no modificado. Datos del item:\n")
            queryOneItem(anyDoc)
    else:        
        result = myCollection.insert_one(item)
        print(result)

# Trae solo el primer documento
def readOnce():
    result = myCollection.find_one()
    print(result)

# Trae todos los documentos
def readAll():
    result = myCollection.find()
    for item in result:
        print(item)

# Busca todos los documentos filtrados por el criterio (expresado en los clave-valor del diccionario pasado como parametro)
def queryData(dict):
    query = dict
    result = myCollection.find(query)
    return result

# Busca el primer documento que satisfaga el criterio (expresado en los clave-valor del diccionario pasado como parametro)
def queryOneItem(dict):
    query = dict
    result = myCollection.find_one(query)
    return result

# Busca por ObjectID    
def findByObjectID(_id):
    query = {"_id" : ObjectId(_id)}
    result = myCollection.find_one(query)
    print(result)
    
# Actualiza el documento con el ObjectID pasado por el 1er parametro, con los datos brindados en el diccionario pasado por el 2do parametro
def updateDataObjID(id, newData):
    query = {"_id" : ObjectId(id)}
    newValues = {"$set":newData}                # $set --> actualiza solo los campos indicados por los pares clave-valor colocados a la derecha --> {"key":"value", "key":"value", ...}
    myCollection.update_one(query, newValues)
    
# Actualizar el documento cuya clave (1er parametro) posee el valor indicado (2do parametro), con los nuevos valores del diccionario pasado en el 3er parametro
def updateDataKeyValue(key, value, newData):
    query = {key : value}
    newValues = {"$set" : newData}
    myCollection.update_one(query, newValues)

# Eliminar documentos    
def deleteDataObjID(id):
    query = {"_id" : ObjectId(id)}
    myCollection.delete_one(query)

###################################################################################################

## RUTAS ##

# Ruta Home #
@app.route("/")
def main():
    return render_template("index.html")

# Ruta intermedia del metodo POST activado desde formulario del "index.html"
@app.route("/search", methods=['GET', 'POST'])
def search():    
    if request.method == 'POST':
        id = request.form.get('id')
        item = queryOneItem( {"id":int(id)} )
        print(item)
        return render_template( "results.html", item=item )

# Ruta formulario de insercion de registros a la BBDD #
@app.route("/agregar")
def agregar():
    return render_template("agregar.html")

# Ruta intermedia del metodo POST activado desde formulario de "agregar.html" #
@app.route("/agregando_item", methods=['GET', 'POST'])
def agregando_item():
    if request.method == 'POST':
        formInput = request.form
        formInput = formInput.to_dict()
        resultado = queryOneItem( {'name' : formInput['name']} )
        print(resultado)
        if resultado == None:
            # Insertamos los datos del nuevo juego
            agregado = insertNew(formInput)
            if agregado != None:
                return render_template("results.html", item=agregado, mensaje=2)
        else:
            # No insertamos nada y avisamos que ya existe
            return render_template("results.html", item=resultado, nuevo=formInput, mensaje=1)
    else:
        return redirect("/")


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


# item01 = {"id" : 1,
#           "name" : "Saboteur",
#           "minPlayers" : 3,
#           "maxPlayers" : 10,
#           "minAge" : 8,
#           "fromCountry" : "Alemania",
#           "priceDollars" : 15.25
#           }
# item02 = {"id" : 2,
#           "name" : "Kremlin",
#           "minPlayers" : 2,
#           "maxPlayers" : 6,
#           "minAge" : 12,
#           "fromCountry" : "Switzerland",
#           "priceDollars" : 55.0
#           }
# item03 = {"id" : 3,
#           "name" : "Catan",
#           "minPlayers" : 3,
#           "maxPlayers" : 4,
#           "minAge" : 10,
#           "fromCountry" : "Alemania",
#           "priceDollars" : 25.0
#           }
# item04 = {"id" : 4,
#           "name" : "Rummy",
#           "minPlayers" : 2,
#           "maxPlayers" : 4,
#           "minAge" : 8,
#           "fromCountry" : "Inglaterra",
#           "priceDollars" : 20.50
#           }

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

