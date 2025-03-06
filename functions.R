# --- 2. Modified process_files_spectrometer Function (with Plotting) ---

library(readxl)
library(janitor)
library(dplyr)
library(photobiology)
library(here)
library(ggspectra)

plot_spectrometer_laac <- function(
  arquivos,
  reference_spectrum = c(
    "Chlorophyll_a",
    "Chlorophyll_b",
    "Zeaxanthin",
    "β_carotene",
    "Anthocyanin",
    "Pr",
    "Pfr",
    "Cryptochrome",
    "LOV",
    "Phycoerythrin",
    "Allophycocyanin"
  ),
  plot_rooms = c("Room_A", "Room_B"),
  plot_title = "Light spectrum - Comparing to XXXX",
  span = 15,
  text.size = 3.5,
  rds_file = here::here("dados", "reference_spectra.RDS")
) {
  #' Process Spectrometer LI-180 .txt files, convert to source_spct, and plot with a selected reference spectrum.
  #'
  #' This function reads and processes .txt files from a Spectrometer LI-180,
  #' extracts the wavelength and PPFD data, converts the data to photobiology::source_spct
  #' objects, and generates a plot comparing the spectra to a selected reference spectrum.
  #'
  #' @param arquivos A vector of file paths to the .txt files for Room A and Room B.
  #'                  Assumes the first file is Room A and the second is Room B.
  #' @param reference_spectrum A string specifying the name of the reference spectrum to use
  #'        (e.g., "Chlorophyll_a", "Beta_Carotene").  The valid options are:
  #'        "Chlorophyll_a", "Chlorophyll_b", "Zeaxanthin", "β_carotene", "Anthocyanin",
  #'        "Pr", "Pfr", "Cryptochrome", "LOV", "Phycoerythrin", "Allophycocyanin".
  #'        If NULL, no reference spectrum is used.
  #' @param plot_rooms A character vector specifying which rooms to plot.  Can be "Room_A", "Room_B", or both.
  #' @param plot_title A string specifying the title of the plot. If NULL, a default title is used.
  #' @param span The 'span' parameter for the smoothing function in autoplot (default: 15).
  #' @param text.size The text size for annotations in the plot (default: 3.5).
  #' @param rds_file Path to the .RDS file containing the reference spectra (default: "dados/reference_spectra.RDS").
  #' @return A ggplot object (the plot).  Returns NULL if there are errors.

  # --- Initialize ---
  roomA <- NULL
  roomB <- NULL
  plot_list <- base::list()

  # --- Load Reference Spectrum ---
  tryCatch(
    {
      all_reference_spectra <- base::readRDS(rds_file)
      selected_reference_spectrum <- NULL # Initialize to NULL

      # Check if the requested reference spectrum exists
      if (!is.null(reference_spectrum)) {
        if (reference_spectrum %in% names(all_reference_spectra)) {
          selected_reference_spectrum <- all_reference_spectra[[
            reference_spectrum
          ]]
        } else {
          warning(
            base::paste(
              "Reference spectrum '",
              reference_spectrum,
              "' not found in RDS file."
            )
          )
        }
      }
    },
    error = function(e) {
      warning(base::paste("Erro ao ler o arquivo RDS:", e$message))
      return(NULL) # Return NULL if RDS file can't be read
    }
  )

  # --- Process Spectrometer Files ---
  if (length(arquivos) != 2) {
    warning("Expected two files (Room A and Room B).")
    return(NULL) # Return NULL if the number of files is incorrect.
  }

  # Process Room A
  tryCatch(
    {
      roomA_data <- process_files_spectrometer_internal(arquivos[1]) # Using the internal function
      roomA <- roomA_data |>
        dplyr::rename(s.e.irrad = PPFD, w.length = Wavelength) |>
        dplyr::mutate(s.e.irrad = s.e.irrad / 10) |>
        photobiology::as.source_spct()
      if ("Room_A" %in% plot_rooms) plot_list[["Room_A"]] <- roomA
    },
    error = function(e) {
      warning(base::paste("Erro ao processar o arquivo Room A:", e$message))
      roomA <- NULL # Set to NULL in case of error
    }
  )

  # Process Room B
  tryCatch(
    {
      roomB_data <- process_files_spectrometer_internal(arquivos[2]) # Using the internal function
      roomB <- roomB_data |>
        dplyr::rename(s.e.irrad = PPFD, w.length = Wavelength) |>
        dplyr::mutate(s.e.irrad = s.e.irrad / 10) |>
        photobiology::as.source_spct()
      if ("Room_B" %in% plot_rooms) plot_list[["Room_B"]] <- roomB
    },
    error = function(e) {
      warning(base::paste("Erro ao processar o arquivo Room B:", e$message))
      roomB <- NULL # Set to NULL in case of error
    }
  )

  # --- Create Plot ---
  if ((is.null(roomA) && is.null(roomB)) || length(plot_list) == 0) {
    warning("No valid Room A or Room B data to plot.")
    return(NULL) # Return NULL if there's nothing to plot
  }

  # Add the reference spectrum to the list *only* if it was loaded successfully
  if (!is.null(selected_reference_spectrum)) {
    plot_list[[reference_spectrum]] <- selected_reference_spectrum
  }

  # Construct the title
  if (is.null(plot_title)) {
    if (!is.null(reference_spectrum)) {
      plot_title <- base::paste(
        "Light spectrum - Comparing to",
        reference_spectrum
      )
    } else {
      plot_title <- "Light spectrum"
    }
  }

  # Generate the plot
  tryCatch(
    {
      p <- photobiology::source_mspct(plot_list) |>
        autoplot(
          idfactor = "Legend",
          w.band = photobiologyWavebands::VIS_bands("ISO"),
          unit.out = "photon",
          annotations = c("+", "peak.labels", "valley.labels"),
          span = span,
          text.size = text.size
        ) +
        labs(title = plot_title)
      return(p) # Return the plot
    },
    error = function(e) {
      warning(base::paste("Erro ao gerar o gráfico:", e$message))
      return(NULL) # Return NULL if there's an error during plotting
    }
  )
}

# --- Internal Helper Function (to avoid code duplication) ---
process_files_spectrometer_internal <- function(arquivo) {
  #' Internal function to process a single spectrometer file.
  data <- tryCatch(
    {
      utils::read.table(
        arquivo,
        sep = "\t",
        header = FALSE,
        stringsAsFactors = FALSE,
        encoding = "UTF-8"
      )
    },
    error = function(e) {
      warning(base::paste("Erro ao ler o arquivo:", arquivo, "-", e$message))
      return(NULL)
    }
  )

  if (is.null(data)) return(NULL)

  linha_inicial <- base::grep("\\(umol/\\(m\\^2\\*s\\)\\)", data[, 1])
  if (length(linha_inicial) == 0) {
    warning(
      base::paste(
        "Linha inicial contendo '(umol/(m^2*s))' não encontrada no arquivo:",
        arquivo
      )
    )
    return(NULL)
  }
  linha_inicial <- linha_inicial[1]

  linha_cctk <- base::grep("CCT\\(K\\)", data[, 1])
  if (length(linha_cctk) > 0) {
    linha_anterior <- linha_cctk[1] - 1
    if (linha_anterior > 0) {
      limite_superior <- linha_anterior
    } else {
      limite_superior <- nrow(data)
    }
  } else {
    limite_superior <- nrow(data)
  }

  data <- data[linha_inicial:limite_superior, ]

  colnames(data) <- c("Wavelength", "PPFD")
  data$Wavelength <- base::gsub("\\(umol.*", "", data$Wavelength)
  data$Wavelength <- as.numeric(base::gsub("[^0-9]", "", data$Wavelength))
  data$PPFD <- as.numeric(base::gsub(",", ".", data$PPFD, fixed = TRUE))

  # Check for NA values after conversion to numeric
  if (any(is.na(data$Wavelength)) || any(is.na(data$PPFD))) {
    warning(
      base::paste(
        "NA values introduced in file:",
        arquivo,
        ". Check data cleaning steps."
      )
    )
  }
  return(data)
}

process_reference_spectrum <- function(
  excel_file,
  rds_file = here::here("dados", "reference_spectra.RDS")
) {
  #' Process reference spectra from an Excel file and save them to an RDS file.
  #'
  #' This function reads reference spectra from a specified Excel file,
  #' processes them, and saves them as a list of `source_spct` objects to an RDS file.
  #'
  #' @param excel_file Path to the Excel file containing the reference spectra.
  #' @param rds_file Path to the RDS file where the processed spectra will be saved
  #'        (default: here::here("dados", "reference_spectra.RDS")).
  #'
  #' @return None (invisibly returns NULL).  Saves the reference spectra to the RDS file.
  #'
  #' @details The Excel file is expected to have a sheet named "pigmentos" with
  #'          specific ranges defined for each reference spectrum.  The function
  #'          will create the "dados" directory if it does not exist.

  # Check if the Excel file exists
  if (!file.exists(excel_file)) {
    stop(paste("Erro: O arquivo Excel não foi encontrado em:", excel_file))
  }

  # Create the 'dados' directory if it doesn't exist
  dados_dir <- here::here("dados")
  if (!dir.exists(dados_dir)) {
    dir.create(dados_dir)
    base::cat("Diretório 'dados' criado em:", dados_dir, "\n")
  }

  # Define the path to the Excel file
  spectros_referencia_file <- excel_file

  # Load all reference spectra
  tryCatch(
    {
      chl_a <- readxl::read_excel(
        spectros_referencia_file,
        sheet = "pigmentos",
        range = "A2:B90"
      ) |>
        janitor::clean_names() |>
        dplyr::rename(
          s.e.irrad = relative_absorbance,
          w.length = wavelength_nm
        ) |>
        photobiology::as.source_spct()
      chl_b <- readxl::read_excel(
        spectros_referencia_file,
        sheet = "pigmentos",
        range = "C2:D90"
      ) |>
        janitor::clean_names() |>
        dplyr::rename(
          s.e.irrad = relative_absorbance,
          w.length = wavelength_nm
        ) |>
        photobiology::as.source_spct()
      zeaxanthin <- readxl::read_excel(
        spectros_referencia_file,
        sheet = "pigmentos",
        range = "F2:G58"
      ) |>
        janitor::clean_names() |>
        dplyr::rename(
          s.e.irrad = relative_absorbance,
          w.length = wavelength_nm
        ) |>
        photobiology::as.source_spct()
      Beta_Carotene <- readxl::read_excel(
        spectros_referencia_file,
        sheet = "pigmentos",
        range = "E2:F58"
      ) |>
        janitor::clean_names() |>
        dplyr::rename(
          s.e.irrad = relative_absorbance,
          w.length = wavelength_nm
        ) |>
        photobiology::as.source_spct()
      Anthocyanin <- readxl::read_excel(
        spectros_referencia_file,
        sheet = "pigmentos",
        range = "H2:I45"
      ) |>
        janitor::clean_names() |>
        dplyr::rename(
          s.e.irrad = relative_absorbance,
          w.length = wavelength_nm
        ) |>
        photobiology::as.source_spct()
      Pr <- readxl::read_excel(
        spectros_referencia_file,
        sheet = "pigmentos",
        range = "J2:K65"
      ) |>
        janitor::clean_names() |>
        dplyr::rename(
          s.e.irrad = relative_absorbance,
          w.length = wavelength_nm
        ) |>
        photobiology::as.source_spct()
      Pfr <- readxl::read_excel(
        spectros_referencia_file,
        sheet = "pigmentos",
        range = "L2:M65"
      ) |>
        janitor::clean_names() |>
        dplyr::rename(
          s.e.irrad = relative_absorbance,
          w.length = wavelength_nm
        ) |>
        photobiology::as.source_spct()
      Cryptochrome <- readxl::read_excel(
        spectros_referencia_file,
        sheet = "pigmentos",
        range = "N2:O61"
      ) |>
        janitor::clean_names() |>
        dplyr::rename(
          s.e.irrad = relative_absorbance,
          w.length = wavelength_nm
        ) |>
        photobiology::as.source_spct()
      LOV <- readxl::read_excel(
        spectros_referencia_file,
        sheet = "pigmentos",
        range = "P2:Q55"
      ) |>
        janitor::clean_names() |>
        dplyr::rename(
          s.e.irrad = relative_absorbance,
          w.length = wavelength_nm
        ) |>
        photobiology::as.source_spct()
      Phycoerythrin <- readxl::read_excel(
        spectros_referencia_file,
        sheet = "pigmentos",
        range = "R2:S67"
      ) |>
        janitor::clean_names() |>
        dplyr::rename(
          s.e.irrad = relative_absorbance,
          w.length = wavelength_nm
        ) |>
        photobiology::as.source_spct()
      Allophycocyanin <- readxl::read_excel(
        spectros_referencia_file,
        sheet = "pigmentos",
        range = "V2:W52"
      ) |>
        janitor::clean_names() |>
        dplyr::rename(
          s.e.irrad = relative_absorbance,
          w.length = wavelength_nm
        ) |>
        photobiology::as.source_spct()

      # Create a list of the reference spectra
      reference_spectra <- base::list(
        Chlorophyll_a = chl_a,
        Chlorophyll_b = chl_b,
        Zeaxanthin = zeaxanthin,
        `β_carotene` = Beta_Carotene,
        Anthocyanin = Anthocyanin,
        Pr = Pr,
        Pfr = Pfr,
        Cryptochrome = Cryptochrome,
        LOV = LOV,
        Phycoerythrin = Phycoerythrin,
        Allophycocyanin = Allophycocyanin
      )

      # Save the list to an RDS file
      base::saveRDS(reference_spectra, file = rds_file)

      base::cat("\nReference spectra saved to:", rds_file, "\n")
    },
    error = function(e) {
      stop(base::paste("Erro ao processar espectros:", e$message))
    }
  )

  invisible(NULL) # Return NULL invisibly
}
