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


def adicionar_usuario(dados:list, csvfile):
  with open(csvfile, 'a', encoding='utf-8', newline='') as file:
    writer = csv.writer(file, delimiter=',')
    user_data = [dado for dado in dados]
    print(user_data)
    writer.writerow(user_data)


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