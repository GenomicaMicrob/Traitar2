# Installation Guide for Traitar2

This document provides detailed instructions for installing Traitar2 and its dependencies across different environments.

## Prerequisites

Traitar2 is a Python-based tool that relies on several external bioinformatic tools and R packages:

* **Python 3.10+** (Recommended)
* **HMMER** (for protein family annotation)
* **Prodigal** (for gene prediction)
* **GNU Parallel** (for multi-threaded execution)
* **R** with the following packages:
  * `ComplexHeatmap` (Bioconductor)
  * `dplyr`, `tidyr`, `GetoptLong`, `RColorBrewer`

---

## 1. Mamba/Conda Installation (Recommended)

This is the fastest and most reliable method, as it handles all Python, R, and binary dependencies automatically.

### Step 1: Clone the repository

```bash
git clone https://github.com/GenomicaMicrob/Traitar2
cd Traitar2
```

### Step 2: Create and activate the environment

If you don't have **Mamba** installed, we highly recommend it over standard Conda for faster dependency resolution. You can get it by:

* **Installing Miniforge (contains Mamba)**: Download it from the [Miniforge GitHub](https://github.com/conda-forge/miniforge).
* **Installing within Conda**:

    ```bash
    conda install -n base -c conda-forge mamba
    ```

If you prefer to stay with Conda, just replace `mamba` with `conda` in the following commands.

```bash
mamba env create -f environment.yml
# OR: conda env create -f environment.yml

conda activate traitar2
```

### Step 3: Install the package

Installs Traitar2 in "editable" mode so you can run the `traitar2` command from anywhere.

```bash
pip install -e .
```

---

## 2. Python Virtual Environment (venv)

If you have already installed the **Binary Dependencies** (HMMER, Prodigal, R) but prefer not to use Conda, you can use a standard Python virtual environment.

### Step 1: Create the environment

```bash
python3 -m venv traitar2_env
```

### Step 2: Activate the environment

* **On Linux/macOS**:

    ```bash
    source traitar2_env/bin/activate
    ```

* **On Windows**:

    ```bash
    traitar2_env\Scripts\activate
    ```

### Step 3: Install dependencies

```bash
pip install --upgrade pip
pip install -e .
```

---

## 3. Manual Installation (Global or custom)

If you prefer to manage your own environment or are working on a system where Conda is not available, follow these steps.

### Step 1: Install Binary Dependencies

Traitar2 requires several external bioinformatic tools. **Note: These are binary tools, they cannot be installed via `pip`.**

#### On Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install hmmer prodigal parallel
```

#### On macOS (using Homebrew)

```bash
brew install hmmer prodigal parallel
```

#### Manual Download

If you don't have a package manager, you can download the binaries directly:

* **HMMER**: [http://hmmer.org/download.html](http://hmmer.org/download.html)
* **Prodigal**: [https://github.com/hyattpd/Prodigal](https://github.com/hyattpd/Prodigal)
* **GNU Parallel**: [https://www.gnu.org/software/parallel/](https://www.gnu.org/software/parallel/)

### Step 2: Install Python Dependencies

```bash
pip install pandas numpy scipy matplotlib
```

### Step 3: Setup R Environment

Traitar2 uses R for generating professional heatmaps. Open R and run:

```R
# Install CRAN packages
install.packages(c("dplyr", "tidyr", "GetoptLong", "RColorBrewer"))

# Install Bioconductor packages
if (!require("BiocManager", quietly = TRUE))
    install.packages("BiocManager")
BiocManager::install("ComplexHeatmap")
```

---

## 4. Verification

After installation, you can verify that all components are correctly configured by running:

```bash
# Check Traitar2
traitar2 --version

# Check dependencies
which hmmsearch
which prodigal
which parallel
Rscript -e "library(ComplexHeatmap); print('R is ready!')"
```

---

## 5. Download Pfam HMMs database

Traitar2 requires the Pfam database v27 to function. Run the following command to download and set it up automatically. You need to run this command only once.

```bash
traitar2 pfam pfam_db
```

This will download approximately 230 MB of data and configure the project root for its access to the database.

[!TIP]
If you already have the Pfam database (`Pfam-A.hmm`) on your system, you can skip the download by pointing Traitar to its directory:

```bash
traitar2 pfam --local /path/to/your/pfam_folder/
```

The Pfam database can also be manually downloaded from: [ftp://ftp.ebi.ac.uk/pub/databases/Pfam/releases/Pfam27.0/Pfam-A.hmm.gz](ftp://ftp.ebi.ac.uk/pub/databases/Pfam/releases/Pfam27.0/Pfam-A.hmm.gz)

If you want to install the database in one location and then move the Pfam folder to a new one, you have to run the above command (`--local`) again in order for traitar2 to fix the path to the database.

---
## 6. Testing

You can test the installation with the example genomes provided.

Three genomes of *Streptococcus agalactiae* are in the `example/` directory. You can run traitar2 as follows:

```bash
traitar2 phenotype -d example/ -o agalactiae_results
```

You will get a heatmap (`.png`), and a publication-ready summary table (`Phenotypic_table.md`) highlighting differences between the genomes analyzed.

---

## 7. Troubleshooting

### "GNU parallel is not available"

If you see this error despite having it installed, make sure it's in your `$PATH` or run `parallel --citation` once to silence the citation notice, which sometimes interferes with automated scripts.

### R Heatmap Errors

If heatmaps are not being generated, the most common cause is a missing R dependency. Try running the heatmap script manually to see the specific error:

```bash
Rscript src/heatmap.R --help
```

### Pfam Database Path

If Traitar2 complains it cannot find the Pfam database:

1. Run `traitar2 pfam pfam_db` to download it.
2. If you have it locally, run `traitar2 pfam --local /path/to/folder/` to update the `config.json` helper.
