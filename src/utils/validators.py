import re


def validate_cnj_number(number: str) -> bool:
    """
    Valida número de processo no padrão CNJ.
    
    Formato: NNNNNNN-DD.AAAA.J.TR.OOOO
    """
    clean = re.sub(r'\D', '', number)
    if len(clean) != 20:
        return False
    
    # Validação do dígito verificador
    nnnnnnn = clean[0:7]
    dd = clean[7:9]
    aaaa = clean[9:13]
    
    # Cálculo do dígito verificador
    numero_base = nnnnnnn + aaaa + clean[13:]
    resto = int(numero_base) % 97
    dv_calculado = 98 - resto
    
    return int(dd) == dv_calculado


def validate_cpf(cpf: str) -> bool:
    """Valida CPF."""
    cpf = re.sub(r'\D', '', cpf)
    
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    
    # Validação dos dígitos verificadores
    for i in range(9, 11):
        value = sum((int(cpf[num]) * ((i+1) - num) for num in range(0, i)))
        digit = ((value * 10) % 11) % 10
        if digit != int(cpf[i]):
            return False
    
    return True


def validate_cnpj(cnpj: str) -> bool:
    """Valida CNPJ."""
    cnpj = re.sub(r'\D', '', cnpj)
    
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False
    
    # Validação dos dígitos verificadores
    def calc_digit(cnpj_partial, weights):
        sum_val = sum(int(cnpj_partial[i]) * weights[i] for i in range(len(weights)))
        remainder = sum_val % 11
        return 0 if remainder < 2 else 11 - remainder
    
    weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    
    digit1 = calc_digit(cnpj[:12], weights1)
    digit2 = calc_digit(cnpj[:13], weights2)
    
    return cnpj[-2:] == f"{digit1}{digit2}"