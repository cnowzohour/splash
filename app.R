library(shiny)
library(readr)
library(dplyr)
library(plotly)

basePathMac <- "~/Downloads"
basePathPi <- "/home/pi"
basePath <- if (dir.exists(basePathPi)) basePathPi else basePathMac

readData <- function() {
  dat <- bind_rows(lapply(list.files(file.path(basePath, "splash_data"), "*.csv", full.names = T), read_csv))
  log <- unlist(lapply(list.files(file.path(basePath, "splash_data"), "*.log", full.names = T), function(path) {
    f <- file(path, "r")
    log <- readLines(f)
    close(f)
    log
  }))
  list(dat = dat, log = log)
}

ui <- fluidPage(
  tags$head(
    tags$style(
      type="text/css",
      "body.disconnected {
         background-color: inherit;
         opacity: 1;
       }"
    )
  ),
  plotlyOutput("plot")
)

server <- function(input, output) {
  output$plot <- renderPlotly({
    data <- readData()
    dat <- data$dat
    log <- data$log
    logLinesIrrigationControl <- Filter(function(line) grepl("Irrigation control", line), log)
    logLinesTimeThreshold <- Filter(function(line) grepl("IRRIGATION_CONTROL_MAX_RATE_H", line), log)
    logLinesMoistureThreshold <- Filter(function(line) grepl("MIN_MOISTURE_THRESHOLD", line), log)
    getDateTime <- function(line) as.POSIXct(paste(strsplit(line, " ")[[1]][1:2], collapse = " "), tz = "UTC")
    dtIrrigationControl <- lapply(logLinesIrrigationControl, getDateTime)
    dtTimeThreshold <- lapply(logLinesTimeThreshold, getDateTime)
    dtMoistureThreshold <- lapply(logLinesMoistureThreshold, getDateTime)
    y2 <- list(
      overlaying = "y",
      side = "right",
      title = "Temperature"
    )
    vline <- function(color) function(x) {
      list(
        type = "line", 
        y0 = 0, 
        y1 = 1, 
        yref = "paper",
        x0 = x, 
        x1 = x, 
        line = list(color = color)
      )
    }
    plot_ly(dat, type = "scatter", mode = "lines") %>%
      add_trace(x = ~datetime, y = ~moisture, name = "Moisture") %>%
      add_trace(x = ~datetime, y = ~temperature, name = "Temperature", yaxis = "y2") %>%
      layout(
        yaxis2 = y2,
        yaxis = list(title = "Moisture"),
        xaxis = list(title = "Time", range = c((as.numeric(Sys.time()) - 7 * 24 * 3600) * 1000L, as.numeric(Sys.time()) * 1000L)),
        shapes = c(lapply(dtIrrigationControl, vline("gray")), lapply(dtTimeThreshold, vline("blue")), lapply(dtMoistureThreshold, vline("red")))
      )
  })
}

shinyApp(ui, server, options = c(port = 8000))
