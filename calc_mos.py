import os
import glob
import csv
import argparse
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

def parse_arguments():
    parser = argparse.ArgumentParser(description="Perform MOS analysis, Welch's t-test, and visualization.")
    parser.add_argument("--input_dir", "-i", type=str, default="results", help="Directory containing CSV files.")
    parser.add_argument("--output_file", "-o", type=str, default="results.csv", help="Output CSV file for MOS results.")
    parser.add_argument("--analysis_dir", "-a", type=str, default="analysis", help="Directory to save analysis results.")
    return parser.parse_args()

def compute_mean_and_ci(values, confidence=0.95):
    arr = np.array(values, dtype=float)
    n = len(arr)
    mean = np.mean(arr)
    std = np.std(arr, ddof=1)
    se = std / np.sqrt(n)
    margin = stats.t.ppf((1 + confidence) / 2., n-1) * se
    return mean, mean - margin, mean + margin, margin

def classify_file(filepath):
    filename = os.path.basename(filepath)
    dirs = filepath.split("/")
    model = dirs[2] if len(dirs) > 2 else "unknown_model"
    if model == "Natural":
        return model, "f1.00"
    if "f0.50" in filename:
        return model, "f0.50"
    elif "f1.00" in filename:
        return model, "f1.00"
    elif "f2.00" in filename:
        return model, "f2.00"
    return model, "f1.00"

def perform_ttest(group1, group2):
    t_stat, p_value = stats.ttest_ind(group1, group2, equal_var=False)
    return t_stat, p_value

def compute_effect_sizes(group1, group2):
    """
    Compute Cohen's d and Hedge's g for two independent groups.
    """
    mean1, mean2 = np.mean(group1), np.mean(group2)
    s1, s2 = np.std(group1, ddof=1), np.std(group2, ddof=1)
    n1, n2 = len(group1), len(group2)
    pooled_sd = np.sqrt(((n1 - 1) * s1 ** 2 + (n2 - 1) * s2 ** 2) / (n1 + n2 - 2))
    d = (mean1 - mean2) / pooled_sd
    # Correction factor for Hedge's g
    correction = 1 - (3 / (4 * (n1 + n2) - 9))
    g = d * correction
    return d, g

def interpret_ttest(t_stat, p_value, group1_mean, group2_mean, d, g):
    significance = "Significant" if p_value < 0.05 else "Not significant"
    winner = "Group 1" if group1_mean > group2_mean else "Group 2"
    return f"t={t_stat:.3f}, p={p_value:.4e}, d={d:.3f}, g={g:.3f} ({significance}), Winner: {winner}"

def save_results_and_ttests(results, ttest_results, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    results_path = os.path.join(output_dir, "results.txt")
    with open(results_path, "w") as f:
        f.write("MOS Results\n")
        for r in results:
            f.write(f"{r}\n")
        f.write("\nT-Test Results\n")
        for pitch, comparisons in ttest_results.items():
            f.write(f"\nResults for f0={pitch}:\n")
            for comp, result in comparisons.items():
                f.write(f"{comp}: {result}\n")
    print(f"Results saved to {results_path}")

def plot_results(data_dict, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    colors = {
        "Natural": "#8dc891",  # 明るいグリーン
        "SiFiGAN": "#5a9bd4",  # 明るいブルー
        "VAE_SiFiGAN_v1": "#f4a261",  # 明るいオレンジ
        "VAE_SiFiGAN_v2": "#e76f51"  # 明るいレッド
    }
    for f0 in data_dict:
        models = list(data_dict[f0].keys())
        means, errors, counts = [], [], []
        for model in models:
            scores = data_dict[f0][model]
            mean, lower, upper, margin = compute_mean_and_ci(scores)
            means.append(mean)
            errors.append(margin)
            counts.append(len(scores))
        plt.figure(figsize=(6, 6), dpi=600)
        x = np.arange(len(models))
        bars = plt.bar(x, means, yerr=errors, capsize=5, width=0.6, color=[colors[m] for m in models])
        for i, bar in enumerate(bars):
            plt.text(bar.get_x() + bar.get_width() / 2, 1.05, f"{means[i]:.2f}", ha='center', va='bottom', size=12, weight='bold')
        plt.rcParams['axes.axisbelow'] = True
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.xticks(x, models, rotation=45)
        plt.ylim(1, 5)
        plt.yticks(np.arange(1, 5.1, 0.5))
        plt.ylabel("MOS")
        plt.title(f"MOS Scores for {f0} (n={sum(counts) // len(counts)})")
        output_path = os.path.join(output_dir, f"MOS_f0_{f0}.png")
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()

def main():
    args = parse_arguments()
    data_dict = {"f1.00": {}, "f0.50": {}, "f2.00": {}}
    models = ["Natural", "SiFiGAN", "VAE_SiFiGAN_v1", "VAE_SiFiGAN_v2"]
    for f0 in data_dict:
        data_dict[f0] = {model: [] for model in models if model != "Natural" or f0 == "f1.00"}
    for file in glob.glob(os.path.join(args.input_dir, "*.csv")):
        with open(file, "r") as f:
            for row in csv.reader(f):
                if len(row) < 2 or not row[1].isdigit():
                    continue
                model, pitch = classify_file(row[0])
                score = float(row[1])
                if model in data_dict[pitch]:
                    data_dict[pitch][model].append(score)
    results, ttest_results = [], {}
    for pitch in data_dict:
        if pitch == "f1.00":
            comparisons = [("Natural", "SiFiGAN"), ("Natural", "VAE_SiFiGAN_v1"), ("Natural", "VAE_SiFiGAN_v2"), ("SiFiGAN", "VAE_SiFiGAN_v1"), ("SiFiGAN", "VAE_SiFiGAN_v2"), ("VAE_SiFiGAN_v1", "VAE_SiFiGAN_v2")]
        else:
            comparisons = [("SiFiGAN", "VAE_SiFiGAN_v1"), ("SiFiGAN", "VAE_SiFiGAN_v2"), ("VAE_SiFiGAN_v1", "VAE_SiFiGAN_v2")]
        ttest_results[pitch] = {}
        for model in data_dict[pitch]:
            scores = data_dict[pitch][model]
            mean, lower, upper, margin = compute_mean_and_ci(scores)
            results.append(f"{pitch}, {model}: MOS={mean:.3f}±{margin:.3f}, 95% CI=({lower:.3f}, {upper:.3f}), n={len(scores)}")
        for model1, model2 in comparisons:
            if model1 in data_dict[pitch] and model2 in data_dict[pitch]:
                scores1, scores2 = data_dict[pitch][model1], data_dict[pitch][model2]
                t_stat, p_value = perform_ttest(scores1, scores2)
                mean1, mean2 = np.mean(scores1), np.mean(scores2)
                cohen_d, hedges_g = compute_effect_sizes(scores1, scores2)
                result = interpret_ttest(t_stat, p_value, mean1, mean2, cohen_d, hedges_g)
                ttest_results[pitch][f"{model1} vs {model2}"] = result
    save_results_and_ttests(results, ttest_results, args.analysis_dir)
    plot_results(data_dict, args.analysis_dir + "/fig")

if __name__ == "__main__":
    main()
