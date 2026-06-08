import urllib.request
import urllib.error
import json
import sys
import os
import gzip 
import src
import threading
import time
import itertools
import shutil

def download(args):
    """download or setup Pfam HMMs and write destination into config file"""
    
    if not os.path.exists(args.Pfam_db):
        os.makedirs(args.Pfam_db, exist_ok=True)

    hmm_file = os.path.join(args.Pfam_db, "Pfam-A.hmm")
    gz_file = os.path.join(args.Pfam_db, "Pfam-A.hmm.gz")

    # Step 1: Download if not local and hmm doesn't exist
    if not args.local and not os.path.exists(hmm_file) and not os.path.exists(gz_file):
        attempts = 0
        while attempts < 3:
            try:
                print(f"Attempt {attempts + 1}/3: Downloading Pfam HMMs...")
                sys.stdout.flush()
                
                url = "ftp://ftp.ebi.ac.uk/pub/databases/Pfam/releases/Pfam27.0/Pfam-A.hmm.gz"
                response = urllib.request.urlopen(url, timeout=5)
                content_length = int(response.headers.get('Content-Length', 0))
                total_size_mb = content_length / (1024 * 1024)
                
                with open(gz_file, 'wb') as f:
                    CHUNK = 1000000
                    downloaded = 0
                    while True:
                        chunk = response.read(CHUNK)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if content_length > 0:
                            progress = (downloaded / content_length) * 100
                            downloaded_mb = downloaded / (1024 * 1024)
                            print(f"\rDownloading: {downloaded_mb:.1f} MB / {total_size_mb:.1f} MB ({progress:.1f}%)", end="")
                            sys.stdout.flush()
                    
                    print("\nDownload completed successfully.")
                    sys.stdout.flush()
                break
            except (urllib.error.URLError, TimeoutError) as e:
                attempts += 1
                print(f"\nError: {e}")
                if attempts >= 3:
                    sys.exit("Maximum retry attempts reached. Download failed.")
                print(f"Retrying... ({attempts}/3)")
                sys.stdout.flush()

    # Step 2: Extract if only gz exists
    if os.path.exists(gz_file) and not os.path.exists(hmm_file):
        print(f"Extracting {gz_file}...")
        sys.stdout.flush()
        
        stop_spinner = threading.Event()
        def spin():
            spinner = itertools.cycle(['-', '/', '|', '\\'])
            while not stop_spinner.is_set():
                sys.stdout.write(f"\rExtracting: {next(spinner)}")
                sys.stdout.flush()
                time.sleep(0.1)
        
        spinner_thread = threading.Thread(target=spin)
        spinner_thread.daemon = True
        spinner_thread.start()
        
        try:
            with gzip.open(gz_file, 'rb') as zf:
                with open(hmm_file, 'wb') as out_f:
                    shutil.copyfileobj(zf, out_f)
            stop_spinner.set()
            spinner_thread.join()
            sys.stdout.write("\r" + " " * 30 + "\r")
            print("Extraction completed successfully.")
        except Exception as e:
            stop_spinner.set()
            spinner_thread.join()
            sys.exit(f"\nError extracting file: {e}")
        finally:
            sys.stdout.flush()
            
        if not args.local:
            try:
                os.remove(gz_file)
                print(f"Removed temporary download file {gz_file}")
            except: pass

    # Step 3: Run hmmpress if indices are missing
    if os.path.exists(hmm_file):
        indices = [hmm_file + ext for ext in ['.h3f', '.h3i', '.h3m', '.h3p']]
        if not all(os.path.exists(idx) for idx in indices):
            print(f"Creating HMMER database indices with hmmpress...")
            sys.stdout.flush()
            
            stop_spinner = threading.Event()
            def spin_press():
                spinner = itertools.cycle(['-', '/', '|', '\\'])
                while not stop_spinner.is_set():
                    sys.stdout.write(f"\rIndexing: {next(spinner)}")
                    sys.stdout.flush()
                    time.sleep(0.1)
            
            spinner_thread = threading.Thread(target=spin_press)
            spinner_thread.daemon = True
            spinner_thread.start()
            
            try:
                import subprocess
                result = subprocess.run(["hmmpress", "-f", hmm_file], capture_output=True, text=True)
                stop_spinner.set()
                spinner_thread.join()
                sys.stdout.write("\r" + " " * 30 + "\r")
                
                if result.returncode != 0:
                    sys.exit(f"\nError running hmmpress: {result.stderr}")
                print("HMMER database created successfully.")
            except FileNotFoundError:
                stop_spinner.set()
                spinner_thread.join()
                sys.exit("\nError: 'hmmpress' not found. Please install HMMER.")
            finally:
                sys.stdout.flush()

    # Step 4: Verify and create config.json
    # Locate the data directory where config.json should reside
    src_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(os.path.join(src_dir, 'data')):
        data_dir = os.path.join(src_dir, 'data')
    else:
        # Root of the repository/development fallback
        data_dir = os.path.abspath(os.path.join(src_dir, '..'))
    
    config_path = os.path.join(data_dir, "config.json")
    
    if not os.path.exists(hmm_file):
        sys.exit(f"Error: Pfam-A.hmm not found in {args.Pfam_db}. Make sure the file exists or provide a valid path.")

    with open(config_path, 'w') as config:
        config.write(json.dumps({"hmms": os.path.abspath(args.Pfam_db)}))
    
    print(f"Configuration completed. Using Pfam database at: {os.path.abspath(args.Pfam_db)}")

