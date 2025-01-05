#!/usr/bin/env python3

import os
import sys
import glob
import argparse

import soundfile as sf
import pyloudnorm as pyln

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Recursively normalize all .wav files in a directory to -24dB using pyloudnorm."
    )
    parser.add_argument(
        "--root_dir", "-r", 
        type=str, 
        default="./wav/set1/", 
        help="Root directory to search wav files."
    )
    parser.add_argument(
        "--target_lufs", "-t",
        type=float,
        default=-24.0,
        help="Target loudness in dB LUFS (default: -24.0)."
    )
    return parser.parse_args()

def main():
    args = parse_arguments()

    # 指定されたディレクトリ（デフォルトはカレントディレクトリ）以下の.wavファイルを再帰的に検索
    pattern = os.path.join(args.root_dir, "**", "*.wav")
    filelist = glob.glob(pattern, recursive=True)

    print(f"Found {len(filelist)} .wav files in '{args.root_dir}'.")
    print(f"Normalizing each to {args.target_lufs:.1f} dB LUFS...\n")

    meter = None
    processed_count = 0

    for wav_path in filelist:
        # 波形読み込み
        try:
            data, sr = sf.read(wav_path)
        except Exception as e:
            print(f"Could not read file: {wav_path}. Skipped. Error: {e}")
            continue

        # モノラル・ステレオなどチャンネル数確認
        # pyloudnorm.Meter は一度だけ sr 指定して使い回しでも構わない
        # ただしサンプリングレートが毎回違うかもしれないので、都度作成
        meter = pyln.Meter(sr)  # EBU R128

        # ラウドネス計測
        loudness = meter.integrated_loudness(data)

        # すでに目標より大幅に大きい or 小さい音量の場合、正規化
        # pyloudnorm では下記で波形を -24 dB LUFS に合わせる
        normalized_data = pyln.normalize.loudness(data, loudness, args.target_lufs)

        # 上書き保存
        # (バックアップを取りたい場合は別ファイルに書くかオプションを作る)
        try:
            sf.write(wav_path, normalized_data, sr)
            processed_count += 1
            print(f"[{processed_count}] Normalized: {wav_path}  (original loudness {loudness:.2f} LUFS)")
        except Exception as e:
            print(f"Could not write file: {wav_path}. Error: {e}")
            continue

    print("\nDone.")
    print(f"Total processed: {processed_count}/{len(filelist)}")

if __name__ == "__main__":
    main()
