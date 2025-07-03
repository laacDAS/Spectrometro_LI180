# SCRIPT PARA GERAR TABELA DE DADOS FOTOBIOLÓGICOS
#
# Este script lê os arquivos de espectro das luminárias monocromáticas,
# calcula métricas fotobiológicas (PPFD, PFD, etc.) e gera uma tabela
# HTML formatada com os resultados.

# Carregar pacotes necessários
if (!require("pacman")) {
  install.packages("pacman")
}
pacman::p_load(tidyverse, gt, here)

# Carregar funções personalizadas (onde os cálculos são definidos)
# Certifique-se de que functions.R contém a função 'calcular_dados_fotobiologicos'
source(here::here("plot_spectra", "functions.R"))

# 1. Definir o caminho para os dados das luminárias
caminho_dados <- here::here(
  "plot_spectra",
  "dados",
  "Spectros",
  "Luminarias_monocromaticas"
)

# 2. Listar todos os arquivos .txt no diretório
arquivos_luminarias <- list.files(
  path = caminho_dados,
  pattern = "\\.txt$",
  full.names = TRUE
)

# 3. Processar cada arquivo e combinar os resultados em um único data frame
# A função 'calcular_dados_fotobiologicos' deve ser definida em 'functions.R'.
# Ela deve receber um caminho de arquivo e retornar um data frame/tibble com uma linha.
dados_completos <- map_dfr(arquivos_luminarias, calcular_dados_fotobiologicos)

# 4. Criar a tabela formatada com o pacote 'gt'
tabela_gt <- dados_completos %>%
  # Ordenar os dados para melhor visualização
  arrange(tipo_luz, identificador_luminaria, PPFD) %>%
  gt() %>%
  tab_header(
    title = "Dados de intensidades das luminárias monocromáticas do LAAC"
  ) %>%
  fmt_number(columns = where(is.numeric), decimals = 2) %>%
  cols_label(
    arquivo_origem = "Arquivo",
    tipo_luz = "Tipo de Luz",
    identificador_luminaria = "ID Luminária"
  )

# 5. Salvar a tabela como um arquivo HTML na raiz do projeto
output_path <- here::here("tabela_fotobiologica.html")
gtsave(tabela_gt, filename = output_path)

message("Tabela salva com sucesso em: ", output_path)
