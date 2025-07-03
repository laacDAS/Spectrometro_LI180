# Guia de Uso: Análise de Espectros (plot_spectra)

Esta pasta contém os scripts em R para a análise e visualização de dados espectrais coletados com o espectrômetro LI-180. As principais funcionalidades incluem a comparação de espectros de ambientes com espectros de referência (pigmentos) e a geração de uma tabela com dados fotobiológicos para luminárias monocromáticas.

## 📋 Pré-requisitos

Certifique-se de que o R e o RStudio (recomendado) estão instalados. Além disso, os seguintes pacotes R são necessários. Instale-os executando o comando abaixo no console do R:

```r
install.packages(c("tidyverse", "readxl", "data.table", "ggplot2", "here", "gridExtra", "gt", "glue", "janitor"))
```

## 📁 Estrutura de Arquivos

- **`main.R`**: Script principal que orquestra a leitura, processamento e plotagem dos espectros.
- **`functions.R`**: Contém as funções auxiliares, como `plot_spectrometer_laac` e `process_reference_spectrum`.
- **`gerar_tabela_fotobiologica.R`**: Script dedicado para criar a tabela de resumo com dados fotobiológicos.
- **`spectrometer_sun.R`**: Script específico para análise de espectros solares.
- **`dados/`**: Diretório para armazenar os dados brutos e de referência.
  - `spectros_referencia.xlsx`: Planilha com os espectros de referência (ex: Clorofila a, b).
  - `Spectros/`: Subpasta contendo os espectros medidos (ex: `RoomA/`, `RoomB/`).
- **`outputs/`**: Diretório onde os gráficos gerados (`.png`) são salvos.
- **`tabela_fotobiologica.html`**: Arquivo HTML gerado com o resumo dos dados fotobiológicos.

## 🚀 Como Usar

### 1. Preparação dos Dados

- **Espectros de Referência:** Adicione ou modifique os espectros de referência na planilha `dados/spectros_referencia.xlsx`. O script `main.R` irá processar este arquivo e criar um `reference_spectra.RDS` para acesso mais rápido na primeira execução.
- **Dados Medidos:** Coloque seus arquivos de espectro (`.txt`) nas subpastas apropriadas dentro de `dados/Spectros/`.

### 2. Execução do Script de Análise de Espectros

1.  Abra o projeto no RStudio.
2.  Abra o arquivo `main.R`.
3.  Modifique o vetor `Rooms` para incluir os caminhos dos arquivos de dados que você deseja analisar.
4.  Execute o script (pressionando `Ctrl+Shift+Enter` ou usando o botão "Source").
5.  Os gráficos de comparação serão gerados e salvos na pasta `outputs/`.

### 3. Geração da Tabela Fotobiológica

Uma das principais funcionalidades é a geração de uma tabela HTML (`tabela_fotobiologica.html`) que resume os dados fotobiológicos (PPFD, PFD, e PFD por faixa de luz) para as luminárias monocromáticas.

#### Como gerar:

Para gerar a tabela, basta executar o script `gerar_tabela_fotobiologica.R`.

1.  Abra o projeto no RStudio.
2.  Abra o arquivo `gerar_tabela_fotobiologica.R`.
3.  Execute o script (pressionando `Ctrl+Shift+Enter` ou usando o botão "Source").

**Saída:** O arquivo `tabela_fotobiologica.html` será criado ou atualizado na pasta principal do projeto, contendo um resumo detalhado das medições.

### Gerar etiquetas para cada luminária
Para gerar etiquetas para cada luminária, você pode usar o script `etiquetas.R`.

#### Como gerar:

1.  Abra o projeto no RStudio.
2.  Abra o arquivo `etiquetas.R`.
3.  Execute o script (pressionando `Ctrl+Shift+Enter` ou usando o botão "Source").

**Saída:** O script irá gerar arquivos de etiqueta (provavelmente em formato PDF ou imagem) para cada luminária, contendo informações relevantes como o nome da luminária e dados fotobiológicos.

## ⚙️ Personalização

- **Arquivos de Entrada:** Altere os caminhos no vetor `Rooms` em `main.R` para analisar diferentes conjuntos de dados.
- **Gráficos:** No `main.R`, você pode escolher quais espectros de referência plotar, alterando as chamadas à função `plot_spectrometer_laac`. Os parâmetros como título (`plot_title`) e suavização da curva (`span`) também podem ser ajustados diretamente na chamada da função.