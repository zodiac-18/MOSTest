#!/bin/bash

# 指定のコピー元ディレクトリ
SOURCE_DIR="/home/ogita23/nas01home/sifigan/SiFiGAN/egs/namine_ritsu/exp/vae_sifigan_mel/wav/500000"

# 指定のコピー先ディレクトリ
DEST_DIR="/home/ogita23/mrnas03home/MOSTest/wav/set1/VAE-SiFiGAN_v1"

# 指定のファイル
FILES=(
    "namine_ritsu_1st_color_seg1_f1.00.wav"
    "namine_ritsu_1st_color_seg18_f1.00.wav"
    "namine_ritsu_ARROW_seg5_f1.00.wav"
    "namine_ritsu_ARROW_seg13_f1.00.wav"
    "namine_ritsu_BC_seg2_f1.00.wav"
    "namine_ritsu_BC_seg13_f1.00.wav"
    "namine_ritsu_BC_seg20_f1.00.wav"
    "namine_ritsu_Closetoyou_seg5_f1.00.wav"
    "namine_ritsu_Closetoyou_seg10_f1.00.wav"
    "namine_ritsu_Closetoyou_seg24_f1.00.wav"
    "namine_ritsu_ERROR_seg3_f1.00.wav"
    "namine_ritsu_ERROR_seg21_f1.00.wav"
    "namine_ritsu_1st_color_seg1_f0.50.wav"
    "namine_ritsu_1st_color_seg18_f0.50.wav"
    "namine_ritsu_ARROW_seg5_f0.50.wav"
    "namine_ritsu_ARROW_seg13_f0.50.wav"
    "namine_ritsu_BC_seg2_f0.50.wav"
    "namine_ritsu_BC_seg13_f0.50.wav"
    "namine_ritsu_BC_seg20_f0.50.wav"
    "namine_ritsu_Closetoyou_seg5_f0.50.wav"
    "namine_ritsu_Closetoyou_seg10_f0.50.wav"
    "namine_ritsu_Closetoyou_seg24_f0.50.wav"
    "namine_ritsu_ERROR_seg3_f0.50.wav"
    "namine_ritsu_ERROR_seg21_f0.50.wav"
    "namine_ritsu_1st_color_seg1_f2.00.wav"
    "namine_ritsu_1st_color_seg18_f2.00.wav"
    "namine_ritsu_ARROW_seg5_f2.00.wav"
    "namine_ritsu_ARROW_seg13_f2.00.wav"
    "namine_ritsu_BC_seg2_f2.00.wav"
    "namine_ritsu_BC_seg13_f2.00.wav"
    "namine_ritsu_BC_seg20_f2.00.wav"
    "namine_ritsu_Closetoyou_seg5_f2.00.wav"
    "namine_ritsu_Closetoyou_seg10_f2.00.wav"
    "namine_ritsu_Closetoyou_seg24_f2.00.wav"
    "namine_ritsu_ERROR_seg3_f2.00.wav"
    "namine_ritsu_ERROR_seg21_f2.00.wav"
)

# コピー先ディレクトリが存在しない場合は作成
mkdir -p "$DEST_DIR"

# ファイルのコピーと名前変更
for FILE in "${FILES[@]}"; do
    # コピー元ファイルのパス
    SOURCE_FILE="$SOURCE_DIR/$FILE"

    # コピー先ファイルのパス（名前変更）
    DEST_FILE="$DEST_DIR/${FILE#namine_ritsu_}"

    # ファイルが存在するかチェックしてコピー
    if [ -e "$SOURCE_FILE" ]; then
        cp "$SOURCE_FILE" "$DEST_FILE"
        echo "Copied and renamed: $SOURCE_FILE -> $DEST_FILE"
    else
        echo "File not found: $SOURCE_FILE"
    fi
done
