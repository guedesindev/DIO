from datetime import datetime, date
import locale

locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

clientes = []

def receber_input_validado(mensagem, campo, validacao=None, mensagem_erro=None, converter=None):
  while True:
    entrada = input(mensagem).strip()
    if not entrada:
      print(f"{campo} é obrigatório.")
      continue

    if validacao is None:
      return entrada
    elif validacao(entrada):
      return converter(entrada) if converter else entrada
    else:
      print( mensagem_erro if mensagem_erro else "Entrada inválida. Tente Novamente.")

def validar_nome(nome):
  return not nome.isdigit() and not nome.isnumeric()

def validar_cpf(cpf):
  """Este método não validará o digito verificador, apenas sanitizará o cpf digitado pelo usuário garantindo que contenha apenas os números"""
  cpf_limpo = cpf.replace('.', '').replace('-', '')
  if not cpf_limpo.isdigit() or len(cpf) != 11:
    print('CPF inválido. Digite apenas 11 numeros')
    return False
  # elif verificar_cpf_existente(cpf_limpo):
  #   print('CPF já cadastrado.')
  #   return False
  else:
    print('CPF não cadastrado, continuando o cadastro.')
    return True


def validar_dt_nascimento(dt_nascimento_str):
  try:
    datetime.strptime(dt_nascimento_str, '%d/%m/%Y')
    return True
  except ValueError:
    return False

def converter_dt_nascimento(dt_nascimento_str):
  if(dt_nascimento_str):
    return datetime.strptime(dt_nascimento_str, "%d/%m/%Y").date()

def validar_numero_endereco(nro_str):
  return nro_str.isdigit() or nro_str.isnumeric()

def converter_numero_endereco(nro_str):
  return int(nro_str)

def validar_text_obrigatorio(texto):
  return not texto.isdigit() or not texto.isnumeric()

def validar_uf(uf):
  return len(uf) == 2 and uf.isalpha()


def verificar_cpf_existente(cpf):
  for cliente in clientes:
    if cliente.cpf == cpf:
      return True
  else:
    return False