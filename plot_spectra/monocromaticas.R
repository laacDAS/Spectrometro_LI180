rm(list = ls())
options(scipen = 999)

if (!require(pacman, quietly = TRUE)) {
  install.packages("pacman")
  library(pacman)
}

pacman::p_load(
  update = T,
  "tidyverse",
  "readr",
  "here",
  "ggspectra",
  "ggrepel",
  "photobiologyWavebands",
  "janitor",
  "readxl"
)

# Deep BLue - DB ---------------------------------------------------------

deep_blue_4_0 <- readr::read_table("dados_monocromaticas/DB/uMOL_4DB0.txt") |>
  janitor::clean_names() |>
  dplyr::select(wavelength_nm, pfd_umol) |>
  dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
  photobiology::as.source_spct()

deep_blue_4_100 <- readr::read_table(
  "dados_monocromaticas/DB/uMOL_4DB100.txt"
) |>
  janitor::clean_names() |>
  dplyr::select(wavelength_nm, pfd_umol) |>
  dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
  photobiology::as.source_spct()

deep_blue_5_0 <- readr::read_table("dados_monocromaticas/DB/uMOL_5DB0.txt") |>
  janitor::clean_names() |>
  dplyr::select(wavelength_nm, pfd_umol) |>
  dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
  photobiology::as.source_spct()

deep_blue_5_100 <- readr::read_table(
  "dados_monocromaticas/DB/uMOL_5DB100.txt"
) |>
  janitor::clean_names() |>
  dplyr::select(wavelength_nm, pfd_umol) |>
  dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
  photobiology::as.source_spct()

deep_blue_6_0 <- readr::read_table("dados_monocromaticas/DB/uMOL_6DB0.txt") |>
  janitor::clean_names() |>
  dplyr::select(wavelength_nm, pfd_umol) |>
  dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
  photobiology::as.source_spct()

deep_blue_6_100 <- readr::read_table(
  "dados_monocromaticas/DB/uMOL_6DB100.txt"
) |>
  janitor::clean_names() |>
  dplyr::select(wavelength_nm, pfd_umol) |>
  dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
  photobiology::as.source_spct()

deep_blue_7_0 <- readr::read_table("dados_monocromaticas/DB/uMOL_7DB0.txt") |>
  janitor::clean_names() |>
  dplyr::select(wavelength_nm, pfd_umol) |>
  dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
  photobiology::as.source_spct()

deep_blue_7_100 <- readr::read_table(
  "dados_monocromaticas/DB/uMOL_7DB100.txt"
) |>
  janitor::clean_names() |>
  dplyr::select(wavelength_nm, pfd_umol) |>
  dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
  photobiology::as.source_spct()

# Far Red - FR -----------------------------------------------------------

far_red_13_0 <- readr::read_table(
  "dados_monocromaticas/FR/uMOL_13FR0.txt"
) |>
  janitor::clean_names() |>
  dplyr::select(wavelength_nm, pfd_umol) |>
  dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
  photobiology::as.source_spct()

far_red_13_100 <- readr::read_table(
  "dados_monocromaticas/FR/uMOL_13FR100.txt"
) |>
  janitor::clean_names() |>
  dplyr::select(wavelength_nm, pfd_umol) |>
  dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
  photobiology::as.source_spct()

far_red_14_0 <- readr::read_table(
  "dados_monocromaticas/FR/uMOL_14FR0.txt"
) |>
  janitor::clean_names() |>
  dplyr::select(wavelength_nm, pfd_umol) |>
  dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
  photobiology::as.source_spct()

far_red_14_100 <- readr::read_table(
  "dados_monocromaticas/FR/uMOL_14FR100.txt"
) |>
  janitor::clean_names() |>
  dplyr::select(wavelength_nm, pfd_umol) |>
  dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
  photobiology::as.source_spct()

# Green - G --------------------------------------------------------------

green_8_0 <- readr::read_table(
  "dados_monocromaticas/G/uMOL_8G0.txt"
) |>
  janitor::clean_names() |>
  dplyr::select(wavelength_nm, pfd_umol) |>
  dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
  photobiology::as.source_spct()

green_8_100 <- readr::read_table(
  "dados_monocromaticas/G/uMOL_8G100.txt"
) |>
  janitor::clean_names() |>
  dplyr::select(wavelength_nm, pfd_umol) |>
  dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
  photobiology::as.source_spct()


# Ultravioleta - UVA -----------------------------------------------------

uva_3_0 <- readr::read_table(
  "dados_monocromaticas/UVA/uMOL_3UVA0.txt"
) |>
  janitor::clean_names() |>
  dplyr::select(wavelength_nm, pfd_umol) |>
  dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
  photobiology::as.source_spct()

uva_3_100 <- readr::read_table(
  "dados_monocromaticas/UVA/uMOL_3UVA100.txt"
) |>
  janitor::clean_names() |>
  dplyr::select(wavelength_nm, pfd_umol) |>
  dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
  photobiology::as.source_spct()

# Hiper Red - HR ---------------------------------------------------------

hiper_red_9_0 <- readr::read_table(
  "dados_monocromaticas/HR/uMOL_9HR0.txt"
) |>
  janitor::clean_names() |>
  dplyr::select(wavelength_nm, pfd_umol) |>
  dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
  photobiology::as.source_spct()

hiper_red_9_100 <- readr::read_table(
  "dados_monocromaticas/HR/uMOL_9HR100.txt"
) |>
  janitor::clean_names() |>
  dplyr::select(wavelength_nm, pfd_umol) |>
  dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
  photobiology::as.source_spct()

hiper_red_10_0 <- readr::read_table(
  "dados_monocromaticas/HR/uMOL_10HR0.txt"
) |>
  janitor::clean_names() |>
  dplyr::select(wavelength_nm, pfd_umol) |>
  dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
  photobiology::as.source_spct()

hiper_red_10_100 <- readr::read_table(
  "dados_monocromaticas/HR/uMOL_10HR100.txt"
) |>
  janitor::clean_names() |>
  dplyr::select(wavelength_nm, pfd_umol) |>
  dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
  photobiology::as.source_spct()

hiper_red_11_0 <- readr::read_table(
  "dados_monocromaticas/HR/uMOL_11HR0.txt"
) |>
  janitor::clean_names() |>
  dplyr::select(wavelength_nm, pfd_umol) |>
  dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
  photobiology::as.source_spct()

hiper_red_11_100 <- readr::read_table(
  "dados_monocromaticas/HR/uMOL_11HR100.txt"
) |>
  janitor::clean_names() |>
  dplyr::select(wavelength_nm, pfd_umol) |>
  dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
  photobiology::as.source_spct()

hiper_red_12_0 <- readr::read_table(
  "dados_monocromaticas/HR/uMOL_12HR0.txt"
) |>
  janitor::clean_names() |>
  dplyr::select(wavelength_nm, pfd_umol) |>
  dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
  photobiology::as.source_spct()

hiper_red_12_100 <- readr::read_table(
  "dados_monocromaticas/HR/uMOL_12HR100.txt"
) |>
  janitor::clean_names() |>
  dplyr::select(wavelength_nm, pfd_umol) |>
  dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
  photobiology::as.source_spct()


# white - W --------------------------------------------------------------

white_1_0 <- readr::read_table(
  "dados_monocromaticas/W/uMOL_1W0.txt"
) |>
  janitor::clean_names() |>
  dplyr::select(wavelength_nm, pfd_umol) |>
  dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
  photobiology::as.source_spct()

white_1_100 <- readr::read_table(
  "dados_monocromaticas/W/uMOL_1W100.txt"
) |>
  janitor::clean_names() |>
  dplyr::select(wavelength_nm, pfd_umol) |>
  dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
  photobiology::as.source_spct()

white_2_0 <- readr::read_table(
  "dados_monocromaticas/W/uMOL_2W0.txt"
) |>
  janitor::clean_names() |>
  dplyr::select(wavelength_nm, pfd_umol) |>
  dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
  photobiology::as.source_spct()

white_2_100 <- readr::read_table(
  "dados_monocromaticas/W/uMOL_2W100.txt"
) |>
  janitor::clean_names() |>
  dplyr::select(wavelength_nm, pfd_umol) |>
  dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
  photobiology::as.source_spct()


# funções de gráfico -----------------------------------------------------

# Carregando pacotes necessários
library(tidyverse)
library(readr)
library(stringr)
library(photobiology)
library(photobiologyWavebands)
library(ggspectra)

# Caminho base para os arquivos ESPD e espectros
caminho_base <- "C:/Users/jarde/OneDrive/Documentos/GitHub/Spectrometro_LI180/plot_spectra/dados_monocromaticas/ESPD"

# Dicionário de nomes amigáveis
nomes_amigaveis <- c(
  "uva_3" = "Ultravioleta A | Luminária 3",
  "deep_blue_4" = "Deep Blue | Luminária 4",
  "deep_blue_5" = "Deep Blue | Luminária 5",
  "deep_blue_6" = "Deep Blue | Luminária 6",
  "deep_blue_7" = "Deep Blue | Luminária 7",
  "green_8" = "Verde | Luminária 8",
  "hiper_red_9" = "Hiper Red | Luminária 9",
  "hiper_red_10" = "Hiper Red | Luminária 10",
  "hiper_red_11" = "Hiper Red | Luminária 11",
  "hiper_red_12" = "Hiper Red | Luminária 12",
  "far_red_13" = "Far Red | Luminária 13",
  "far_red_14" = "Far Red | Luminária 14",
  "white_1" = "Branca | Luminária 1",
  "white_2" = "Branca | Luminária 2"
)

# Função para ler valores fotobiológicos dos arquivos ESPD
ler_dados_espd <- function(caminho) {
  linhas <- read_lines(caminho)
  dados_luz <- linhas[str_detect(
    linhas,
    "^(PPFD|PFD|PFD-UV|PFD-B|PFD-G|PFD-R|PFD-FR)\\t"
  )]
  valores <- str_split_fixed(dados_luz, "\\t", 2)
  nomes <- valores[, 1]
  valores_num <- as.numeric(valores[, 2])
  names(valores_num) <- nomes
  return(valores_num)
}

# Função principal para plotar pares _0 e _100 com dados no subtítulo
plot_pares <- function(prefixo) {
  obj_0 <- get(paste0(prefixo, "_0"), envir = .GlobalEnv)
  obj_100 <- get(paste0(prefixo, "_100"), envir = .GlobalEnv)
  mspct <- source_mspct(list(`0%` = obj_0, `100%` = obj_100))

  titulo <- ifelse(
    prefixo %in% names(nomes_amigaveis),
    nomes_amigaveis[[prefixo]],
    prefixo
  )

  caminho_espd_0 <- list.files(
    path = caminho_base,
    recursive = TRUE,
    full.names = TRUE,
    pattern = paste0("ESPD_.*", toupper(prefixo), "0\\.txt")
  )
  caminho_espd_100 <- list.files(
    path = caminho_base,
    recursive = TRUE,
    full.names = TRUE,
    pattern = paste0("ESPD_.*", toupper(prefixo), "100\\.txt")
  )

  legenda_extra <- ""
  if (length(caminho_espd_0) == 1 && length(caminho_espd_100) == 1) {
    dados_0 <- ler_dados_espd(caminho_espd_0)
    dados_100 <- ler_dados_espd(caminho_espd_100)

    legenda_extra <- sprintf(
      "PPFD (0%%): %.2f | PPFD (100%%): %.2f\nB: %.2f | G: %.2f | R: %.2f | FR: %.2f",
      dados_0["PPFD"],
      dados_100["PPFD"],
      dados_100["PFD-B"],
      dados_100["PFD-G"],
      dados_100["PFD-R"],
      dados_100["PFD-FR"]
    )
  }

  g <- autoplot(
    mspct,
    unit.out = "photon",
    idfactor = "spct.names",
    w.band = VIS_bands("ISO"),
    annotations = c("+", "peak.labels", "valley.labels"),
    span = 15,
    text.size = 4,
    label.qty = "contribution.pc"
  ) +
    labs(title = titulo, subtitle = legenda_extra) +
    scale_x_continuous(expand = expansion(mult = c(0, 0.01))) +
    theme(legend.position = "bottom")

  return(g)
}

# Lista de prefixos únicos
prefixos <- c(
  "uva_3",
  "deep_blue_4",
  "deep_blue_5",
  "deep_blue_6",
  "deep_blue_7",
  "green_8",
  "hiper_red_9",
  "hiper_red_10",
  "hiper_red_11",
  "hiper_red_12",
  "far_red_13",
  "far_red_14",
  "white_1",
  "white_2"
)

# Criar diretório de saída
dir.create("graficos_pares_png", showWarnings = FALSE)

# Salvar gráficos em PNG
for (prefixo in prefixos) {
  g <- plot_pares(prefixo)
  ggsave(
    filename = paste0("graficos_pares_png/", prefixo, ".png"),
    plot = g,
    width = 14,
    height = 6,
    dpi = 300
  )
}

# Salvar todos os gráficos em um único PDF
pdf("graficos_pares.pdf", width = 14, height = 6)

for (prefixo in prefixos) {
  g <- plot_pares(prefixo)
  print(g)
}

dev.off()

# Seção deestração de dados dos ESPD e montagem de tabela ---------------

#' Extrai dados fotobiológicos de um único arquivo ESPD.
#'
#' @param caminho_arquivo O caminho completo para o arquivo .txt do ESPD.
#' @return Um tibble (data.frame) com uma linha contendo os dados extraídos e o nome do arquivo.
processar_arquivo_espd <- function(caminho_arquivo) {
  # Ler as linhas do arquivo
  linhas <- readr::read_lines(caminho_arquivo)

  # Métricas que queremos extrair
  metricas_alvo <- c(
    "PPFD",
    "PFD",
    "PFD-UV",
    "PFD-B",
    "PFD-G",
    "PFD-R",
    "PFD-FR"
  )

  # Criar o padrão regex para encontrar as linhas (início da linha + métrica + tab)
  padrao_regex <- paste0("^(", paste(metricas_alvo, collapse = "|"), ")\\t")

  # Filtrar as linhas que contêm os dados de interesse
  dados_luz <- linhas[stringr::str_detect(linhas, padrao_regex)]

  # Se não encontrar dados, retorna NULL para ser ignorado pelo map_dfr
  if (length(dados_luz) == 0) {
    return(NULL)
  }

  # Separar nome da métrica e valor
  valores_split <- stringr::str_split_fixed(dados_luz, "\\t", 2)

  # Converte a matriz de valores para uma lista nomeada e depois para um tibble
  valores_num <- as.numeric(valores_split[, 2])
  names(valores_num) <- valores_split[, 1]

  dados_df <- tibble::as_tibble(as.list(valores_num))

  # Adicionar o nome do arquivo como identificador na primeira coluna
  dados_df <- dados_df |>
    dplyr::mutate(
      arquivo_origem = basename(caminho_arquivo),
      .before = 1
    )

  return(dados_df)
}

#' Processa todos os arquivos ESPD em um diretório e gera uma tabela CSV.
#'
#' @param caminho_diretorio O caminho para o diretório raiz que contém os arquivos ESPD (pode estar em subpastas).
#' @param arquivo_saida_csv O nome do arquivo CSV a ser criado.
#' @param nomes_map Um vetor nomeado para mapear prefixos de arquivo para nomes amigáveis.
#' @return Retorna a tabela completa de dados de forma invisível.
gerar_tabela_fotobiologica_csv <- function(
  caminho_diretorio,
  arquivo_saida_csv,
  nomes_map
) {
  arquivos_espd <- list.files(
    path = caminho_diretorio,
    pattern = "^ESPD_.*\\.txt$",
    recursive = TRUE,
    full.names = TRUE
  )

  if (length(arquivos_espd) == 0) {
    warning("Nenhum arquivo ESPD encontrado no diretório: ", caminho_diretorio)
    return(invisible(NULL))
  }

  # Gera uma tabela de consulta (lookup table) a partir dos nomes amigáveis
  # Mapeia um código de arquivo (ex: "4DB") para um nome amigável (ex: "Deep Blue | Luminária 4")
  file_codes <- names(nomes_map) |>
    purrr::map_chr(
      ~ {
        parts <- stringr::str_split(.x, "_")[[1]]
        number <- parts[length(parts)]
        color_words <- parts[1:(length(parts) - 1)]
        # Casos especiais podem ser tratados aqui
        if (.x == "uva_3") {
          return("3UVA")
        }
        initials <- stringr::str_sub(color_words, 1, 1) |>
          toupper() |>
          paste(collapse = "")
        return(paste0(number, initials))
      }
    )

  lookup_table <- stats::setNames(as.character(nomes_map), file_codes)

  tabela_completa <- purrr::map_dfr(arquivos_espd, processar_arquivo_espd)

  # Adiciona colunas com nomes amigáveis, separa em tipo e identificador, e reordena
  tabela_completa <- tabela_completa |>
    dplyr::mutate(
      file_code = stringr::str_remove_all(
        arquivo_origem,
        "ESPD_|(0|10|100)\\.txt$"
      ),
      luminaria_completa = lookup_table[file_code],
      .after = arquivo_origem
    ) |>
    dplyr::select(-file_code) |>
    tidyr::separate(
      col = luminaria_completa,
      into = c("tipo_luz", "identificador_luminaria"),
      sep = "\\s*\\|\\s*",
      remove = TRUE
    )

  readr::write_csv(tabela_completa, arquivo_saida_csv)
  message(paste(
    "Tabela salva com sucesso em:",
    file.path(getwd(), arquivo_saida_csv)
  ))
  return(invisible(tabela_completa))
}

# --- Execução da Extração ---

# Definir o caminho onde os arquivos ESPD estão localizados
caminho_dados_espd <- "C:/Users/jarde/OneDrive/Documentos/GitHub/Spectrometro_LI180/plot_spectra/dados_monocromaticas/"

# Chamar a função para gerar o arquivo CSV "dados_fotobiologicos_compilados.csv"
dados_extraidos <- gerar_tabela_fotobiologica_csv(
  caminho_dados_espd,
  "dados_fotobiologicos_compilados.csv",
  nomes_map = nomes_amigaveis
)

# salvar a tabela em HTML
library(gt)
gt(
  data = dados_extraidos,
  caption = "Dados de intensidades das luminárias monocromáticas do LAAC"
) |>
  gtsave(filename = "tabela_fotobiologica.html")
