import sqlite3

# Conexão com o banco de dados
conn = sqlite3.connect("db/registro_ponto.db")
cursor = conn.cursor()

# Criando tabela de usuários
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    senha TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK(tipo IN ('admin', 'colaborador'))
)
""")

# Criando tabela de colaboradores
cursor.execute("""
CREATE TABLE IF NOT EXISTS colaboradores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    nome TEXT NOT NULL,
    FOREIGN KEY(usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
)
""")

# Criando tabela de registros de ponto
cursor.execute("""
CREATE TABLE IF NOT EXISTS registros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    colaborador_id INTEGER NOT NULL,
    hora_registro TEXT NOT NULL,
    data_registro TEXT NOT NULL,
    FOREIGN KEY(colaborador_id) REFERENCES colaboradores(id)
)
""")

# Mensagem de sucesso
cursor.execute("INSERT INTO usuarios (nome, senha, tipo) VALUES (?, ?, ?)", ('admin', '123', 'admin'))
usuario_id = cursor.lastrowid
cursor.execute("INSERT INTO colaboradores (usuario_id, nome) VALUES (?, ?)", (usuario_id, 'admin'))

cursor.execute("INSERT INTO usuarios (nome, senha, tipo) VALUES (?, ?, ?)", ('colaborador', '123', 'colaborador'))
usuario_id = cursor.lastrowid
cursor.execute("INSERT INTO colaboradores (usuario_id, nome) VALUES (?, ?)", (usuario_id, 'colaborador'))



print("Banco de dados configurado com sucesso!")
conn.commit()
conn.close()
