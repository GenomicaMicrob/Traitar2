#!/usr/bin/env Rscript

# Suppress all warnings and messages
options(warn = -1)
suppressMessages({
  suppressPackageStartupMessages(library(ComplexHeatmap))
  suppressPackageStartupMessages(library(RColorBrewer))
  suppressPackageStartupMessages(library(dplyr))
  suppressPackageStartupMessages(library(tidyr))
  suppressPackageStartupMessages(library(GetoptLong))
})

# --- Argument Parsing ---
data_f <- NULL
out_f <- NULL
sample_f <- NULL
color_f <- NULL
pt_metadata_f <- NULL
cluster_rows <- TRUE
cluster_cols <- TRUE
orientation <- "horizontal"

GetoptLong(
  "data_f=s", "Path to prediction matrix",
  "out_f=s", "Path to output file (PDF/PNG)",
  "sample_f=s", "Path to sample metadata (optional)",
  "color_f=s", "Path to color definition file",
  "pt_metadata_f=s", "Path to phenotype metadata file",
  "orientation=s", "Heatmap orientation: horizontal or vertical",
  "cluster_rows!", "Cluster rows (samples)",
  "cluster_cols!", "Cluster columns (phenotypes)"
)

# --- Simplified Execution Mode ---
# If called with a directory as a remaining argument, infer all paths
results_dir <- NULL
extra_args <- commandArgs(trailingOnly = TRUE)
# GetoptLong might have consumed these, but we check if we still have a path
# Actually GetoptLong is quite strict. Let's add a fallback if basic files are missing.

if (is.null(data_f) && length(extra_args) > 0) {
  results_dir <- extra_args[length(extra_args)]
}

if (!is.null(results_dir) && dir.exists(results_dir)) {
  if (is.null(data_f)) {
    # Try combined first, then phypat
    mats <- c(
      file.path(results_dir, "phenotype_prediction", "predictions_majority-vote_combined.txt"),
      file.path(results_dir, "phenotype_prediction", "predictions_majority-vote.txt")
    )
    data_f <- mats[file.exists(mats)][1]
  }
  if (is.null(pt_metadata_f)) {
    meta <- file.path(results_dir, "phenotype_metadata.csv")
    if (file.exists(meta)) pt_metadata_f <- meta
  }
  if (is.null(out_f)) {
    out_f <- file.path(results_dir, "phenotype_prediction", "heatmap_final.pdf")
  }
}

# Find colors.txt relative to the script if not provided
if (is.null(color_f)) {
  # Get script path
  initial.options <- commandArgs(trailingOnly = FALSE)
  file.arg.name <- "--file="
  script.name <- sub(file.arg.name, "", initial.options[grep(file.arg.name, initial.options)])
  if (length(script.name) > 0) {
    # Script is in src/, data is in src/data/
    color_f <- file.path(dirname(script.name), "data", "colors.txt")
  }
}

# --- Validation ---
if (is.null(data_f) || !file.exists(data_f)) {
  stop("Missing input matrix. Use --data_f or provide the results directory path.")
}
if (!(orientation %in% c("horizontal", "vertical"))) {
  stop("Invalid orientation. Use 'horizontal' or 'vertical'.")
}

# --- 1. Load Data ---
mat <- read.table(data_f, header = TRUE, sep = "\t", row.names = 1, check.names = FALSE)
mat <- as.matrix(mat)

# --- 2. Colors ---
colors_map <- c(
  "0" = "#F7F7F7", # Light Gray
  "1" = "#A6CEE3", # PhyPat
  "2" = "#B2DF8A", # PGL
  "3" = "#1F78B4" # Both
)

# --- 3. Sample Annotations ---
sample_anno <- NULL
sample_cats <- NULL
sample_anno_col <- NULL
if (!is.null(sample_f) && file.exists(sample_f)) {
  samples_df <- read.table(sample_f, header = TRUE, sep = "\t", check.names = FALSE)
  if ("category" %in% colnames(samples_df)) {
    sample_cats <- samples_df$category[match(rownames(mat), samples_df$sample_name)]
    unique_cats <- unique(na.omit(sample_cats))
    if (!is.null(color_f) && file.exists(color_f)) {
      pal_df <- read.table(color_f, header = TRUE, sep = "\t")
      pal <- rgb(pal_df$r, pal_df$g, pal_df$b, maxColorValue = 255)
      sample_anno_col <- setNames(pal[seq_along(unique_cats)], unique_cats)
    }
  }
}

# --- 4. Phenotype Annotations ---
pt_anno <- NULL
pt_cats <- NULL
pt_anno_col <- NULL
if (!is.null(pt_metadata_f) && file.exists(pt_metadata_f)) {
  pt_df <- read.csv(pt_metadata_f, check.names = FALSE)
  if ("category" %in% colnames(pt_df)) {
    pt_cats <- pt_df$category[match(colnames(mat), pt_df$accession)]
    unique_pt_cats <- unique(na.omit(pt_cats))
    if (!is.null(color_f) && file.exists(color_f)) {
      pal_df <- read.table(color_f, header = TRUE, sep = "\t")
      pal <- rev(rgb(pal_df$r, pal_df$g, pal_df$b, maxColorValue = 255))
      pt_anno_col <- setNames(pal[seq_along(unique_pt_cats)], unique_pt_cats)
    }
  }
}

# --- 5. Layout ---
row_split_val <- sample_cats
col_split_val <- pt_cats
heatmap_cluster_rows <- cluster_rows
heatmap_cluster_cols <- cluster_cols

if (orientation == "vertical") {
  mat <- t(mat)
  row_split_val <- pt_cats
  col_split_val <- sample_cats
  heatmap_cluster_rows <- cluster_cols
  heatmap_cluster_cols <- cluster_rows

  if (!is.null(pt_cats) && !is.null(pt_anno_col)) {
    pt_anno <- rowAnnotation(
      Phenotype_Group = pt_cats, col = list(Phenotype_Group = pt_anno_col),
      show_annotation_name = FALSE,
      annotation_legend_param = list(title = "Trait Category")
    )
  }
  if (!is.null(sample_cats) && !is.null(sample_anno_col)) {
    sample_anno <- columnAnnotation(
      Category = sample_cats, col = list(Category = sample_anno_col),
      show_annotation_name = FALSE,
      annotation_legend_param = list(title = "Sample Group")
    )
  }
} else {
  if (!is.null(sample_cats) && !is.null(sample_anno_col)) {
    sample_anno <- rowAnnotation(
      Category = sample_cats, col = list(Category = sample_anno_col),
      show_annotation_name = FALSE,
      annotation_legend_param = list(title = "Sample Group")
    )
  }
  if (!is.null(pt_cats) && !is.null(pt_anno_col)) {
    pt_anno <- columnAnnotation(
      Phenotype_Group = pt_cats, col = list(Phenotype_Group = pt_anno_col),
      show_annotation_name = FALSE,
      annotation_legend_param = list(title = "Trait Category")
    )
  }
}

# --- 6. Dimensions ---
cell_size <- 5 # mm
ht_width <- ncol(mat) * unit(cell_size, "mm")
ht_height <- nrow(mat) * unit(cell_size, "mm")
pdf_width <- (ncol(mat) * cell_size * 0.03937) + 10
pdf_height <- (nrow(mat) * cell_size * 0.03937) + 8

# --- 7. Plot ---
message("Generating: ", out_f)
ext <- tools::file_ext(out_f)
if (ext == "pdf") pdf(out_f, width = pdf_width, height = pdf_height) else png(out_f, width = (pdf_width * 150), height = (pdf_height * 150), res = 150)

ht <- Heatmap(
  mat,
  name = "Prediction", col = colors_map,
  width = ht_width, height = ht_height,
  cluster_rows = heatmap_cluster_rows, cluster_columns = heatmap_cluster_cols,
  left_annotation = if (orientation == "vertical") pt_anno else sample_anno,
  top_annotation = if (orientation == "vertical") sample_anno else pt_anno,
  rect_gp = gpar(col = "white", lwd = 0.5),
  row_names_side = "right", show_row_names = TRUE, show_column_names = TRUE,
  row_names_gp = gpar(fontsize = 8), column_names_gp = gpar(fontsize = 8),
  row_split = row_split_val, row_title_side = "right", row_title_rot = 0,
  row_title_gp = gpar(fontsize = 9, fontface = "bold"),
  column_split = col_split_val, column_title_side = "top", column_title_rot = 45,
  column_title_gp = gpar(fontsize = 9, fontface = "bold"),
  heatmap_legend_param = list(title = "Prediction", at = c(0, 1, 2, 3), labels = c("Negative", "PhyPat", "PGL", "Both"))
)

draw(ht, merge_legend = TRUE, heatmap_legend_side = "right", annotation_legend_side = "right", padding = unit(c(20, 20, 20, 20), "mm"))
invisible(dev.off())
