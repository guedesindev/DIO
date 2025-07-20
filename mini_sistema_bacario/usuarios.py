# Criação de banco de dados de usuários e contas
import os, shutil, csv, sys
from pathlib import Path


PATH_ROOT = Path(__file__).parent

users_csv = ''
if not os.path.exists(PATH_ROOT/'arquivos'):
  os.mkdir('arquivos')

file = PATH_ROOT/'arquivos'/'clientes.csv'

def criar_arquivo():
  with open(file, 'w', encoding='utf-8', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(['cpf', 'nome', 'data_nascimento', 'endereco', 'num_contas'])


def adicionar_usuario(cliente, csvfile):
  with open(csvfile, 'a', encoding='utf-8', newline='') as file:
    writer = csv.writer(file, delimiter=',')
    dados = [cliente.cpf, cliente.nome, cliente.data_nascimento, cliente.endereco]
    writer.writerow(dados)


def pegar_dados_csv(file):
  with open(file, 'r', encoding='utf-8', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    try:
      clientes = []
      for idx, row in enumerate(reader):
        if idx == 0:
          continue
        clientes.append(row)
      
      return clientes
    except csv.Error as e:
      sys.exit(f"{e}")

def ler_csv(file):
  with open(file, 'r', encoding='utf-8', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
      print(row)


def adicionar_contas(cliente, file) -> None:
  """
  Localiza o cliente e altera sua lista de contas e adicionar nova conta

  Args:
    cliente (PessoaFisica): A lista de contas do cliente.
    file (str): o endereço do arquivo clientes.csv
  """

  linhas = []
  try:
    with open(file, 'r', encoding='utf-8', newline='') as csvfile:
      reader = csv.reader(csvfile, delimiter=',')
      linhas = list(reader)

    for i, linha in enumerate(linhas):
      if i == 0:
        continue
      
      if linha[0] == cliente.cpf:
        linha.append(cliente.contas)
        linhas[i] = linha
        print(i, linha)

    with open(file, 'w', encoding='utf-8', newline='') as csvfile:
      writer = csv.writer(csvfile, delimiter=',')
      for linha in linhas:
        print(f"Linha: {linha}")
        writer.writerow(linha)
    
    print(f"Lista de contas: '{cliente.contas}' adicionado ao cliente")
  except FileNotFoundError:
    print(f"Erro: O arquivo '{file}' não foi encontrado.")
  except Exception as e:
    print(f"Ocorreu um erro: {e}")