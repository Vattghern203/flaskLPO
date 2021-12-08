# Otávio Augusto Barbiéri Comp 4
import time

from flask import Flask, render_template, request, redirect, session, flash, url_for, send_from_directory

from dao import JogoDao, UsuarioDao

from flask_mysqldb import MySQL

from models import Jogo, Usuario

import os

app = Flask(__name__)
app.secret_key = 'LP2'

app.config['UPLOAD_PATH'] = os.path.dirname(os.path.abspath(__file__))+'/uploads'
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'jogoteca'
app.config['MYSQL_PORT'] = 3306

db = MySQL(app)

jogo_dao = JogoDao(db)
usuario_dao = UsuarioDao(db)


@app.route('/')
def index():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect('/login')
    return render_template('index.html', titulo='Central de jogos')


@app.route('/lista_jogos')
def lista_jogos():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect('/login?proxima=lista_jogos')
    lista = jogo_dao.listar()
    return render_template('lista.html', titulo='Lista de Jogos', jogos=lista)


@app.route('/novo')
def novo():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect('/login?proxima=novo')
    return render_template('novo.html', titulo='Cadastro Novos Jogo')


@app.route('/criar', methods=['POST', ])
def criar():
    nome = request.form['nome']
    categoria = request.form['categoria']
    console = request.form['console']
    jogo = Jogo(nome, categoria, console)

    jogo = jogo_dao.salvar(jogo)
    
    arquivo = request.files['arquivo']
    upload_path = app.config['UPLOAD_PATH']
    timestamp = time.time()
    arquivo.save(f'{upload_path}/capa{jogo._id}-{timestamp}.jpg')
    
    return redirect('/lista_jogos')


@app.route('/login')
def login():
    proxima = request.args.get('proxima')
    if proxima == None:
        proxima = ''
    return render_template('login.html', proxima=proxima)


@app.route('/autenticar', methods=['POST', ])
def autenticar():
    usuario = usuario_dao.busca_por_id(request.form['usuario'])
    if usuario:
        if usuario._senha == request.form['senha']:
            session['usuario_logado'] = request.form['usuario']
            flash(request.form['usuario'] + ' logou com sucesso!')
            proxima_pagina = request.form['proxima']
            if proxima_pagina == '':
                return redirect('/')
            else:
                return redirect('/'.format(proxima_pagina))

    flash('Erro ao logar! Tente novamente.')
    return redirect('/login')


@app.route('/logout')
def logout():
    session['usuario_logado'] = None
    flash('Nenhum usuário logado')
    return redirect('/login')


@app.route('/editar/<int:id>')
def editar(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('editar')))
    jogo = jogo_dao.busca_por_id(id)
    nome_imagem = recupera_imagem(id)
    return render_template('editar.html', titulo='Editando jogo selecionado', jogo=jogo, capa_jogo=nome_imagem or 'capa_padrao.jpg')


@app.route('/atualizar', methods=['POST', ])
def atualizar():
    nome = request.form['nome']
    categoria = request.form['categoria']
    console = request.form['console']
    id = request.form['id']
    jogo = Jogo(nome, categoria, console, id)

    arquivo = request.files['arquivo']
    upload_path = app.config['UPLOAD_PATH']
    timestamp = time.time()
    deleta_arquivo(jogo._id)
    arquivo.save(f'{upload_path}/capa{jogo._id}-{timestamp}.jpg')

    jogo_dao.salvar(jogo)

    return redirect('/lista_jogos')


@app.route('/deletar/<int:id>')
def deletar(id):
    jogo_dao.deletar(id)
    flash('O jogo foi deletado com sucesso!')
    return redirect(url_for('lista_jogos'))


@app.route('/uploads/<nome_arquivo>')
def imagem(nome_arquivo):
    return send_from_directory('uploads', nome_arquivo)


def recupera_imagem(id):
    for nome_arquivo in os.listdir(app.config['UPLOAD_PATH']):
        if f'capa{id}-' in nome_arquivo:
            return nome_arquivo


def deleta_arquivo(id):
    arquivo = recupera_imagem(id)
    os.remove(os.path.join(app.config['UPLOAD_PATH'], arquivo))


def print_hi(name):
    #
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# código


if __name__ == '__main__':
    app.run(debug=True)
