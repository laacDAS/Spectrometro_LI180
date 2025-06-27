# Call personalized R functions ------------------------------------------
source("functions.R")

# Create RDS file --------------------------------------------------------
process_reference_spectrum(
  excel_file = here::here("dados", "spectros_referencia.xlsx"),
  rds_file = here::here("dados", "reference_spectra.RDS")
)

# Define the file paths --------------------------------------------------
Rooms <- c(
  here("dados", "Spectros", "RoomA", "ESPD_RoomA_data_all.txt"),
  here("dados", "Spectros", "RoomB", "ESPD_Spectro_RoomB_all.txt")
)

# plot spectruns ---------------------------------------------------------
Chlorophyll_a <- plot_spectrometer_laac(
  arquivos = Rooms,
  reference_spectrum = "Chlorophyll_a",
  plot_rooms = c("Room_A", "Room_B"),
  plot_title = "Light spectrum - Comparing to Chlorophyll a",
  span = 15,
  text.size = 3.5,
  rds_file = "dados/reference_spectra.RDS"
)

Chlorophyll_b <- plot_spectrometer_laac(
  arquivos = Rooms,
  reference_spectrum = "Chlorophyll_b",
  plot_rooms = c("Room_A", "Room_B"),
  plot_title = "Light spectrum - Comparing to Chlorophyll b",
  span = 15,
  text.size = 3.5,
  rds_file = "dados/reference_spectra.RDS"
)

β_carotene <- plot_spectrometer_laac(
  arquivos = Rooms,
  reference_spectrum = "β_carotene",
  plot_rooms = c("Room_A", "Room_B"),
  plot_title = "Light spectrum - Comparing to β_carotene",
  span = 15,
  text.size = 3.5,
  rds_file = "dados/reference_spectra.RDS"
)

Zeaxanthin <-
  plot_spectrometer_laac(
    arquivos = Rooms,
    reference_spectrum = "Zeaxanthin",
    plot_rooms = c("Room_A", "Room_B"),
    plot_title = "Light spectrum - Comparing to Zeaxanthin",
    span = 15,
    text.size = 3.5,
    rds_file = "dados/reference_spectra.RDS"
  )

arranjo <- gridExtra::grid.arrange(Chlorophyll_a, Chlorophyll_b)
arranjo

# Save images ------------------------------------------------------------
ggsave(
  plot = arranjo,
  filename = here("outputs", "arranjo.png"),
  width = 14,
  height = 10,
  dpi = 300
)

ggsave(
  plot = Chlorophyll_a,
  filename = here("outputs", "Chlorophyll_a.png"),
  width = 14,
  height = 10,
  dpi = 300
)

ggsave(
  plot = Chlorophyll_b,
  filename = here("outputs", "Chlorophyll_b.png"),
  width = 14,
  height = 10,
  dpi = 300
)

ggsave(
  plot = Zeaxanthin,
  filename = here("outputs", "Zeaxanthin.png"),
  width = 14,
  height = 10,
  dpi = 300
)

ggsave(
  plot = β_carotene,
  filename = here("outputs", "Beta_carotene.png"),
  width = 14,
  height = 10,
  dpi = 300
)
