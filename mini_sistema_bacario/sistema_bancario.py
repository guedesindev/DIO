from datetime import datetime, date
import locale, os, textwrap, csv
from abc import ABC, abstractmethod, abstractproperty
import validacoes_cadastro_usuario as validacoes
from functools import wraps
from pathlib import Path

from usuarios import criar_arquivo, adicionar_usuario

ROOT_PATH = Path(__file__).parent


def menu():
  menu = """
  ================ MENU ================
  [d]\tDepositar
  [s]\tSacar
  [e]\tExtrato
  [nc]\tNova conta
  [lc]\tListar contas
  [nu]\tNovo usuário
  [q]\tsair
  => """
  return input(textwrap.dedent(menu))


# Decorador para aplicar um log em transações realizadas.
def log_transacao(tipo_transacao): # tipo_transação é o argumento passado na chamada do decorador para saber qual transação está sendo realizada.
  def decorador_interna(func):
    @wraps(func) # Para preservar nome da função, docstring, etc.
    def wrapper(*args, **kwargs):
      # Executar a função original
      resultado = func(*args, **kwargs)

      # Dados para o log
      data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
      log_text = f"[{data_hora}] Função '{func.__name__}' executada com argumentos "
      for arg in args:
        log_text += f"{arg}"
      
      log_text += f". Retornou {resultado}\n"
      # log_text = f"{data_hora}: {func.__name__.upper()}\n"
      # Salvar o log pós a execução da transação
      try:
        if os.path.exists(ROOT_PATH/'arquivos'):
          pass
        else:
          os.mkdir(ROOT_PATH/'arquivos')
        
        file = ROOT_PATH/'arquivos'/'log-transacoes.txt'
        if not os.path.exists(file):
            with open(file, 'w', encoding='utf-8') as logfile:
              logfile.write(f"\n**** LOG DE TRANSAÇÃO ****\n")
              logfile.write(log_text)
        else:
          with open('log-transacoes.txt', 'a', encoding='utf-8') as log:
            log.write(log_text)
      except FileExistsError as e:
        print(f"Erro ao criar arquivo de log: {e}")
      return resultado
    return wrapper
  return decorador_interna


class Cliente():
  def __init__(self, endereco):
    self._endereco = endereco
    self._contas: list["Conta"] = []

  @property
  def endereco(self):
    return self._endereco
  
  @property
  def contas(self):
    return self._contas
  
  def adicionar_conta(self, conta):
    self.contas.append(conta)
  
  def realizar_transacao(self, conta, transacao):
    transacao.registrar(conta)
  

class PessoaFisica(Cliente):
  def __init__(self, cpf, nome, data_nascimento, endereco):
    super().__init__(endereco)
    self._nome = nome
    self._cpf = cpf
    self._data_nascimento = data_nascimento
  
  @property
  def cpf(self):
    return self._cpf
  
  @property
  def nome(self):
    return self._nome
  
  @nome.setter
  def nome(self, nome):
    self._nome = nome

  @property
  def data_nascimento(self):
    return self._data_nascimento.strftime('%d/%m/%Y')
  
  def __repr__(self) -> str:
    return f"<{__class__.__name__}: ({self.cpf})>"


# Classes referentes à conta, transações e histórico
class Conta():
  def __init__(self, numero, cliente): #H istórico é como um extrato
    self._numero = numero
    self._agencia = '0001'
    self._cliente = cliente
    self._saldo = 0
    self._historico = Historico()
  
  @property
  def saldo(self):
    return self._saldo

  @saldo.setter
  def saldo(self, novo_saldo):
    self._saldo = novo_saldo
  
  @property
  def agencia(self):
    return self._agencia
  
  @property
  def numero(self):
    return self._numero
  
  @property
  def cliente(self):
    return self._cliente
  
  @property
  def historico(self):
    return self._historico
  
  @classmethod
  def nova_conta(cls, cliente, numero):    
    return cls(numero, cliente)

  def sacar(self, valor:float):
    saldo = self._saldo
    excedeu_saldo = valor > saldo

    if excedeu_saldo:
      print("\nOperação falhou! Saldo insuficiente para esta operação")
    elif valor > 0:
      self._saldo -= valor
      print('\nSaque realizado com sucesso!')
      return True
    else:
      print('\nOperação Falou! Valor solicitado inválido.')
      return False

  def depositar(self, valor:float):
    if valor > 0:
      self._saldo += valor
      print('Depósito realizado com sucesso!')
      return True
    else:
      print('Operação falhou! Valor para depósito inválido')
      return False


  def exibir_extrato(self):
    print("\n============= EXTRATO ===============")
    if not self.historico.transacoes:
      print('Não há movimentações na conta ainda.')
    else:
      for transacao in self.historico.transacoes:
        sinal = ''
        if transacao.__class__.__name__ == 'Deposito':
          sinal = '(+)'
        elif transacao.__class__.__name__ == 'Saque':
          sinal = '(-)'
        print(f"{sinal}: Valor = {transacao.valor:,.2f}, Data: {transacao.data.strftime('%d/%m/%Y %H:%M:%S')}")
      print(f"Saldo: {self.saldo:,.2f}")
      print("=====================================")
  
    def __str__(self):
      return f"Conta(Número: {self._numero}, Agência: {self._agencia}, Cliente: {self._cliente.nome if self._cliente else 'N/A'})"


class ContaCorrente(Conta):
  def __init__(self, numero, cliente, limite = 500, limite_saques=3):
    super().__init__(numero, cliente)
    self._limite = limite
    self._limite_saques = limite_saques

  def sacar(self, valor):
    numero_saques = len(
        [transacao for transacao in self.historico._transacoes if transacao['tipo'] == Saque.__name__]
      )
    
    excedeu_limite = valor > self._limite
    excedeu_saques = numero_saques >= self._limite_saques

    if excedeu_limite:
      print('\nOperação Falhou! O valor de saque excede o limite.')    
    elif excedeu_saques:
      print('\nOperação falhou! Número máximo de saques excedido.')
    else:
      return super().sacar(valor)
    
    return False
  
  def __repr__(self) -> str:
    return f"<{self.__class__.__name__}: ('{self.agencia}', '{self.numero}', '{self.cliente.nome}')>"
  
  def __str__(self):
    return f"""
            Agência:\t{self.agencia}
            C/C:\t{self.numero}
            Titular:\t{self.cliente.nome}
            """


class Historico():
  def __init__(self):
    self._transacoes = []
  
  # @property
  # def transacoes(self):
  #   return self._transacoes

  def gerar_relatorio_transacoes(self, tipo_filtro=None):
    """
    Gerador que itera sobre transações do histórico,
    opcionalmente filtrando por tipo.
    
    Args:
      tipo_filtro (str, opcional): O nome da classe da transação para filtrar
                                    (ex. "Desposito", "Saque"). Se None retorna todas.
    Yields:
      dict: Um dicionario representando uma transação.                  
    """
    for transacao in self._transacoes:
      if tipo_filtro is None or transacao["tipo"].lower() == tipo_filtro.lower():
        yield transacao

  
  def adicionar_transacao(self, transacao):
    self._transacoes.append({
      "tipo":transacao.__class__.__name__,
      "valor":transacao.valor,
      "data":datetime.now().strftime("%d-%m-%Y %H:%M:%Y")
    })


class Transacao(ABC):  
  @property
  @abstractproperty
  def valor(self):
    pass
  
  @abstractmethod
  def registrar(self, conta):
    pass


class Deposito(Transacao):
  def __init__(self, valor):
    self._valor = valor

  @property
  def valor(self):
    return self._valor
  
  def registrar(self, conta:Conta):
    sucesso_transacao = conta.depositar(self.valor)

    if sucesso_transacao:
      conta.historico.adicionar_transacao(self)
    

class Saque(Transacao):
  def __init__(self, valor):
    self._valor = valor
  
  @property
  def valor(self):
    return self._valor

  def registrar(self, conta):
    sucesso_transacao = conta.sacar(self.valor)

    if sucesso_transacao:
      conta.historico.adicionar_transacao(self)



# ___ A CLASSE ITERADORA ContaIterador ---
class ContaIterador:
  def __init__(self, lista_contas):
    self._lista_contas = lista_contas
    self._index = 0 # índice para controlar a posição atual na iteração

  def __iter__(self):
    return self

  def __next__(self):
    if self._index < len(self._lista_contas):
      conta_atual = self._lista_contas[self._index]
      self._index += 1

      # Retorno das informações básicas da conta
      return {
        "numero": conta_atual.numero,
        "agencai": conta_atual.agencia,
        "saldo": conta_atual.saldo,
        "titular_nome":conta_atual.cliente.nome,
        "titular_cpf": conta_atual.cliente.cpf
      }
    else:
      # Não há mais contas, sinaliza o fim da iteração
      raise StopIteration



# Ações do usuário
def filtrar_cliente(cpf, clientes):
  clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
  return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente):
  if not cliente.contas:
    print('\nCliente não possui conta!')
    return
  
  return cliente.contas[0]


@log_transacao('Despósito')
def depositar(clientes):
  cpf = validacoes.receber_input_validado('CPF: ', 'CPF', validacoes.validar_cpf, 'CPF Inválido. Digite apenas os 11 números.')
  cliente = filtrar_cliente(cpf, clientes)

  if not cliente:
    print('\nCliente não encontrado')
    return
  
  valor = float(input("Informe o valor do depósito: "))
  transacao = Deposito(valor)

  conta = recuperar_conta_cliente(cliente)
  if not conta:
    return
  
  cliente.realizar_transacao(conta, transacao)


@log_transacao('Saque')
def sacar(clientes):
  cpf = validacoes.receber_input_validado('CPF: ', 'CPF', validacoes.validar_cpf, 'CPF Inválido. Digite apenas os 11 números.')
  cliente = filtrar_cliente(cpf, clientes)

  if not cliente:
    print('\nCliente não localizado!')
    return
  
  valor = float(input('Informe o valor do saque: '))
  transacao = Saque(valor)

  conta = recuperar_conta_cliente(cliente)
  if not conta:
    return
  
  cliente.realizar_transacao(conta, transacao)


def exibir_extrato(clientes):
  cpf = validacoes.receber_input_validado('CPF: ', 'CPF', validacoes.validar_cpf, 'CPF Inválido. Digite apenas os 11 números.')
  # cpf = input("CPF: ").strip()
  cpf_limpo = cpf.replace(".", "").replace("-", "")
  if not cpf_limpo.isdigit() or len(cpf_limpo) != 11:
    print('CPF inválido deve conter apenas digitos e 11 algarismos exatamente.')
    return
  
  cliente = filtrar_cliente(cpf_limpo, clientes)

  if not cliente:
    print('\nCLiente não encontrado!')
    return
  
  conta = recuperar_conta_cliente(cliente)
  if not conta:
    return
  
  print("\n================ EXTRATO ================")

  movimentacoes_encontradas = False
  for transacao in conta.historico.gerar_relatorio_transacoes():
    print(f"  Tipo: {transacao['tipo']}, Valor: R$ {transacao['valor']:.2f}, Data: {transacao['data']}")
    movimentacoes_encontradas = True

  if not movimentacoes_encontradas:
    print('Não foram realizadas movimentações.')

  print(f"\nSaldo: \t\t\tR$ {conta.saldo:,.2f}")
  print("==========================================")

@log_transacao("Criação de Cliente")
def criar_cliente():
    usuario = {}
    print("\n=============== Cadastro de Novo Cliente ===============")

    nome = validacoes.receber_input_validado('Nome: ', 'Nome', validacoes.validar_nome, "Nome Inválido.")
    usuario['nome'] = nome

    cpf = validacoes.receber_input_validado('CPF (apenas dígitos): ', 'CPF', validacoes.validar_cpf, 'CPF Inválido. Digite apenas os 11 números.')
    usuario['cpf'] = cpf
    

    dt_nascimento = validacoes.receber_input_validado('Data de nascimento (formato: dd/mm/aaaa): ', 'Data de Nascimento', validacoes.validar_dt_nascimento, "Formato de data inválido (dd/mm/aaaa).", validacoes.converter_dt_nascimento)
    usuario['data_nascimento'] = dt_nascimento
    

    usuario['endereco'] = ''

    logradouro = validacoes.receber_input_validado('Logradouro: ', 'logradouro', validacoes.validar_text_obrigatorio, 'Logradouro inválido')
    usuario['endereco'] += logradouro
    
    nro = validacoes.receber_input_validado('Nº: ', 'número', validacoes.validar_numero_endereco,  "O nº do endereço deve ser um dígito, ou 0 se não houver.", validacoes.converter_numero_endereco)
    usuario['endereco'] += f', {nro}'
    

    bairro = validacoes.receber_input_validado('Bairro: ', 'bairro', validacoes.validar_text_obrigatorio, "Bairro inválido")
    usuario['endereco'] += f', {bairro}'
    

    cidade = validacoes.receber_input_validado('Cidade: ', 'cidade', validacoes.validar_text_obrigatorio, 'Valor inválido para cidade.')
    usuario['endereco'] += f' - {cidade}'
    

    uf = validacoes.receber_input_validado('UF: ', 'uf', validacoes.validar_uf, 'UF inválida (exemplo: SP).')
    usuario['endereco'] += f'/{uf}'
    
    
    cliente = PessoaFisica(usuario.get('cpf'), usuario.get('nome'), usuario.get('data_nascimento'), usuario.get('endereco'))
    # Criar um CSV com os dados do cliente
    if not os.path.exists(ROOT_PATH/'usuarios.csv'):
      criar_arquivo()
      adicionar_usuario([usuario['cpf'], usuario['nome'], usuario['data_nascimento'], usuario['endereco']], 'users.csv')
    else:
      print(f" Arquivo users.csv existe: {os.path.exists(ROOT_PATH/'users.csv')}")
      adicionar_usuario([usuario['cpf'], usuario['nome'], usuario['data_nascimento'], usuario['endereco']], 'users.csv')


    validacoes.clientes.append(cliente)
    print("\n=== Finalização de Cadastro de Cliente ===============")
    print("\n=============== Cliente Cadastrado Com Sucesso !===============")
    
@log_transacao("Criação de Conta")
def criar_conta(numero_conta, clientes, contas):      
  while True:
    cpf = validacoes.receber_input_validado('CPF: ', 'CPF', validacoes.validar_cpf, 'CPF Inválido. Digite apenas os 11 números.')
    if cpf == 'q':
      break
    else: 
      cpf_limpo = cpf.replace('.', '').replace('-', '')
      if not cpf_limpo.isdigit() or len(cpf) != 11:
        print('CPF inválido. Digite apenas 11 numeros')
        return False
      else:
        cliente = localizar_cli(cpf_limpo, clientes)
        if cliente:
          conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
          contas.append(conta)
          cliente.contas.append(conta)
          print("\n=== Conta criada com sucess! ===\n")
          break
        else:
          print('Cliente não localizado. Deseja cadastrar novo cliente?')
          resposta = input(f"[S]im / [N]ão").strip()
          if resposta.lower() == 's':
            print(f"Cadastrando novo cliente")
          elif resposta.lower() == 'n':
            print(f"Voltando ao menu inicial...")
            break

@log_transacao('Listar Contas')
def listar_contas(contas):
  # for conta in contas:
  #   print('=' * 100)
  #   print(textwrap.dedent(str(conta)))
  contas_listadas = ContaIterador(contas)
  print(contas_listadas)

def localizar_cli(cpf, clientes):
    for cliente in clientes:
      if cliente.cpf == cpf:
        return cliente
    print('Cliente não localizado, favor verifique o CPF digitado.')
    return None        


def main():
  clientes = validacoes.clientes
  contas = []

  print('\n==================================================')
  print('=== Sistema Bancário Suzano - Python Developer ===')
  print('==================================================')

  while True:
    print('\nEscolha uma operação:')
    opcao = menu()
    match opcao:
      case 'nu':
        criar_cliente()
      case 'nc':
        numero_conta = len(contas) + 1
        criar_conta(numero_conta, clientes, contas)
      case 'q':
        break
      case 'd':
        depositar(clientes)
      case 's':
        sacar(clientes)
      case 'e':
        exibir_extrato(clientes)
      case 'lc':
        listar_contas(contas)
      case _:
        continue
  

if __name__=='__main__':
  main()


