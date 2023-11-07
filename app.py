from flask import Flask, request, make_response
from bson.objectid import ObjectId
from datetime import datetime
import pymongo
import certifi
import qrcode
import json
import io

# Conectando ao servidor do MongoDB
str_con = "mongodb+srv://admin:admin@aplicativoqrcode.mmjtjk8.mongodb.net/?retryWrites=true&w=majority"
client_con = pymongo.MongoClient(str_con, tlsCAFile=certifi.where())

# Selecionando as databases e as collections
usuarios = client_con.db_aplicativo.usuarios
portas = client_con.db_aplicativo.portas
relatorios = client_con.db_aplicativo.relatorios
presencas = client_con.db_aplicativo.presencas

# Criando o app Flask e o objeto QRcode
app = Flask("Aplicativo QR Code")

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

        # Data atual
        data_hora_atual = datetime.now()

        # Data atual formatada
        data_formatada = data_hora_atual.strftime("%Y/%m/%d %H:%M")

        # Obtendo a data e a hora
        data = data_formatada[:10]
        hora = data_formatada[11:]

        # Criando o dicionário com os dados do acesso
        relatorio = {
            "login_usuario": login_usuario,
            "numero_predio": numero_predio,
            "numero_sala": numero_sala,
            "data": data,
            "hora": hora,
            "acesso": acesso
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
        return data_formatada
    

# Rota para marcar presença
@app.route("/presenca/usuario/<login_usuario>", methods=["GET"])
def marcar_presenca(login_usuario):
    # Tenta executar o código
    try:
        # Obtendo o usuário
        usuario = usuarios.find_one({"login": login_usuario})

        # Verificando se o usuário existe
        if usuario is None:
            return {"erro": "Usuário não encontrado"}, 404

        # Data atual
        data_hora_atual = datetime.now()

        # Data atual formatada
        data_formatada = data_hora_atual.strftime("%Y/%m/%d %H:%M")

        # Obtendo a data e a hora
        data = data_formatada[:10]
        hora = data_formatada[11:]

        # Criando dicionario com os dados da presença
        presenca = {
            "login_usuario": usuario["login"],
            "nome": usuario["nome"],
            "permissao": usuario["permissao"],
            "data": data,
            "hora": hora
        }

        # Inserindo a presenca no banco de dados
        presencas.insert_one(presenca).inserted_id

        # Retornando mensagem de sucesso
        return {"mensagem": "Presença cadastrada com sucesso."}, 201

    # Caso ocorra algum erro, retorna o erro
    except Exception as e:
        return {"erro": str(e)}, 500
    

# Rota para obter presenças
@app.route("/presencas", methods=["GET"])
def obter_presencas():
    # Tenta executar o código
    try:
        # Obtendo dados do json
        dados = request.get_json()

        # Obtendo a data
        data = dados.get("data")

        # Verificando se a data foi informada
        if data == None:
            return {"erro": "Data não informada"}, 400
        
        # Obtendo as presenças
        presencas_dia = list(presencas.find({"data": data}))

        # Organizar as presenças por usuário
        presencas_organizadas = {}

        # Percorrendo as presenças do dia
        for presenca in presencas_dia:
            # Obtendo os dados da presença
            login_usuario = presenca["login_usuario"]
            nome = presenca["nome"]
            permissao = presenca["permissao"]
            data = presenca["data"]
            hora = presenca["hora"]
            
            # Organizando as presenças por usuário
            presencas_organizadas[login_usuario] = {
                    "login_usuario": login_usuario,
                    "nome": nome,
                    "permissao": permissao,
                    "data": data,
                    "hora": hora,
            }

        # Criando a estrutura de dados das presenças
        response = {
            "presencas": presencas_organizadas
        }

        # Retornando as presenças
        return response 
    
    # Caso ocorra algum erro, retorna o erro
    except Exception as e:
        return {"erro": str(e)}, 500


# Rota para gerar um QR Code
@app.route("/qrcode/usuario/<login_usuario>", methods=["GET"])
def gerar_qrcode(login_usuario):
    # Tenta executar o código
    try:
        # Obtendo o usuário
        usuario = usuarios.find_one({"login": login_usuario})

        # Verificando se o usuário existe
        if usuario is None:
            return {"erro": "Usuário não encontrado"}, 404

        # Criando o dicionário com o login do usuário
        dados = {
            "login": usuario["login"]
        }

        # Serializa os dados em formato JSON
        json_data = json.dumps(dados)

        # Gere o QR Code a partir dos dados serializados em JSON
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=12,
            border=6,
        )
        qr.add_data(json_data)
        qr.make(fit=True)

        # Crie uma imagem a partir do QR code
        img = qr.make_image(fill_color="black", back_color="white")

        # Crie uma resposta do Flask com a imagem em formato PNG
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)

        # Crie uma resposta do Flask com a imagem em formato PNG
        response = make_response(img_io.read())
        response.headers["Content-Type"] = "image/png"

        # Retorne a resposta
        return response

    # Caso ocorra algum erro, retorna o erro
    except Exception as e:
        return {"erro": str(e)}, 500


# Rota para gerar relatórios
@app.route("/relatorios", methods = ["GET"])
def gerar_relatorios():
    # Tenta executar o código
    try:
        # Obtendo dados da porta
        dados = request.get_json()

        # Obtendo a data
        data = dados.get("data")

        # Obtendo o número da sala
        numero_sala = dados.get("sala")

        # Obtendo o número do prédio
        numero_predio = dados.get("predio")
        
        # Verificando se os dados foram informados
        if data == None or numero_sala == None or numero_predio == None:
            return {"erro": "Data, sala e prédio devem ser informados"}, 400
        
        # Organizar o relatório por prédio e sala
        relatorios_organizados = {}

        # Obtendo o relatório
        relatorios_dia = list(relatorios.find({"data": data, "numero_predio": numero_predio, "numero_sala": numero_sala}))

        # Verificando se o relatório existe
        if relatorios_dia == []:
            return {"erro": "Relatório não encontrado"}, 404

        # Percorrendo o relatório do dia
        for relatorio in relatorios_dia:
            # Obtendo os dados do relatório
            acesso = relatorio['acesso']

            # Verifica se o acesso já está no dicionário do usuário
            if acesso in relatorios_organizados:
                relatorios_organizados[acesso] += 1
            else:
                relatorios_organizados[acesso] = 1

        # Criando a estrutura de dados do relatório
        response = {
            "relatorio": relatorios_organizados
        }

        # Retornando o relatório
        return response

    # Caso ocorra algum erro, retorna o erro
    except Exception as e:
        return {"erro": str(e)}, 500
    

# Rota para gerar relatórios gerais
@app.route("/relatorios/gerais", methods=["GET"])
def gerar_relatorios_gerais():
    # Tenta executar o código
    try:
        # Obtendo dados da porta
        dados = request.get_json()

        # Obtendo a data
        data = dados.get("data")
        
        # Obtendo os relatórios do dia
        relatorios_dia = list(relatorios.find({"data": data}))

        # Organizar os relatórios por prédio e sala
        relatorios_organizados = {}

        # Percorrendo os relatórios do dia
        for relatorio in relatorios_dia:
            # Obtendo os dados do relatório
            prédio = relatorio['numero_predio']
            sala = relatorio['numero_sala']
            acesso = relatorio['acesso']

            # Verifica se o prédio já está no dicionário
            if prédio not in relatorios_organizados:
                relatorios_organizados[prédio] = {}

            # Verifica se a sala já está no dicionário do prédio
            if sala not in relatorios_organizados[prédio]:
                relatorios_organizados[prédio][sala] = {}

            # Verifica se o acesso já está no dicionário da sala
            if acesso in relatorios_organizados[prédio][sala]:
                relatorios_organizados[prédio][sala][acesso] += 1
            else:
                relatorios_organizados[prédio][sala][acesso] = 1

        # Criando a estrutura de dados do relatório
        response = {
            "relatorios": relatorios_organizados
        }

        # Retornando o relatório
        return response

    # Caso ocorra algum erro, retorna o erro
    except Exception as e:
        return {"erro": str(e)}, 500


if __name__ == '__main__':
    app.run(debug=True)
