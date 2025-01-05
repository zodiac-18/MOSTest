#!/bin/bash

# 各setに入れるファイルのリストを用意した想定
# natural_flag の設定
natural_flag=True

# コピー元ディレクトリ
SOURCE_DIR="/home/ogita23/nas01home/sifigan/SiFiGAN/egs/namine_ritsu/data/wav"

# ベースコピー先ディレクトリ
BASE_DEST_DIR="/home/ogita23/mrnas03home/MOSTest/wav"

# ベースファイルリストディレクトリ
BASE_FILE_LIST_DIR="/home/ogita23/mrnas03home/MOSTest/wav"

# 処理するセット番号を指定（1～9をループ）
for SET_NUM in {1..9}; do
  # 対応するコピー先ディレクトリ
  DEST_DIR="$BASE_DEST_DIR/set$SET_NUM/Natural"
  
  # 対応するファイルリスト
  FILE_LIST="$BASE_FILE_LIST_DIR/set$SET_NUM/set$SET_NUM.list"
  
  # コピー先ディレクトリが存在しない場合は作成
  mkdir -p "$DEST_DIR"
  
  # ファイルリストが存在するかチェック
  if [ -e "$FILE_LIST" ]; then
    echo "Processing set$SET_NUM..."
    
    # 一時的なファイル名リストを保持する配列
    declare -A UNIQUE_FILES
    
    # ファイルリストを読み取って処理
    while IFS= read -r FILE; do
      # natural_flag=True の場合、`f` 以下を無視してファイル名を生成
      if [ "$natural_flag" = True ]; then
        BASE_NAME=$(echo "$FILE" | sed 's/_f[0-9.]*.wav$/.wav/')
      else
        BASE_NAME="$FILE"
      fi
      
      # コピー元ファイルのパス
      SOURCE_FILE="$SOURCE_DIR/$BASE_NAME"
      
      # コピー先ファイルのパス（名前変更）
      DEST_FILE="$DEST_DIR/${BASE_NAME#namine_ritsu_}"
      
      # ファイルの一意性をチェックしてコピー
      if [ -z "${UNIQUE_FILES[$BASE_NAME]}" ]; then
        UNIQUE_FILES["$BASE_NAME"]=1

        # ファイルが存在するかチェックしてコピー
        if [ -e "$SOURCE_FILE" ]; then
          cp "$SOURCE_FILE" "$DEST_FILE"
          echo "Copied and renamed: $SOURCE_FILE -> $DEST_FILE"
        else
          echo "File not found: $SOURCE_FILE"
        fi
      fi
    done < "$FILE_LIST"
  else
    echo "File list not found for set$SET_NUM: $FILE_LIST"
  fi
done
