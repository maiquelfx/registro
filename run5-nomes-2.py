# -*- coding: utf-8 -*-
"""
Created on Fri Feb 13 16:05:08 2026
@author: Win
"""
import unicodedata
import csv
from collections import defaultdict

# ================= CONFIGURAÇÃO DE ENTRADA E SAÍDA =================
fonte = '08-06-2026.txt'
entrada = ['profissoes.txt', 'subs.txt', 'tecnologia.txt', 'nomes_saida.txt', ]  #'subs.txt', 'tecnologia.txt', 'nomes_saida.txt', 'nomes2.txt', 'profissoes.txt'
resultcsv = '08-06-2026.csv'
# ===================================================================

def limpar_texto(texto):
    """Remove acentos, cedilha e converte para minúsculo"""
    nfkd = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).lower().replace('ç', 'c')

# 1. Carregando e unificando os nomes
print("Carregando nomes...")
nomes = set()
for arquivo in entrada:
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read().replace(',', ' ')
            for n in conteudo.split():
                if n.strip():
                    nomes.add(limpar_texto(n))
        print(f"✓ '{arquivo}' carregado")
    except FileNotFoundError:
        print(f"⚠ '{arquivo}' não encontrado")

print(f"Total de nomes únicos: {len(nomes)}")

# 2. Carregando domínios
print(f"\nCarregando domínios de '{fonte}'...")
try:
    with open(fonte, 'r', encoding='utf-8') as f:
        dominios = [line.strip().lower() for line in f if line.strip()]
except FileNotFoundError:
    print(f"Erro: '{fonte}' não encontrado")
    exit()

print(f"Total de domínios: {len(dominios)}")

# 3. OTIMIZAÇÃO: Criar índice de nomes por tamanho para busca mais rápida
print("\nProcessando correspondências...")
nomes_por_tamanho = defaultdict(set)
for nome in nomes:
    nomes_por_tamanho[len(nome)].add(nome)

dados_planilha = []
processados = 0
total = len(dominios)

for dom in dominios:
    processados += 1
    if processados % 10000 == 0:  # Progresso a cada 10k
        print(f"  Processados: {processados:,}/{total:,} ({100*processados/total:.1f}%)")
    
    partes = dom.split('.', 1)
    corpo_dominio = partes[0]
    tld = partes[1] if len(partes) > 1 else ""
    
    # CORRESPONDÊNCIA EXATA (busca O(1) em vez de O(n))
    if corpo_dominio in nomes:
        dados_planilha.append([corpo_dominio, dom, tld, "Exata"])
    
    # CORRESPONDÊNCIA PARCIAL (apenas nomes menores que o domínio)
    else:
        for tamanho in range(1, len(corpo_dominio) + 1):
            if tamanho in nomes_por_tamanho:
                for nome in nomes_por_tamanho[tamanho]:
                    if nome in corpo_dominio:
                        dados_planilha.append([nome, dom, tld, "Parcial"])
                        break  # Encontrou, não precisa continuar

# 4. Salvando resultados
print("\nSalvando resultados...")
with open(resultcsv, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(['Nome', 'Dominio Completo', 'TLD', 'Tipo de Correspondencia'])
    writer.writerows(dados_planilha)

print(f"\n{'='*50}")
print(f"✓ Processamento Finalizado!")
print(f"  Nomes únicos: {len(nomes):,}")
print(f"  Domínios processados: {len(dominios):,}")
print(f"  Correspondências encontradas: {len(dados_planilha):,}")
print(f"  Arquivo gerado: {resultcsv}")
print(f"{'='*50}")