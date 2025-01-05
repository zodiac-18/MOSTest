#!/bin/bash

# 既に各setにファイルが入った想定
# ファイル構造からリストを作成する

# ベースディレクトリ
BASE_DIR="wav"

# 処理するセット番号を指定（1～9をループ）
for SET_NUM in {1..9}; do
  # 対応するセットのディレクトリ
  SET_DIR="$BASE_DIR/set$SET_NUM"
  
  # 出力リストファイル
  LIST_FILE="$SET_DIR/Natural.list"
  
  # ディレクトリが存在するか確認
  if [ -d "$SET_DIR" ]; then
    echo "Generating list for set$SET_NUM..."
    
    # wavファイルを検索し、パス内の〇〇が完全に "SiFiGAN" と一致するもののみリスト化
    find "$SET_DIR" -type f -name "*.wav" | awk -F'/' '$0 ~ /Natural/ && $(NF-1) == "Natural"' > "$LIST_FILE"
    
    echo "List created: $LIST_FILE"
  else
    echo "Directory not found: $SET_DIR"
  fi
done
