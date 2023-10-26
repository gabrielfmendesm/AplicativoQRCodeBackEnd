from flask import Flask, request, make_response
from flask_qrcode import QRcode
from bson.objectid import ObjectId
from datetime import datetime
import pymongo
import certifi

# Conectando ao servidor do MongoDB
str_con = "mongodb+srv://admin:admin@aplicativoqrcode.mmjtjk8.mongodb.net/?retryWrites=true&w=majority"
client_con = pymongo.MongoClient(str_con, tlsCAFile=certifi.where())

# Selecionando as databases e as collections
usuarios = client_con.db_aplicativo.usuarios
portas = client_con.db_aplicativo.portas
relatorios = client_con.db_aplicativo.relatorios

# Criando o app Flask e o objeto QRcode
app = Flask("Aplicativo QR Code")
qrcode = QRcode(app)


# Rota para cadastrar um usuário
@app.route("/usuario", methods = ["POST"])
def cadastrar_usuario():
    # Tenta executar o código
    try:
        # Obtendo os dados do usuário
        dados = request.get_json()
        
        # Verificando se os dados foram informados
        if "login" not in dados or dados["login"] == "":
            return {"erro": "Login do usuário não informado"}, 400
        if "nome" not in dados or dados["nome"] == "":
            return {"erro": "Nome do usuário não informado"}, 400
        if "permissao" not in dados or dados["permissao"] == "":
            return {"erro": "Nível de permissão do usuário não informado"}, 400
        
        # Verificando se o login e nome são strings e se a permissão é um número
        if type(dados["login"]) != str or type(dados["nome"]) != str or type(dados["permissao"]) != int:
            return {"erro": "Login e nome devem ser strings e permissão deve ser um número"}, 400
        
        # Verificando se o usuário já existe
        filtro = {
            "login": dados["login"]
        }

        # Verificando se o usuário já existe
        usuario = usuarios.find_one(filtro)
        if usuario != None:
            return {"erro": "Usuário já cadastrado"}, 400
        
        # Obtendo os dados do usuário
        login = dados["login"]
        nome = dados["nome"]
        permissao = dados["permissao"]

        # Criando o dicionário com os dados do usuário
        usuario = {
            "login": login,
            "nome": nome,
            "permissao": permissao
        }

        # Inserindo o usuário no banco de dados
        id_usuario = usuarios.insert_one(usuario).inserted_id

        # Retornando a mensagem de sucesso
        return {"mensagem": "Usuário cadastrado com sucesso", "id_usuario": str(id_usuario)}, 201
    
    # Caso ocorra algum erro, retorna o erro
    except Exception as e:
        return {"erro": str(e)}, 500


# Rota para editar um usuário
@app.route("/usuario/<id_usuario>", methods = ["PUT"])
def editar_usuario(id_usuario):
    # Tenta executar o código
    try:
        # Obtendo os dados do usuário
        dados = request.get_json()

        # Verificando se a permissão foi informada
        if "permissao" not in dados or dados["permissao"] == "":
            return {"erro": "Nível de permissão do usuário não informado"}, 400
        
        # Verificando se a permissão é um número
        if type(dados["permissao"]) != int:
            return {"erro": "Permissão deve ser um número"}, 400
        
        # Verificando se o ID do usuário é válido
        id_usuario = ObjectId(id_usuario)

        # Verificando se o usuário existe
        usuario = usuarios.find_one({"_id": id_usuario})

        # Verificando se o usuário existe
        if usuario == None:
            return {"erro": "Usuário não encontrado"}, 404
        
        # Verifica se o usuário já tem a permissão informada
        if usuario["permissao"] == dados["permissao"]:
            return {"erro": "Usuário já tem a permissão informada"}, 400
        
        # Atualizando as exceções do usuário
        usuarios.update_one({"_id": ObjectId(id_usuario)}, {"$set": {"permissao": dados["permissao"]}})

        # Retornando a mensagem de sucesso
        return {"mensagem": "Usuário atualizado com sucesso"}, 200
    
    # Caso ocorra algum erro, retorna o erro
    except Exception as e:
        return {"erro": str(e)}, 500
        

# Rota para cadastrar uma porta
@app.route("/porta", methods = ["POST"])
def cadastrar_porta():
    # Tenta executar o código
    try:
        # Obtendo os dados da porta
        dados = request.get_json()

        # Verificando se os dados foram informados
        if "predio" not in dados or dados["predio"] == "":
            return {"erro": "Prédio da porta não informado"}, 400
        if "sala" not in dados or dados["sala"] == "":
            return {"erro": "Sala da porta não informada"}, 400
        if "permissao" not in dados or dados["permissao"] == "":
            return {"erro": "Nível de permissão da porta não informado"}, 400
        
        # Se o campo exceções não foi informado, cria uma lista vazia
        if "excecoes" not in dados:
            dados["excecoes"] = []

        # Verificar se as exceções são uma lista
        if type(dados["excecoes"]) != list:
            return {"erro": "Exceções devem ser uma lista"}, 400

        # Verificando se o prédio, sala e permissão são números inteiros
        if type(dados["predio"]) != int or type(dados["sala"]) != int or type(dados["permissao"]) != int:
            return {"erro": "Prédio, sala e permissão devem ser números"}, 400
        
        # Verificando se a porta já existe
        filtro = {
            "predio": dados["predio"],
            "sala": dados["sala"]
        }

        # Verificando se a porta já existe
        porta = portas.find_one(filtro)
        if porta != None:
            return {"erro": "Porta já cadastrada"}, 400
        
        # Criando o dicionário com os dados da porta
        porta = {
            "predio": dados["predio"],
            "sala": dados["sala"],
            "permissao": dados["permissao"],
            "excecoes": dados["excecoes"]
        }

        # Inserindo a porta no banco de dados
        id_porta = portas.insert_one(porta).inserted_id

        # Retornando a mensagem de sucesso
        return {"mensagem": "Porta cadastrada com sucesso", "id_porta": str(id_porta)}, 201
    
    # Caso ocorra algum erro, retorna o erro
    except Exception as e:
        return {"erro": str(e)}, 500
    

# Rota para editar uma porta
@app.route("/porta/<id_porta>", methods = ["PUT"])
def editar_porta(id_porta):
    # Tenta executar o código
    try:
        # Obtendo os dados da porta
        dados = request.get_json()

        # Verificando se as exceções foram informadas
        if "excecoes" not in dados:
            return {"erro": "Exceções não informadas"}, 400
        
        # Verificar se as exceções são uma string
        if type(dados["excecoes"]) != str:
            return {"erro": "Exceções devem ser uma string"}, 400
        
        # Obtendo as exceções
        excecoes = dados["excecoes"]
        
        # Obtendo o ID da porta
        id_porta = ObjectId(id_porta)

        # Verificando se a porta existe
        porta = portas.find_one({"_id": id_porta})

        # Verificando se a porta existe
        if porta == None:
            return {"erro": "Porta não encontrada"}, 404
        
        # Obtendo as exceções da porta
        excecoes_porta = porta["excecoes"]

        # Verificando se a exceção já existe
        if excecoes in excecoes_porta:
            return {"erro": "Exceção já cadastrada"}, 400
        
        # Adicionando a exceção na porta
        excecoes_porta.append(excecoes)

        # Atualizando a porta no banco de dados
        portas.update_one({"_id": id_porta}, {"$set": {"excecoes": excecoes_porta}})        

        # Retornando a mensagem de sucesso
        return {"mensagem": "Porta atualizada com sucesso"}, 200
    
    # Caso ocorra algum erro, retorna o erro
    except Exception as e:
        return {"erro": str(e)}, 500
    

# Rota para excluir uma exceção de uma porta
@app.route("/porta/<id_porta>", methods = ["DELETE"])
def excluir_excecao(id_porta):
    # Tenta executar o código
    try:
        # Obtendo dados da porta
        dados = request.get_json()

        # Verificando se a exceção foi informada
        if "excecao" not in dados or dados["excecao"] == "":
            return {"erro": "Exceção não informada"}, 400
        
        # Verificar se a exceção é uma string
        if type(dados["excecao"]) != str:
            return {"erro": "Exceção deve ser uma string"}, 400
        
        # Obtendo a exceção
        excecao = dados["excecao"]

        # Obtendo o ID da porta
        id_porta = ObjectId(id_porta)

        # Verificando se a porta existe
        porta = portas.find_one({"_id": id_porta})

        # Verificando se a porta existe
        if porta == None:
            return {"erro": "Porta não encontrada"}, 404
        
        # Obtendo as exceções da porta
        excecoes_porta = porta["excecoes"]

        # Verificando se a exceção existe
        if excecao not in excecoes_porta:
            return {"erro": "Exceção não cadastrada"}, 400
        
        # Removendo a exceção da porta
        excecoes_porta.remove(excecao)

        # Atualizando a porta no banco de dados
        portas.update_one({"_id": id_porta}, {"$set": {"excecoes": excecoes_porta}})

        # Retornando a mensagem de sucesso
        return {"mensagem": "Exceção excluída com sucesso"}, 200
    
    # Caso ocorra algum erro, retorna o erro
    except Exception as e:
        return {"erro": str(e)}, 500
    

# Rota para testar o acesso a uma porta
@app.route("/acesso/usuario/<login_usuario>/predio/<numero_predio>/sala/<numero_sala>", methods = ["GET"])
def testar_acesso(login_usuario, numero_predio, numero_sala):
    # Tenta executar o código
    try:
        # Obtendo o usuário
        usuario = usuarios.find_one({"login": login_usuario})

        # Verificando se o usuário existe
        if usuario == None:
            return {"erro": "Usuário não encontrado"}, 404
        
        # Obtendo a porta
        porta = portas.find_one({"predio": int(numero_predio), "sala": int(numero_sala)})

        # Verificando se a porta existe
        if porta == None:
            return {"erro": "Porta não encontrada"}, 404
        
        # Obtendo a permissão do usuário e da porta
        permissao_usuario = usuario["permissao"]
        permissao_porta = porta["permissao"]

        # Obtendo as exceções da porta
        excecoes_porta = porta["excecoes"]

        # Verificando se o usuário tem acesso à porta
        if permissao_usuario >= permissao_porta:
            acesso = "ACESSO PERMITIDO"
        elif login_usuario in excecoes_porta:
            acesso = "ACESSO PERMITIDO"
        else:
            acesso = "ACESSO NEGADO"
        
        # Criando o dicionário com os dados do acesso
        relatorio = {
            "login_usuario": login_usuario,
            "numero_predio": numero_predio,
            "numero_sala": numero_sala,
            "data_hora": datetime.now()
        }

        # Inserindo o acesso no banco de dados
        relatorios.insert_one(relatorio).inserted_id

        # Retornando a mensagens
        if acesso == "ACESSO PERMITIDO":
            return {"mensagem": acesso}, 200
        else:
            return {"mensagem": acesso}, 403

    # Caso ocorra algum erro, retorna o erro
    except Exception as e:
        return {"erro": str(e)}, 500


# Rota para gerar um QR Code
@app.route("/qrcode/usuario/<login_usuario>", methods = ["GET"])
def gerar_qrcode(login_usuario):
    # Tenta executar o código
    try:
        # Obtendo o usuário
        usuario = usuarios.find_one({"login": login_usuario})

        # Verificando se o usuário existe
        if usuario == None:
            return {"erro": "Usuário não encontrado"}, 404

        # Criando o diciário com os dados do usuário
        dados = {
            "login": usuario["login"],
            "nome": usuario["nome"],
            "permissao": usuario["permissao"],
            "data_hora": datetime.now()
        }

        # Gere o QR Code a partir dos dados
        qr = qrcode(dados, mode="raw", box_size=12, border=6)

        # Criando a resposta
        response = make_response(qr)
        response.headers["Content-Type"] = "image/png"

        return response

    except Exception as e:
        return {"erro": str(e)}, 500


if __name__ == '__main__':
    app.run(debug=True)