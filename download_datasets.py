import os
import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

os.makedirs("datasets/raw", exist_ok=True)
os.makedirs("datasets/processed", exist_ok=True)

urls = {
    "datasets/raw/crop_production.csv": [
        "https://raw.githubusercontent.com/ankitaS11/Crop-Yield-Prediction-in-India-using-ML/master/crop_production.csv",
        "https://raw.githubusercontent.com/ritveek19/EDA_CropProduction/master/crop_production.csv"
    ],
    "datasets/raw/rainfall.csv": [
        "https://raw.githubusercontent.com/rajiv8/Rainfall-Prediction/master/rainfall%20in%20india%201901-2015.csv",
        "https://raw.githubusercontent.com/MainakRepositor/Datasets/master/rainfall%20in%20india%201901-2015.csv"
    ]
}

for dest, candidates in urls.items():
    success = False
    for url in candidates:
        try:
            print(f"Downloading {dest} from {url}...")
            urllib.request.urlretrieve(url, dest)
            if os.path.exists(dest) and os.path.getsize(dest) > 1000:
                print(f"Successfully downloaded {dest} ({os.path.getsize(dest)} bytes)")
                success = True
                break
        except Exception as e:
            print(f"Failed to download from {url}: {e}")
    if not success:
        print(f"Warning: Could not download {dest} from remote sources.")

