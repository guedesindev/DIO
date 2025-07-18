# Criação de banco de dados de usuários e contas
import os, shutil, csv
from pathlib import Path


PATH_ROOT = Path(__file__).parent

users_csv = PATH_ROOT/'users.csv'

def criar_arquivo():
  with open(users_csv, 'w', encoding='utf-8', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(['cpf', 'nome', 'data_nascimento', 'endereco', 'num_contas'])

def adicionar_usuario(dados:list, csvfile):
  with open(csvfile, 'a', encoding='utf-8', newline='') as file:
    writer = csv.writer(file, delimiter=',')
    user_data = [dado for dado in dados]
    print(user_data)
    writer.writerow(user_data)

def ler_csv(file):
  with open(file, 'r', encoding='utf-8', newline='') as file:
    reader = csv.reader(file, delimiter=',')
    for row in reader:
      print(row)