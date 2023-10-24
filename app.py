import pymongo
from flask import Flask, request, jsonify
import json
from bson import ObjectId
from pymongo import MongoClient, UpdateOne
# Retirar na versão final
import certifi


# Conectando ao servidor do MongoDB
str_con = "mongodb+srv://admin:admin@aplicativoqrcode.mmjtjk8.mongodb.net/?retryWrites=true&w=majority"
client_con = pymongo.MongoClient(str_con, tlsCAFile=certifi.where())

# Selecionando as databases e as collections
usuarios_col = client_con.usuarios.col_usuarios
portas_col = client_con.portas.col_portas
# Iniciando o Flask
app = Flask("Aplicativo QR Code")

# Rota teste
@app.route("/")
def teste():
    return "Aplicativo QR Code"

@app.route("/usuario", methods = ["POST"])
def cadastra_usuario():
    try:
        request_data = request.json
        if "nome" not in request_data or request_data["nome"] == "":
            return {"mensagem":"Nome do usuario não informado"}, 400
        if "permissao" not in request_data or request_data["permissao"] == "":
            return {"mensagem": "Nível de permissão do usuário não informado"}, 400

        nome = request_data["nome"]
        permissao = request_data["permissao"]

        mydb = client_con["usuarios"]
        mycol = mydb["col_usuarios"]
        mydict = { "nome": nome,
                  "permissao": permissao}
        x = mycol.insert_one(mydict)

        return jsonify({"mensagem":"Usário cadastrado"}), 200
        
    except Exception as e:
        return {"erro": str(e)}, 500
    
@app.route("/porta", methods = ["POST"])
def cadastra_porta():
    try:
        request_data = request.json
        if "predio" not in request_data or request_data["predio"] == "":
            return {"mensagem":"Predio da porta não informado"}, 400
        if "sala" not in request_data or request_data["sala"] == "":
            return {"mensagem":"Sala da porta não informado"}, 400
        if "permissao" not in request_data or request_data["permissao"] == "":
            return {"mensagem": "Nível de permissão da porta não informado"}, 400
        if "excessoes" not in request_data:
            return {"mensagem": "Excessoes não informadas"}, 400
        

        predio = request_data["predio"]
        permissao = request_data["permissao"]
        sala = request_data["sala"]
        excessoes = request_data["excessoes"]

        mydb = client_con["portas"]
        mycol = mydb["col_portas"]
        mydict = { "predio": predio,
                  "sala": sala,
                  "permissao": permissao,
                  "excessoes": excessoes}
        x = mycol.insert_one(mydict)

        return jsonify({"mensagem":"Porta cadastrada"}), 200
        
    except Exception as e:
        return {"erro": str(e)}, 500
    

@app.route("/acesso/usuario/<id_usuario>/porta/<id_porta>", methods = ["GET"])
def tenta_acesso(id_usuario, id_porta):
    try:
        try:
            # Converta o ID da string para um ObjectId
            id_usuario = ObjectId(id_usuario)
            id_porta = ObjectId(id_porta)
        except Exception as e:
            return jsonify({"error": "ID inválido"}), 400
        
        filtro1 = {
        "_id": id_usuario
        }
        filtro2 = {
        "_id": id_porta
        }
        usuario = usuarios_col.find_one(filtro1)
        porta = portas_col.find_one(filtro2)
        nivel_permissao_usuario = usuario["permissao"]
        nome_usuario = usuario["nome"]
        nivel_permissao_porta = porta["permissao"]
        execessoes = porta["excessoes"]
        if nivel_permissao_usuario >= nivel_permissao_porta:
            return {"mensagem": "ACESSO LIBERADO"}
        elif nome_usuario in execessoes:
            return {"mensagem": "ACESSO LIBERADO"}
        else:
            return {"mensagem": "ACESSO NEGADO"}


    except Exception as e:
        return {"erro": str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True)