# -*- coding: utf-8 -*-
"""
Created on Fri Feb 13 16:05:08 2026
@author: Win
"""

import unicodedata
import csv
import re
from collections import defaultdict

# ================= CONFIGURAÇÃO DE ENTRADA E SAÍDA =================
fonte = '11-08-2026.txt'
entrada = [
    'profissoes.txt',
    'subs.txt',
    'tecnologia.txt',
    'nomes_saida.txt',
    'ingles.txt',
    'ai.txt',
]
resultcsv = '11-08-2026-v2.csv'
# ===================================================================


def limpar_texto(texto):
    """
    Remove acentos, cedilha, espaços e caracteres especiais.
    Retorna apenas letras e números em minúsculo.
    
    Exemplos:
        'médico'                  -> 'medico'
        'engenheiro de software'  -> 'engenheirodesoftware'
        'segurança da informação' -> 'segurancadainformacao'
    """
    texto = texto.strip().lower()

    # Remove acentos
    nfkd = unicodedata.normalize('NFKD', texto)
    texto = "".join(
        c for c in nfkd
        if not unicodedata.combining(c)
    )

    # Remove qualquer coisa que não seja letra ou número
    texto = re.sub(r'[^a-z0-9]', '', texto)

    return texto


def extrair_nomes(conteudo):
    """
    Extrai termos preservando expressões com várias palavras.

    Aceita arquivos como:
        médico, enfermeiro, dentista
        engenheiro de software, cientista de dados

    Também aceita um termo por linha.
    """
    # Primeiro transforma quebras de linha em vírgulas
    conteudo = conteudo.replace('\n', ',')

    # Divide somente por vírgulas
    termos = conteudo.split(',')

    nomes = set()

    for termo in termos:
        termo = termo.strip()

        if termo:
            nome = limpar_texto(termo)

            if nome:
                nomes.add(nome)

    return nomes


# 1. Carregando e unificando os nomes
print("Carregando nomes...")

nomes = set()

for arquivo in entrada:
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()

        nomes.update(extrair_nomes(conteudo))

        print(f"✓ '{arquivo}' carregado")

    except FileNotFoundError:
        print(f"⚠ '{arquivo}' não encontrado")


print(f"Total de nomes únicos: {len(nomes):,}")


# 2. Carregando domínios
print(f"\nCarregando domínios de '{fonte}'...")

try:
    with open(fonte, 'r', encoding='utf-8') as f:
        dominios = [
            line.strip().lower()
            for line in f
            if line.strip()
        ]

except FileNotFoundError:
    print(f"Erro: '{fonte}' não encontrado")
    exit()


print(f"Total de domínios: {len(dominios):,}")


# 3. OTIMIZAÇÃO:
# Criar índice de nomes por tamanho para busca mais rápida

print("\nProcessando correspondências...")

nomes_por_tamanho = defaultdict(set)

for nome in nomes:
    nomes_por_tamanho[len(nome)].add(nome)


dados_planilha = []
processados = 0
total = len(dominios)


# 4. Processando domínios
for dom in dominios:

    processados += 1

    if processados % 10000 == 0:
        print(
            f"  Processados: {processados:,}/{total:,} "
            f"({100 * processados / total:.1f}%)"
        )

    # Divide apenas no primeiro ponto.
    # Exemplo:
    # engenheirodesoftware.com.br
    # corpo = engenheirodesoftware
    # tld   = com.br
    partes = dom.split('.', 1)

    corpo_original = partes[0]
    tld = partes[1] if len(partes) > 1 else ""

    # Normaliza também o domínio para garantir comparação consistente
    corpo_dominio = limpar_texto(corpo_original)

    if not corpo_dominio:
        continue


    # ==============================================================
    # CORRESPONDÊNCIA EXATA
    # ==============================================================
    if corpo_dominio in nomes:

        dados_planilha.append([
            corpo_dominio,
            dom,
            tld,
            "Exata"
        ])


    # ==============================================================
    # CORRESPONDÊNCIA PARCIAL
    # ==============================================================
    else:

        encontrou = False

        # Procura primeiro nomes maiores, pois são mais específicos.
        # Exemplo:
        # 'engenheirodesoftware'
        #
        # prefere:
        # 'engenheirodesoftware'
        #
        # em vez de simplesmente:
        # 'engenheiro'
        for tamanho in sorted(
            nomes_por_tamanho.keys(),
            reverse=True
        ):

            # Se o nome for maior que o domínio, não cabe
            if tamanho > len(corpo_dominio):
                continue

            for nome in nomes_por_tamanho[tamanho]:

                if nome in corpo_dominio:

                    dados_planilha.append([
                        nome,
                        dom,
                        tld,
                        "Parcial"
                    ])

                    encontrou = True
                    break

            if encontrou:
                break


# 5. Salvando resultados
print("\nSalvando resultados...")

with open(
    resultcsv,
    'w',
    newline='',
    encoding='utf-8-sig'
) as f:

    writer = csv.writer(
        f,
        delimiter=';'
    )

    writer.writerow([
        'Nome',
        'Dominio Completo',
        'TLD',
        'Tipo de Correspondencia'
    ])

    writer.writerows(dados_planilha)


# 6. Resumo
print(f"\n{'=' * 50}")
print("✓ Processamento Finalizado!")
print(f"  Nomes únicos: {len(nomes):,}")
print(f"  Domínios processados: {len(dominios):,}")
print(
    f"  Correspondências encontradas: "
    f"{len(dados_planilha):,}"
)
print(f"  Arquivo gerado: {resultcsv}")
print(f"{'=' * 50}")
