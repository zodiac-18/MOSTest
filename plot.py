import os
import glob
import csv
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import argparse
from shutil import copy2
import re

def parse_arguments():
    parser = argparse.ArgumentParser(description="Perform MOS analysis with additional distribution checks and ranking.")
    parser.add_argument("--input_dir", "-i", type=str, default="results", help="Directory containing MOS CSV files.")
    parser.add_argument("--output_file", "-o", type=str, default="results.csv", help="Output CSV file for MOS results.")
    parser.add_argument("--analysis_dir", "-a", type=str, default="analysis", help="Directory to save analysis results.")
    return parser.parse_args()

def compute_mean_and_ci(values, confidence=0.95):
    arr = np.array(values, dtype=float)
    n = len(arr)
    mean = np.mean(arr)
    std = np.std(arr, ddof=1)
    se = std / np.sqrt(n)
    margin = stats.t.ppf((1 + confidence) / 2., n - 1) * se
    return mean, mean - margin, mean + margin, margin

def classify_file(filepath):
    """
    f0 倍率を判定 (filename に f0.50, f1.00, f2.00 が含まれると仮定)
    """
    filename = os.path.basename(filepath)
    if "f0.50" in filename:
        return "f0.50"
    elif "f1.00" in filename:
        return "f1.00"
    elif "f2.00" in filename:
        return "f2.00"
    else:
        return "unknown"

def extract_segment_name(filepath):
    """
    ファイル名から「楽曲セグメント名」を取り出すためのヘルパー関数の例。
    例:
       filepath = "wav/set1/SiFiGAN/1st_color_seg1_f1.00.wav"
       → segment_name = "1st_color_seg1"
    """
    filename = os.path.basename(filepath)
    name_no_ext = filename.replace(".wav", "")
    # 例: "_f1.00"などを除去 (実際のファイル名パターンに合わせて調整)
    name_no_f = re.sub(r"_f\d\.\d\d", "", name_no_ext)
    return name_no_f

def check_distribution(data_dict, analysis_dir):
    """
    data_dict[f0][model][segment_name] = {
        "scores": [...],
        "file_path": ... 
    }
    の構造を想定。分布確認は、全セグメントの scores を合算してヒストグラムを作成。
    """
    os.makedirs(f"{analysis_dir}/fig", exist_ok=True)
    for f0, model_dict in data_dict.items():
        for model, seg_dict in model_dict.items():
            all_scores = []
            for seg_name, info in seg_dict.items():
                all_scores.extend(info["scores"])  # 全セグメントのスコアをまとめる

            if len(all_scores) == 0:
                continue

            # スコア分布のヒストグラム
            plt.hist(all_scores, bins=np.arange(0.5, 6, 1), alpha=0.7,
                     color='skyblue', density=True, label='Score Distribution')
            plt.title(f"Distribution: {model} (f0={f0})")
            plt.xlabel("MOS Score")
            plt.ylabel("Frequency")

            # 理論的な正規分布を重ねてプロット
            mean, std = np.mean(all_scores), np.std(all_scores)
            x = np.linspace(1, 5, 100)
            pdf = stats.norm.pdf(x, mean, std)
            plt.plot(x, pdf, 'k', linewidth=2, label='Normal Distribution')

            plt.legend()
            plt.savefig(f"{analysis_dir}/fig/{model}_f0_{f0}.png")
            plt.close()

            # Shapiro-Wilk検定
            stat, p = stats.shapiro(all_scores)
            print(f"Shapiro-Wilk Test for {model} (f0={f0}): W={stat:.3f}, p={p:.3e}")

def compute_medians(data_dict):
    """
    各 f0, 各 model について、すべてのセグメントの scores を合算し、その中央値を求める。
    """
    median_dict = {}
    for f0, model_dict in data_dict.items():
        median_dict[f0] = {}
        for model, seg_dict in model_dict.items():
            all_scores = []
            for seg_name, info in seg_dict.items():
                all_scores.extend(info["scores"])
            if all_scores:
                median_dict[f0][model] = np.median(all_scores)
            else:
                median_dict[f0][model] = None
    return median_dict

def rank_and_copy(data_dict, median_dict, analysis_dir):
    """
    1) 各 f0 について
    2) compare_pairs でモデルA,モデルBをペア比較
    3) セグメント毎に「AvgMOS(A), AvgMOS(B), |差分|」を算出
    4) 差分が大きい順に並べて
       - 全セグメントをCSVに出力 (ランキング全体)
       - 上位10セグメントのみコピー
    5) CSVにはサンプル数(セグメント総数)を記録
    """

    output_dir = os.path.join(analysis_dir, "compare_voice")
    os.makedirs(output_dir, exist_ok=True)

    compare_pairs = [
        ("SiFiGAN", "VAE_SiFiGAN_v1"),
        ("SiFiGAN", "VAE_SiFiGAN_v2"),
        ("VAE_SiFiGAN_v1", "VAE_SiFiGAN_v2"),
        # 必要に応じて ("Natural", "SiFiGAN") など追加
    ]

    for f0, model_dict in data_dict.items():
        for (modelA, modelB) in compare_pairs:
            # modelA と modelB が data_dict[f0] の中に存在しなければスキップ
            if modelA not in model_dict or modelB not in model_dict:
                continue

            seg_dictA = model_dict[modelA]  # seg_name -> {"scores": [...], "file_path": ...}
            seg_dictB = model_dict[modelB]

            # 共通するセグメントだけ比較
            segmentsA = set(seg_dictA.keys())
            segmentsB = set(seg_dictB.keys())
            common_segments = segmentsA.intersection(segmentsB)

            diff_list = []  # (seg_name, avgA, avgB, diff_val)
            for seg_name in common_segments:
                scoresA = seg_dictA[seg_name]["scores"]
                scoresB = seg_dictB[seg_name]["scores"]

                if len(scoresA) == 0 or len(scoresB) == 0:
                    continue

                avgA = np.mean(scoresA)
                avgB = np.mean(scoresB)
                diff_val = abs(avgA - avgB)
                assert len(scoresA) == len(scoresB)

                diff_list.append((seg_name, avgA, avgB, diff_val))

            # 差分が大きい順にソート
            diff_list.sort(key=lambda x: x[3], reverse=True)

            # コピー先フォルダ (上位10件)
            folder_path = os.path.join(output_dir, f"{modelA}_vs_{modelB}", f0)
            os.makedirs(folder_path, exist_ok=True)

            # モデルの全体中央値を取得
            medianA = median_dict[f0].get(modelA, None)
            medianB = median_dict[f0].get(modelB, None)

            # === CSV出力用 ===
            csv_path = os.path.join(folder_path, f"ranking_{modelA}_vs_{modelB}.csv")
            with open(csv_path, "w", encoding="utf-8", newline="") as f_csv:
                writer = csv.writer(f_csv)
                # ヘッダ
                writer.writerow([
                    "Rank",
                    "SegmentName",
                    "MOS_Difference",
                    f"{modelA}_AvgMOS",
                    f"{modelB}_AvgMOS",
                    f"{modelA}_Median",
                    f"{modelB}_Median"
                ])

                # 全セグメント書き出し (ランキング全体)
                for rank_idx, (seg_name, avgA, avgB, diff_val) in enumerate(diff_list, start=1):
                    row_data = [
                        rank_idx,
                        seg_name,
                        f"{diff_val:.3f}",
                        f"{avgA:.3f}",
                        f"{avgB:.3f}",
                        f"{medianA:.3f}" if medianA is not None else "",
                        f"{medianB:.3f}" if medianB is not None else ""
                    ]
                    writer.writerow(row_data)

                # 最後にサンプル数（セグメント数）を記録
                writer.writerow([])
                writer.writerow([f"Total segments: {len(diff_list)}"])
                writer.writerow([f"Total samples: {len(scoresB)}"])

            # === 上位10件だけコピー ===
            top_10 = diff_list[:10]
            for seg_name, avgA, avgB, diff_val in top_10:
                filepathA = seg_dictA[seg_name]["file_path"]
                filepathB = seg_dictB[seg_name]["file_path"]

                basenameA = os.path.basename(filepathA)
                basenameB = os.path.basename(filepathB)

                destA = os.path.join(folder_path, basenameA.replace(".wav", f"_{modelA}.wav"))
                destB = os.path.join(folder_path, basenameB.replace(".wav", f"_{modelB}.wav"))

                copy2(filepathA, destA)
                copy2(filepathB, destB)

def main():
    args = parse_arguments()

    # data_dict[f0][model][segment_name] = {
    #   "scores": [...],
    #   "file_path": "最後に読んだファイルのパス",
    # }
    data_dict = {
        "f0.50": {},
        "f1.00": {},
        "f2.00": {}
    }

    # CSV の読み込み
    for file in glob.glob(os.path.join(args.input_dir, "*.csv")):
        with open(file, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                file_path = row[0]
                score = float(row[1])

                # f0 分類
                f0 = classify_file(file_path)
                if f0 not in data_dict:
                    # もし unknown や想定外の f0 が来たらスキップ
                    continue

                # モデル名
                parts = file_path.split("/")
                if len(parts) >= 3:
                    model = parts[-2]
                else:
                    model = "unknown"

                # モデルの辞書が未初期化なら作る
                if model not in data_dict[f0]:
                    data_dict[f0][model] = {}

                # セグメント名を取り出す
                seg_name = extract_segment_name(file_path)
                if seg_name not in data_dict[f0][model]:
                    data_dict[f0][model][seg_name] = {
                        "scores": [],
                        "file_path": file_path
                    }

                data_dict[f0][model][seg_name]["scores"].append(score)
                # file_path は上書きでもOK (同じセグメントなら同じファイル想定の場合)

    # 分布確認
    check_distribution(data_dict, args.analysis_dir)

    # 各モデルの中央値
    median_dict = compute_medians(data_dict)

    # 全体ランキング出力 & 上位10のファイルコピー
    rank_and_copy(data_dict, median_dict, args.analysis_dir)

if __name__ == "__main__":
    main()
