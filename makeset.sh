#!/bin/bash

# 指定のコピー元ディレクトリ
SOURCE_DIR="/home/ogita23/nas01home/sifigan/SiFiGAN/egs/namine_ritsu/data/wav"

# 指定のコピー先ディレクトリ
DEST_DIR="/home/ogita23/mrnas03home/MOSTest/wav/set1/natural"

# 指定のファイル
FILES=(
    "namine_ritsu_1st_color_seg1.wav"
    "namine_ritsu_1st_color_seg18.wav"
    "namine_ritsu_ARROW_seg5.wav"
    "namine_ritsu_ARROW_seg13.wav"
    "namine_ritsu_BC_seg2.wav"
    "namine_ritsu_BC_seg13.wav"
    "namine_ritsu_BC_seg20.wav"
    "namine_ritsu_Closetoyou_seg5.wav"
    "namine_ritsu_Closetoyou_seg10.wav"
    "namine_ritsu_Closetoyou_seg24.wav"
    "namine_ritsu_ERROR_seg3.wav"
    "namine_ritsu_ERROR_seg21.wav"
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
