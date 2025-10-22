#%% [1. Setup e Configuração]
# Importação das bibliotecas necessárias
import pandas as pd
import os

# --- Configurações do Projeto ---

# Caminho relativo para a pasta de dados brutos
caminho_base = "dados" 

# Ano de referência para a análise (ex: "vct_2024")
ano_analise = "vct_2024" 

# Caminho de destino para os arquivos processados
pasta_limpa = "dados_limpos"

# ----------------------------------


#%% [2. Carregamento dos Dados]
# Monta os caminhos completos para os arquivos de origem
caminho_agents = os.path.join(caminho_base, ano_analise, "agents")
caminho_player_stats = os.path.join(caminho_base, ano_analise, "players_stats")

print(f"Iniciando carregamento dos dados de '{ano_analise}'...")

try:
    # Carrega os datasets brutos
    arquivo_mapas = os.path.join(caminho_agents, "maps_stats.csv")
    arquivo_agentes = os.path.join(caminho_agents, "agents_pick_rates.csv")
    arquivo_jogadores = os.path.join(caminho_player_stats, "players_stats.csv")

    df_mapas = pd.read_csv(arquivo_mapas)
    df_agentes = pd.read_csv(arquivo_agentes)
    df_jogadores = pd.read_csv(arquivo_jogadores)
    
    print("Arquivos carregados com sucesso.")

except FileNotFoundError as e:
    print(f"--- ERRO: Arquivo não encontrado! ---")
    print(f"O Python não conseguiu encontrar o arquivo no caminho: {e.filename}")


#%% [3. Verificação Inicial dos Dados]
# Verificação rápida da estrutura e tipos de dados (Data Discovery)

print("\n--- Verificação df_mapas ---")
df_mapas.info()
print(df_mapas.head())

print("\n--- Verificação df_agentes ---")
df_agentes.info()
print(df_agentes.head())

print("\n--- Verificação df_jogadores ---")
df_jogadores.info()
print(df_jogadores.head())


#%% [4.1. Limpeza - df_mapas]
print("\n--- Processando df_mapas... ---")

# Colunas de % estão como 'object' (string). Precisam ser numéricas.
# Força a coluna para string (garante) antes de usar .str.replace()
df_mapas['Attacker Side Win Percentage'] = df_mapas['Attacker Side Win Percentage'].astype(str).str.replace('%', '')
df_mapas['Defender Side Win Percentage'] = df_mapas['Defender Side Win Percentage'].astype(str).str.replace('%', '')

# Converte para numérico. 'errors='coerce'' transforma textos inválidos (ex: 'NaN') em Nulo.
df_mapas['Attacker Side Win Percentage'] = pd.to_numeric(df_mapas['Attacker Side Win Percentage'], errors='coerce')
df_mapas['Defender Side Win Percentage'] = pd.to_numeric(df_mapas['Defender Side Win Percentage'], errors='coerce')

# Feature Engineering: Cria nova feature 'diferenca_percentual' para análise de desequilíbrio
df_mapas['diferenca_percentual'] = abs(df_mapas['Attacker Side Win Percentage'] - df_mapas['Defender Side Win Percentage'])

# Preenche valores nulos (NaN) gerados pelo 'coerce' com 0
df_mapas = df_mapas.fillna(0)

print("df_mapas limpo.")
print(df_mapas[['Map', 'Attacker Side Win Percentage', 'Defender Side Win Percentage', 'diferenca_percentual']].head())


#%% [4.2. Limpeza - df_agentes]
print("\n--- Processando df_agentes... ---")

# Limpeza da coluna 'Pick Rate' (mesmo processo do df_mapas)
df_agentes['Pick Rate'] = df_agentes['Pick Rate'].astype(str).str.replace('%', '')
df_agentes['Pick Rate'] = pd.to_numeric(df_agentes['Pick Rate'], errors='coerce')
df_agentes = df_agentes.fillna(0)

print("df_agentes limpo.")
print(df_agentes[['Agent', 'Pick Rate']].head())


#%% [4.3. Limpeza - df_jogadores]
print("\n--- Processando df_jogadores... ---")

# Limpeza das colunas de porcentagem
df_jogadores['Headshot %'] = df_jogadores['Headshot %'].astype(str).str.replace('%', '')
df_jogadores['Clutch Success %'] = df_jogadores['Clutch Success %'].astype(str).str.replace('%', '')

# Conversão para numérico
df_jogadores['Kills:Deaths'] = pd.to_numeric(df_jogadores['Kills:Deaths'], errors='coerce')
df_jogadores['Headshot %'] = pd.to_numeric(df_jogadores['Headshot %'], errors='coerce')
df_jogadores['Clutch Success %'] = pd.to_numeric(df_jogadores['Clutch Success %'], errors='coerce')

# Renomeia colunas para facilitar o BI (sem espaços ou caracteres especiais)
df_jogadores = df_jogadores.rename(columns={
    'Kills:Deaths': 'KDRatio',
    'Headshot %': 'Headshot_Pct',
    'Clutch Success %': 'Clutch_Pct',
    'Average Combat Score': 'ACS',
    'Rounds Played': 'Rounds_Played'
})

# Garante que não há nulos nas colunas numéricas após a conversão
cols_numericas_jogadores = ['KDRatio', 'Headshot_Pct', 'Clutch_Pct', 'Rating', 'ACS']
df_jogadores[cols_numericas_jogadores] = df_jogadores[cols_numericas_jogadores].fillna(0)

print("df_jogadores limpo e colunas renomeadas.")
print(df_jogadores[['Player', 'Rating', 'ACS', 'KDRatio', 'Headshot_Pct']].head())


#%% [5. Exportação dos Dados Limpos]
print("\n--- Exportando arquivos limpos... ---")

# Prepara a pasta de destino para os dados limpos
if not os.path.exists(pasta_limpa):
    os.makedirs(pasta_limpa)
    print(f"Pasta '{pasta_limpa}' criada.")

try:
    # Salva os arquivos processados na pasta de destino
    df_mapas.to_csv(os.path.join(pasta_limpa, "mapas_limpo.csv"), index=False)
    df_agentes.to_csv(os.path.join(pasta_limpa, "agentes_limpo.csv"), index=False)
    df_jogadores.to_csv(os.path.join(pasta_limpa, "jogadores_limpo.csv"), index=False)
    
    print(f"SUCESSO! 3 arquivos limpos foram salvos na pasta: '{pasta_limpa}'")
    print("Próximo passo: Power BI.")

except Exception as e:
    print(f"ERRO ao salvar arquivos: {e}")