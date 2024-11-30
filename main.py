from datetime import datetime
import traceback
from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import subprocess
import os

from app.password_Generator import generate_password


class RegistroPontoApp:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)  # Permite que o React acesse os endpoints
        self.configure_routes()

    def configure_routes(self):
        self.app.add_url_rule("/login", methods=["POST"], view_func=self.login)
        self.app.add_url_rule("/registrar_ponto", methods=["POST"], view_func=self.registrar_ponto)
        self.app.add_url_rule("/colaboradores/<int:usuario_id>", methods=["GET"], view_func=self.mostrar_colaborador)
        self.app.add_url_rule("/colaboradores", methods=["GET"], view_func=self.listar_colaboradores)
        self.app.add_url_rule("/registros/<int:colaborador_id>", methods=["GET"], view_func=self.listar_registros_por_colaborador)
        self.app.add_url_rule("/colaboradores", methods=["POST"], view_func=self.adicionar_colaborador)
        self.app.add_url_rule("/colaboradores/<int:id_colaborador>", methods=["DELETE"], view_func=self.remover_colaborador)

    def login(self):
        data = request.json
        nome = data.get("nome")
        senha = data.get("senha")

        try:
            with sqlite3.connect("db/registro_ponto.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, tipo FROM usuarios WHERE nome = ? AND senha = ?", (nome, senha))
                user = cursor.fetchone()

                if not user:
                    return jsonify({"error": "Usuário ou senha incorretos"}), 401

                user_id, tipo = user
                colaborador_id = None

                if tipo == "colaborador":
                    cursor.execute("SELECT id FROM colaboradores WHERE usuario_id = ?", (user_id,))
                    colaborador = cursor.fetchone()
                    if colaborador:
                        colaborador_id = colaborador[0]
                    else:
                        return jsonify({"error": "Colaborador não encontrado"}), 404

                return jsonify({"id": user_id, "tipo": tipo, "colaborador_id": colaborador_id}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def registrar_ponto(self):
        data = request.json
        colaborador_id = data.get("colaborador_id")

        if not colaborador_id:
            return jsonify({"error": "Colaborador não autenticado"}), 401

        hora_atual = datetime.now().strftime("%H:%M:%S")
        data_atual = datetime.now().strftime("%Y-%m-%d")

        try:
            with sqlite3.connect("db/registro_ponto.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO registros (colaborador_id, hora_registro, data_registro) 
                    VALUES (?, ?, ?)
                    """,
                    (colaborador_id, hora_atual, data_atual),
                )
                conn.commit()
            return jsonify({
                "message": "Ponto registrado com sucesso!!",
                "horario": hora_atual
                }), 201
        except sqlite3.OperationalError as e:
            return jsonify({"error": f"Erro no banco de dados: {e}"}), 500
        except Exception as e:
            return jsonify({"error": "Ocorreu um erro inesperado."}), 500

    def mostrar_colaborador(self, usuario_id):
        if not usuario_id:
            return jsonify({"erro": "usuario_id não fornecido"}), 400

        try:
            with sqlite3.connect("db/registro_ponto.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT nome FROM colaboradores WHERE usuario_id = ?
                """, (usuario_id,))
                colaborador = cursor.fetchone()

                if colaborador:
                    return jsonify({"nome": colaborador[0]})
                else:
                    return jsonify({"erro": "Colaborador não encontrado"}), 404
        except sqlite3.Error as e:
            print(f"Erro ao acessar o banco de dados: {e}")
            return jsonify({"erro": "Erro ao acessar o banco de dados"}), 500

    def listar_colaboradores(self):
        try:
            with sqlite3.connect("db/registro_ponto.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT colaboradores.id, colaboradores.nome, usuarios.nome AS nome_usuario
                FROM colaboradores
                JOIN usuarios ON colaboradores.usuario_id = usuarios.id
                WHERE usuarios.tipo = 'colaborador'
                """)
                colaboradores = cursor.fetchall()
            return jsonify([{"id": colab[0], "nome": colab[1], "usuario_nome": colab[2]} for colab in colaboradores])
        except sqlite3.Error as e:
            return jsonify({"error": str(e)}), 500

    def listar_registros_por_colaborador(self, colaborador_id):
        # Captura o parâmetro 'data' da query string
        data = request.args.get('data', None)

        print('ID do colaborador:', colaborador_id)
        print('Data da busca:', data)

        try:
            with sqlite3.connect("db/registro_ponto.db") as conn:
                cursor = conn.cursor()
                if data:
                    # Se uma data for fornecida, filtra também por data
                    cursor.execute("""
                        SELECT registros.id, registros.hora_registro, registros.data_registro
                        FROM registros
                        WHERE registros.colaborador_id = ? AND registros.data_registro = ?
                    """, (colaborador_id, data))
                else:
                    # Se nenhuma data for fornecida, retorna todos os registros do colaborador
                    cursor.execute("""
                        SELECT registros.id, registros.hora_registro
                        FROM registros
                        WHERE registros.colaborador_id = ?
                    """, (colaborador_id,))
                
                registros = cursor.fetchall()

            return jsonify([{"id_registro": reg[0], "hora": reg[1]} for reg in registros])

        except sqlite3.Error as e:
            return jsonify({"error": str(e)}), 500


    def adicionar_colaborador(self):
        data = request.json
        nome = data.get("nome")
        print(f"Nome recebido: {nome}")  # Verifique se o nome está sendo recebido corretamente
        senha = generate_password()

        try:
            with sqlite3.connect("db/registro_ponto.db", timeout=30) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;")
                print("Conexão com o banco de dados estabelecida.")  # Log da conexão
                cursor.execute("INSERT INTO usuarios (nome, senha, tipo) VALUES (?, ?, ?)", (nome, senha, 'colaborador'))
                usuario_id = cursor.lastrowid
                cursor.execute("INSERT INTO colaboradores (usuario_id, nome) VALUES (?, ?)", (usuario_id, nome))
                conn.commit()
                print(f"Usuário {nome} adicionado com sucesso com ID {usuario_id}.")  # Confirmação
            return jsonify({"message": f"Colaborador {nome} adicionado com sucesso! senha gerada: {senha}"}), 201
        except sqlite3.OperationalError as e:
            print(f"Erro de operação no banco de dados: {e}")
            return jsonify({"error": "Erro ao acessar o banco de dados. Tente novamente."}), 500
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")
            print(traceback.format_exc())
            return jsonify({"error": "Ocorreu um erro inesperado. Verifique os logs para mais detalhes."}), 500


    def remover_colaborador(self, id_colaborador):
        print('removendo colaborador do id: ', id_colaborador)
        try:
            with sqlite3.connect("db/registro_ponto.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT usuario_id FROM colaboradores WHERE id = ?", (id_colaborador,))
                colaborador = cursor.fetchone()


                if colaborador:
                    usuario_id = colaborador[0]

                    cursor.execute("SELECT COUNT(*) FROM registros WHERE colaborador_id = ?", (id_colaborador,))
                    
                    registros_count = cursor.fetchone()[0]

                    if registros_count > 0:
                        cursor.execute("DELETE FROM registros WHERE colaborador_id = ?", (id_colaborador,))

                    cursor.execute("DELETE FROM colaboradores WHERE id = ?", (id_colaborador,))
                    cursor.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
                    
                    conn.commit()
                    return jsonify({"message": f"Colaborador ID {id_colaborador} e usuário removidos com sucesso!"})
                else:
                    return jsonify({"message": "Colaborador não encontrado!"}), 404
        except sqlite3.Error as e:
            return jsonify({"error": str(e)}), 500
        except Exception as e:
            return


if __name__ == "__main__":
    app = RegistroPontoApp()

    db_create_path = 'db/create_bd.py'
    db_path = 'db/registro_ponto.db'

    if os.path.exists(db_path):
        print('Banco de dados já criado')
    else:
        result = subprocess.run(['python', db_create_path], capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)

    app.app.run(debug=True)
