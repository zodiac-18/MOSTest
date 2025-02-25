#!/bin/bash
# コピー元ディレクトリ（音声合成後のファイルが入っている場所）
SOURCE_DIR="/home/ogita23/mrnas04home/VAE-SiFiGAN/egs/namine_ritsu/data/wav"
# 使用する method 名（任意に指定）
METHOD_NAME="Natural"
# コピー先のベースディレクトリ（例: wav 以下）
BASE_DIR="wav"

# 対象の f 値（ディレクトリ名に使われる部分）
f_values=("")
# 対象の set 番号（例: set1～set9）
set_numbers=(1 2 3 4 5 6 7 8 9)

for set_num in "${set_numbers[@]}"; do
  SET_DIR="${BASE_DIR}/set${set_num}"
  for f_val in "${f_values[@]}"; do
    # 各 set 内の f 値ごとのリストファイル（例: wav/set1/set1_f0.50.list）
    LIST_FILE="${SET_DIR}/set${set_num}_f1.00.list"
    if [ ! -f "$LIST_FILE" ]; then
      echo "List file not found: $LIST_FILE"
      continue
    fi
    # コピー先ディレクトリ（例: wav/set1/f0.50/{method_name}）
    DEST_DIR="${SET_DIR}/f1.00/${METHOD_NAME}"
    mkdir -p "$DEST_DIR"
    # 出力するリストファイル（コピー先のwavファイルのパスを記録、DEST_DIR以下に配置）
    OUTPUT_LIST="${SET_DIR}/f1.00/${METHOD_NAME}.list"
    # 既存の内容があればクリア
    > "$OUTPUT_LIST"
    
    while IFS= read -r file; do
      # ファイル名が末尾に _f◯.〇〇.wav となっているか確認
      if [[ "$file" =~ \.wav$ ]]; then
        SRC_FILE="${SOURCE_DIR}/${file}"
        if [ ! -f "$SRC_FILE" ]; then
          echo "Source file not found: $SRC_FILE"
          continue
        fi
        # 変換後のファイル名：先頭の "namine_ritsu_" と末尾の "_f◯.〇〇" を削除
        dest_filename=$(echo "$file" | sed -E "s/^namine_ritsu_//")
        DEST_FILE="${DEST_DIR}/${dest_filename}"
        cp "$SRC_FILE" "$DEST_FILE"
        echo "Copied: $SRC_FILE -> $DEST_FILE"
        # コピー先ファイルのパスを出力リストに追記
        echo "$DEST_FILE" >> "$OUTPUT_LIST"
      else
        echo "Skipping file (f value mismatch): $file"
      fi
    done < "$LIST_FILE"
  done
done
