### Sistema de Ponto
Este projeto é um sistema de ponto que pode ser configurado e executado localmente. Siga as instruções abaixo para configurar o ambiente e iniciar o sistema. 

### Pré-requisitos
Antes de começar, certifique-se de ter os seguintes itens instalados:

     1 - Visual Studio Code (VSCode): https://code.visualstudio.com/

     2 - SQLite: https://www.sqlite.org/download.html 
          2.1 - Baixe a versão compatível com o seu sistema operacional.
          2.2 - Adicione o diretório do SQLite às variáveis de ambiente do sistema.


### Configuração do Ambiente
1 - Criar um Ambiente Virtual
     No terminal do VSCode, execute:
          python -m venv .env
     *Este comando criará um ambiente virtual para isolar as dependências do projeto.

2 - Ativar o Ambiente Virtual
     Ative o ambiente virtual com o seguinte comando:
          .env\Scripts\Activate
     *Caso esteja usando Linux ou macOS, o comando pode ser:
          source .env/bin/activate

3 - Instalar Dependências
     Com o ambiente virtual ativo, instale todas as dependências do projeto executando:
          pip install -r requirements.txt


### Iniciando o Servidor
1 - Para iniciar o servidor local, execute:
     python main.py
     *Caso o comando python não funcione, tente substituí-lo por py.
2 - O sistema estará rodando localmente.


### Observações
Windows: Os comandos fornecidos são otimizados para este sistema operacional.
Linux/macOS: Os comandos podem variar ligeiramente. Ajuste conforme necessário