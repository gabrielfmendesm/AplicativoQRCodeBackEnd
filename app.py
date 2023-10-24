from flask import Flask, request
import pymongo

# Retirar na versão final
import certifi


# Conectando ao servidor do MongoDB
str_con = "mongodb+srv://admin:admin@aplicativoqrcode.mmjtjk8.mongodb.net/?retryWrites=true&w=majority"
client_con = pymongo.MongoClient(str_con, tlsCAFile=certifi.where())

# Selecionando as databases e as collections
usuarios = client_con.db_aplicativo.usuarios

# Iniciando o Flask
app = Flask("Aplicativo QR Code")

# Rota teste
@app.route("/")
def teste():
    return "Aplicativo QR Code"


if __name__ == '__main__':
    app.run(debug=True)