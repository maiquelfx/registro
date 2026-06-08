import re

def extrair_nomes(arquivo_entrada, arquivo_saida):
    nomes = []

    with open(arquivo_entrada, "r", encoding="utf-8") as f:
        for linha in f:
            # Ignora linhas vazias
            if not linha.strip():
                continue

            # Remove espaços extras e usa regex para capturar o nome
            # Padrão esperado: #NUM  NOME  %
            match = re.search(r"#\d+\s+([A-ZÇÃÉÊÍÓÔÚ]+)", linha)
            if match:
                nomes.append(match.group(1).title())

    # Gera o formato: Nome1, Nome2, Nome3, ...
    resultado = ", ".join(nomes)

    with open(arquivo_saida, "w", encoding="utf-8") as f:
        f.write(resultado)

    print(f"{len(nomes)} nomes extraídos com sucesso.")


# Exemplo de uso
extrair_nomes("nomes-2.txt", "nomes2.txt")