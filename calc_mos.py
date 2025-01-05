import os
import glob
import csv
import argparse
import math
import numpy as np

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Collect MOS CSV files, classify by model & f0-factor (natural->f1.00), then compute average + 95% CI."
    )
    parser.add_argument(
        "--input_dir", "-i",
        type=str,
        default="results",
        help="Directory containing CSV files."
    )
    parser.add_argument(
        "--output_file", "-o",
        type=str,
        default="results.csv",
        help="Output CSV file to save results."
    )
    return parser.parse_args()

def compute_mean_and_ci(values, confidence=0.95):
    """
    values: list of numeric scores.
    Returns mean, lower, upper for 95% CI (Z=1.96 assumption).
    """
    arr = np.array(values, dtype=float)
    n = len(arr)
    if n < 2:
        # Not enough data to compute CI
        mean = arr.mean() if n == 1 else float('nan')
        return mean, float('nan'), float('nan')
    
    mean = np.mean(arr)
    std = np.std(arr, ddof=1)  # sample standard deviation
    z = 1.96  # 95% CI for large sample
    se = std / np.sqrt(n)
    margin = z * se
    lower = mean - margin
    upper = mean + margin
    return mean, lower, upper

def classify_file(filepath):
    """
    filepath の例:
      "wav/set1/SiFiGAN/BC_seg13_f2.00.wav"
    ここからモデルと f0factor を判定し,
    natural → f1.00
    """
    import os
    filename = os.path.basename(filepath)
    dirs = filepath.split("/")

    # 例: dirs[2] == "SiFiGAN" or "VAE_SiFiGAN_v1" or "natural"
    if len(dirs) < 3:
        # 想定外: unknown model
        return ("unknown_model", "f1.00")
    
    model = dirs[2]  # e.g. "SiFiGAN" / "VAE_SiFiGAN_v1" / "natural"

    # natural → f1.00扱い
    if model == "natural":
        return ("natural", "f1.00")
    
    # filenameに "f0.50","f1.00","f2.00" が含まれているか判定
    if "f0.50" in filename:
        pitch = "f0.50"
    elif "f1.00" in filename:
        pitch = "f1.00"
    elif "f2.00" in filename:
        pitch = "f2.00"
    else:
        # デフォルト f1.00扱い
        pitch = "f1.00"
    
    return (model, pitch)

def main():
    args = parse_arguments()
    input_dir = args.input_dir
    output_file = args.output_file

    # data_dict[f0factor][model] = list of scores
    data_dict = {
        "f1.00": {
            "natural": [],
            "SiFiGAN": [],
            "VAE_SiFiGAN_v1": [],
            "VAE_SiFiGAN_v2": []
        },
        "f0.50": {
            "SiFiGAN": [],
            "VAE_SiFiGAN_v1": [],
            "VAE_SiFiGAN_v2": []
        },
        "f2.00": {
            "SiFiGAN": [],
            "VAE_SiFiGAN_v1": [],
            "VAE_SiFiGAN_v2": []
        }
    }

    # read all CSV in input_dir
    pattern = os.path.join(input_dir, "*.csv")
    filelist = glob.glob(pattern)
    if len(filelist) == 0:
        print(f"No CSV files found in {input_dir}")
        return
    
    for csv_path in filelist:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 2:
                    continue
                wavpath = row[0].strip()
                score_str = row[1].strip()
                if not score_str.isdigit():
                    # skip header or invalid lines
                    continue
                score = float(score_str)
                model, pitch = classify_file(wavpath)
                # store score
                if pitch in data_dict:
                    if model in data_dict[pitch]:
                        data_dict[pitch][model].append(score)
                    else:
                        raise ValueError(f"Unknown model: {model}")
                else:
                    raise ValueError(f"Unknown pitch: {pitch}")

    # prepare results
    # we want to output: (pitch, model, count, mean, lower, upper, mean±margin)
    # order: f1.00: [natural,SiFiGAN,v1,v2], f0.50: [SiFiGAN,v1,v2], f2.00: [SiFiGAN,v1,v2]
    results = []

    # f1.00
    pitch = "f1.00"
    for model in ["natural", "SiFiGAN", "VAE_SiFiGAN_v1", "VAE_SiFiGAN_v2"]:
        scores = data_dict[pitch][model]
        n = len(scores)
        mean, lower, upper = compute_mean_and_ci(scores)
        if np.isnan(mean):
            margin = float('nan')
        else:
            margin = upper - mean
        results.append((pitch, model, n, mean, lower, upper, margin))
    
    # f0.50
    pitch = "f0.50"
    for model in ["SiFiGAN", "VAE_SiFiGAN_v1", "VAE_SiFiGAN_v2"]:
        scores = data_dict[pitch][model]
        n = len(scores)
        mean, lower, upper = compute_mean_and_ci(scores)
        if np.isnan(mean):
            margin = float('nan')
        else:
            margin = upper - mean
        results.append((pitch, model, n, mean, lower, upper, margin))

    # f2.00
    pitch = "f2.00"
    for model in ["SiFiGAN", "VAE_SiFiGAN_v1", "VAE_SiFiGAN_v2"]:
        scores = data_dict[pitch][model]
        n = len(scores)
        mean, lower, upper = compute_mean_and_ci(scores)
        if np.isnan(mean):
            margin = float('nan')
        else:
            margin = upper - mean
        results.append((pitch, model, n, mean, lower, upper, margin))

    # print to terminal
    print("f0factor,model,count,mean,lower95,upper95,mean±margin")
    for r in results:
        pitch, model, n, mean, lower, upper, margin = r
        if np.isnan(mean):
            print(f"{pitch},{model},{n},NaN,NaN,NaN,NaN")
        else:
            print(f"{pitch},{model},{n},{mean:.3f},{lower:.3f},{upper:.3f},{mean:.3f}±{margin:.3f}")

    # save to CSV
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["f0factor","model","count","mean","lower95","upper95","mean±margin"])
        for r in results:
            pitch, model, n, mean, lower, upper, margin = r
            if np.isnan(mean):
                writer.writerow([pitch, model, n, "NaN", "NaN", "NaN", "NaN"])
            else:
                writer.writerow([
                    pitch, model, n,
                    f"{mean:.3f}", f"{lower:.3f}", f"{upper:.3f}",
                    f"{mean:.3f}±{margin:.3f}"
                ])

    print(f"\nSaved result as {output_file}")

if __name__ == "__main__":
    args = parse_arguments()
    main()
