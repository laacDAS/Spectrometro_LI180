# Guia de Uso do Sistema de Processamento de Dados LI-180

Os dados são obtidos pelo aparelho LiCor LI-180 Spectometer e devem ser colocados em uma pasta junto com os arquivos python, batch e VBS.

## 1. Coleta e Nomeação dos Arquivos

- Cada coleta de ponto deve seguir a nomenclatura: **XY9IntensidadeCor**.
  - **X**: linha
  - **Y**: coluna
  - **Intensidade**: dimerização da luz
  - **Cor**: combinação de cor usada
  - **9**: usado no lugar de underline, pois o aparelho não possui underline no teclado
- Exemplo de arquivo: **ESPD_429100A** (linha 4, coluna 2, 100% LEDs azuis)

## 2. Organização dos Arquivos

- Coloque todos os arquivos copiados do cartão de memória do LI-180, além dos arquivos `functions.py`, `main.py` e `coordenadas.csv`, em uma mesma pasta.

## 3. Execução do Programa

- Execute o arquivo `main.py` normalmente (via terminal, duplo clique ou como executável).
- Será aberta uma **interface gráfica** com as seguintes opções:

### Opções da Interface

1. **Organizar arquivos por padrão**
    - Move os arquivos para subpastas conforme o padrão de terminação do nome.
    - Arquivos não padronizados podem ser excluídos manualmente.
2. **Extrair coordenadas e valores de subpastas**
    - Extrai coordenadas dos nomes dos arquivos, valores de PFD e PPFD, e utiliza o arquivo `coordenadas.csv` para obter as coordenadas reais.
    - Salva um arquivo `coordenadas_espd.csv` em cada subpasta.
3. **Plotar gráfico 3D simples**
    - Plota um gráfico 3D de pontos usando as coordenadas X (linha), Y (coluna) e Z (PPFD ou PFD).
    - Escolha entre PPFD ou PFD na interface antes de plotar.
4. **Plotar Surface Plot 3D interpolado**
    - Plota uma superfície 3D interpolada para uma pasta selecionada.
    - Escolha entre PPFD ou PFD na interface antes de plotar.
5. **Plotar múltiplas superfícies 3D**
    - Plota superfícies 3D para todas as subpastas encontradas, cada uma representando uma condição de luz.
    - Escolha entre PPFD ou PFD na interface antes de plotar.

## 4. Observações

- O arquivo `coordenadas.csv` deve conter as colunas `linha` e `coluna` com as coordenadas reais dos pontos.
- Os gráficos permitem rotação automática e visualização interativa.
- Para melhor aparência da interface, recomenda-se instalar o pacote `ttkbootstrap` (opcional):

  ```
  pip install ttkbootstrap
  ```

- Para criar um executável, instale o PyInstaller e siga:

  ```
  pip install pyinstaller
  pyinstaller --onefile main.py
  ```