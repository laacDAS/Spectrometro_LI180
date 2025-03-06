# header ------------------------------------------------------------------
rm(list = ls())
options(scipen = 999)

if (!require(pacman, quietly = TRUE)) {
    install.packages("pacman")
    library(pacman)
}

pacman::p_load(
    "tidyverse",
    "readr",
    "here",
    "ggspectra",
    "ggrepel",
    "photobiologyWavebands",
    "janitor",
    "readxl"
)

# imports -----------------------------------------------------------------
d1 <- readr::read_table("dados/sol/uMOL_SOL1.txt") |>
    janitor::clean_names() |>
    dplyr::select(wavelength_nm, pfd_umol) |>
    dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
    photobiology::as.source_spct()

d2 <- readr::read_table("dados/sol/uMOL_sol2.txt") |>
    janitor::clean_names() |>
    dplyr::select(wavelength_nm, pfd_umol) |>
    dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
    photobiology::as.source_spct()

d3 <- readr::read_table("dados/sol/uMOL_sol3.txt") |>
    janitor::clean_names() |>
    dplyr::select(wavelength_nm, pfd_umol) |>
    dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
    photobiology::as.source_spct()

d4 <- readr::read_table("dados/sol/uMOL_SOL4.txt") |>
    janitor::clean_names() |>
    dplyr::select(wavelength_nm, pfd_umol) |>
    dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
    photobiology::as.source_spct()

d5 <- readr::read_table("dados/sol/uMOL_SOL5.txt") |>
    janitor::clean_names() |>
    dplyr::select(wavelength_nm, pfd_umol) |>
    dplyr::rename(s.e.irrad = pfd_umol, w.length = wavelength_nm) |>
    photobiology::as.source_spct()

d_sum <- data.frame(
    w.length = d1$w.length,
    s.e.irrad = d1$s.e.irrad +
        d2$s.e.irrad +
        d3$s.e.irrad +
        d4$s.e.irrad +
        d5$s.e.irrad
) |>
    photobiology::as.source_spct()

d_sum_norm <- data.frame(
    w.length = d1$w.length,
    s.e.irrad = scale(
        d1$s.e.irrad +
            d2$s.e.irrad +
            d3$s.e.irrad +
            d4$s.e.irrad +
            d5$s.e.irrad,
        center = F
    )
) |>
    photobiology::as.source_spct()

chl_a <- read_excel(
    "dados/spectros_referencia.xlsx",
    sheet = "pigmentos",
    range = "A2:B90"
) |>
    janitor::clean_names() |>
    dplyr::rename(s.e.irrad = relative_absorbance, w.length = wavelength_nm) |>
    photobiology::as.source_spct()

B_carot <- read_excel(
    "dados/spectros_referencia.xlsx",
    sheet = "pigmentos",
    range = "E2:F58"
) |>
    janitor::clean_names() |>
    dplyr::rename(s.e.irrad = relative_absorbance, w.length = wavelength_nm) |>
    photobiology::as.source_spct()

# graphics ------------------------------------------------------------------
# espectros hora-a-hora e diário OK
source_mspct(
    list(H08 = d1, H10 = d2, H12 = d3, H14 = d4, H16 = d5, soma = d_sum)
) |>
    autoplot(
        unit.out = "photon",
        idfactor = "Legend",
        w.band = photobiologyWavebands::VIS_bands("ISO"),
        annotations = c("+", "peak.labels", "valley.labels"),
        span = 15,
        text.size = 3.5
    ) +
    labs(title = "espectros hora-a-hora e diário")

# soma vertical dos espectros
autoplot(
    object = d_sum,
    unit.out = "photon",
    idfactor = "Legend",
    w.band = photobiologyWavebands::VIS_bands("ISO"),
    annotations = c("+", "peak.labels", "valley.labels"),
    span = 15,
    text.size = 3.5,
    label.qty = "contribution.pc"
) +
    labs(title = "soma vertical dos espectros")

# media vertical de espectros
source_mspct(list(H08 = d1, H10 = d2, H12 = d3, H14 = d4, H16 = d5)) |>
    autoplot(
        unit.out = "photon",
        idfactor = "Legend",
        w.band = VIS_bands("ISO"),
        annotations = c("+", "peak.labels", "valley.labels"),
        span = 15,
        text.size = 3.5,
        plot.data = "mean"
    ) +
    labs(title = "média vertical dos espectros")

# spectro total diário comparado com clorofila a
source_mspct(list(chl.a = chl_a, sum = d_sum_norm)) |>
    autoplot(
        idfactor = "Legend",
        w.band = VIS_bands("ISO"),
        annotations = c("+", "peak.labels", "valley.labels"),
        span = 15,
        text.size = 3.5
    ) +
    labs(title = "spectro total diário comparado com clorofila a")

# spectro total diário comparado com clorofila b
source_mspct(list(B_carot = B_carot, sum = d_sum_norm)) |>
    autoplot(
        idfactor = "Legend",
        w.band = photobiologyWavebands::VIS_bands("ISO"),
        annotations = c("+", "peak.labels", "valley.labels"),
        span = 15,
        text.size = 3.5
    ) +
    labs(title = "spectro total diário comparado com clorofila b")

# Métricas ----------------------------------------------------------------
# Porcentagem das bandas R, G, B, PhR no visível

d_sum_full <- sum(d_sum$s.e.irrad)
d1_full <- sum(d1$s.e.irrad)
d2_full <- sum(d2$s.e.irrad)
d3_full <- sum(d3$s.e.irrad)
d4_full <- sum(d4$s.e.irrad)
d5_full <- sum(d5$s.e.irrad)

PhR_d_sum <- d_sum |> trim_wl(range = PhR()) |> summarise(sum(s.e.irrad))
PhR_d1 <- d1 |> trim_wl(range = PhR()) |> summarise(sum(s.e.irrad))
PhR_d2 <- d2 |> trim_wl(range = PhR()) |> summarise(sum(s.e.irrad))
PhR_d3 <- d3 |> trim_wl(range = PhR()) |> summarise(sum(s.e.irrad))
PhR_d4 <- d4 |> trim_wl(range = PhR()) |> summarise(sum(s.e.irrad))
PhR_d5 <- d5 |> trim_wl(range = PhR()) |> summarise(sum(s.e.irrad))

B_d_sum <- d_sum |> trim_wl(range = Blue()) |> summarise(sum(s.e.irrad))
B_d1 <- d1 |> trim_wl(range = Blue()) |> summarise(sum(s.e.irrad))
B_d2 <- d2 |> trim_wl(range = Blue()) |> summarise(sum(s.e.irrad))
B_d3 <- d3 |> trim_wl(range = Blue()) |> summarise(sum(s.e.irrad))
B_d4 <- d4 |> trim_wl(range = Blue()) |> summarise(sum(s.e.irrad))
B_d5 <- d5 |> trim_wl(range = Blue()) |> summarise(sum(s.e.irrad))

G_d_sum <- d_sum |> trim_wl(range = Green()) |> summarise(sum(s.e.irrad))
G_d1 <- d1 |> trim_wl(range = Green()) |> summarise(sum(s.e.irrad))
G_d2 <- d2 |> trim_wl(range = Green()) |> summarise(sum(s.e.irrad))
G_d3 <- d3 |> trim_wl(range = Green()) |> summarise(sum(s.e.irrad))
G_d4 <- d4 |> trim_wl(range = Green()) |> summarise(sum(s.e.irrad))
G_d5 <- d5 |> trim_wl(range = Green()) |> summarise(sum(s.e.irrad))

R_d_sum <- d_sum |> trim_wl(range = Red()) |> summarise(sum(s.e.irrad))
R_d1 <- d1 |> trim_wl(range = Red()) |> summarise(sum(s.e.irrad))
R_d2 <- d2 |> trim_wl(range = Red()) |> summarise(sum(s.e.irrad))
R_d3 <- d3 |> trim_wl(range = Red()) |> summarise(sum(s.e.irrad))
R_d4 <- d4 |> trim_wl(range = Red()) |> summarise(sum(s.e.irrad))
R_d5 <- d5 |> trim_wl(range = Red()) |> summarise(sum(s.e.irrad))

sol <- tibble(
    Red = c(
        (R_d1$`sum(s.e.irrad)` / d1_full) * 100,
        (R_d2$`sum(s.e.irrad)` / d2_full) * 100,
        (R_d3$`sum(s.e.irrad)` / d3_full) * 100,
        (R_d4$`sum(s.e.irrad)` / d4_full) * 100,
        (R_d5$`sum(s.e.irrad)` / d5_full) * 100,
        (R_d_sum$`sum(s.e.irrad)` / d_sum_full) * 100
    ),
    Green = c(
        (G_d1$`sum(s.e.irrad)` / d1_full) * 100,
        (G_d2$`sum(s.e.irrad)` / d2_full) * 100,
        (G_d3$`sum(s.e.irrad)` / d3_full) * 100,
        (G_d4$`sum(s.e.irrad)` / d4_full) * 100,
        (G_d5$`sum(s.e.irrad)` / d5_full) * 100,
        (G_d_sum$`sum(s.e.irrad)` / d_sum_full) * 100
    ),
    Blue = c(
        (B_d1$`sum(s.e.irrad)` / d1_full) * 100,
        (B_d2$`sum(s.e.irrad)` / d2_full) * 100,
        (B_d3$`sum(s.e.irrad)` / d3_full) * 100,
        (B_d4$`sum(s.e.irrad)` / d4_full) * 100,
        (B_d5$`sum(s.e.irrad)` / d5_full) * 100,
        (B_d_sum$`sum(s.e.irrad)` / d_sum_full) * 100
    ),
    PhR = c(
        (PhR_d1$`sum(s.e.irrad)` / d1_full) * 100,
        (PhR_d2$`sum(s.e.irrad)` / d2_full) * 100,
        (PhR_d3$`sum(s.e.irrad)` / d3_full) * 100,
        (PhR_d4$`sum(s.e.irrad)` / d4_full) * 100,
        (PhR_d5$`sum(s.e.irrad)` / d5_full) * 100,
        (PhR_d_sum$`sum(s.e.irrad)` / d_sum_full) * 100
    )
) |>
    mutate(Hora = c("08:00", "10:00", "12:00", "14:00", "16:00", "soma")) |>
    select(Hora, Red, Green, Blue, PhR)
sol
