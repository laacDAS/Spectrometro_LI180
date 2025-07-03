library(tidyverse)
library(glue)
library(janitor)
library(gridExtra)
library(grid)

# 1. Ler e limpar os dados
dados <- read_csv("dados_fotobiologicos_compilados.csv") %>%
  clean_names()

# 2. Agrupar e calcular máximos e mínimos
resumo <- dados %>%
  group_by(identificador_luminaria) %>%
  summarise(
    ppfd_max = max(ppfd, na.rm = TRUE),
    ppfd_min = min(ppfd, na.rm = TRUE),
    pfd_max = max(pfd, na.rm = TRUE),
    pfd_min = min(pfd, na.rm = TRUE),
    pfd_uv_max = max(pfd_uv, na.rm = TRUE),
    pfd_uv_min = min(pfd_uv, na.rm = TRUE),
    pfd_b_max = max(pfd_b, na.rm = TRUE),
    pfd_b_min = min(pfd_b, na.rm = TRUE),
    pfd_g_max = max(pfd_g, na.rm = TRUE),
    pfd_g_min = min(pfd_g, na.rm = TRUE),
    pfd_r_max = max(pfd_r, na.rm = TRUE),
    pfd_r_min = min(pfd_r, na.rm = TRUE),
    pfd_fr_max = max(pfd_fr, na.rm = TRUE),
    pfd_fr_min = min(pfd_fr, na.rm = TRUE)
  )

# 3. Criar texto formatado para as etiquetas
resumo <- resumo %>%
  mutate(
    texto = glue(
      "Luminária: {identificador_luminaria}
Valores em µmol m⁻² s⁻¹
Faixa        |   Máx  |   Mín
PPFD         | {sprintf('%6.1f', ppfd_max)} | {sprintf('%6.1f', ppfd_min)}
PFD total    | {sprintf('%6.2f', pfd_max)} | {sprintf('%6.2f', pfd_min)}
UV           | {sprintf('%6.2f', pfd_uv_max)} | {sprintf('%6.2f', pfd_uv_min)}
Blue (B)     | {sprintf('%6.2f', pfd_b_max)} | {sprintf('%6.2f', pfd_b_min)}
Green (G)    | {sprintf('%6.2f', pfd_g_max)} | {sprintf('%6.2f', pfd_g_min)}
Red (R)      | {sprintf('%6.2f', pfd_r_max)} | {sprintf('%6.2f', pfd_r_min)}
Far Red (FR) | {sprintf('%6.2f', pfd_fr_max)} | {sprintf('%6.2f', pfd_fr_min)}"
    )
  )

# 4. Criar objetos gráficos com espaçamento extra
etiquetas_grobs <- lapply(resumo$texto, function(txt) {
  textGrob(
    label = txt,
    gp = gpar(fontsize = 8.5, fontfamily = "mono", lineheight = 1.3),
    just = "left",
    x = 0.05
  )
})

# 5. Layout para etiquetas Avery (3 colunas × 10 linhas)
n_col <- 3
n_row <- 4
por_pagina <- n_col * n_row
n_total <- length(etiquetas_grobs)
n_paginas <- ceiling(n_total / por_pagina)

# 6. Gerar PDF final
pdf("etiquetas_LAAC.pdf", width = 11, height = 8.5) # paisagem

for (pagina in 1:n_paginas) {
  grid.newpage()
  pushViewport(viewport(layout = grid.layout(n_row, n_col)))

  inicio <- (pagina - 1) * por_pagina + 1
  fim <- min(pagina * por_pagina, n_total)
  etiquetas_pag <- etiquetas_grobs[inicio:fim]

  for (i in seq_along(etiquetas_pag)) {
    row <- ceiling(i / n_col)
    col <- ((i - 1) %% n_col) + 1
    vp <- viewport(layout.pos.row = row, layout.pos.col = col)
    pushViewport(vp)
    grid.draw(etiquetas_pag[[i]])
    popViewport()
  }
}

dev.off()
