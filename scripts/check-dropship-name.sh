#!/usr/bin/env bash
# Kiểm tra tên file/thư mục theo quy chuẩn trong docs/dropship-file-naming.md
#
#   scripts/check-dropship-name.sh <ten-file> [...]
#   ls | scripts/check-dropship-name.sh -
#
# Thoát 0 nếu tất cả hợp lệ, 1 nếu có ít nhất một tên sai.

set -u

BRANDS="velahush footrevive theraease allvibe zela market ops"
TYPES="research competitor strategy copy prompt creative audit spec asset report"
BANNED="final latest new copy final2 ban-cuoi"

fail=0

err() { printf '  \033[31m✗\033[0m %s\n' "$1"; }
ok()  { printf '\033[32m✓\033[0m %s\n' "$1"; }

in_list() {
  local needle=$1 item
  shift
  for item in $1; do [ "$item" = "$needle" ] && return 0; done
  return 1
}

check() {
  local name=$1
  local base=$name ext="" errors=0

  printf '\033[1m%s\033[0m\n' "$name"

  # Thư mục (không có phần mở rộng) được phép bỏ trường version.
  if [[ $name == *.* ]]; then
    ext=${name##*.}
    base=${name%.*}
    if [[ ! $ext =~ ^[a-z0-9]+$ ]]; then
      err "phần mở rộng '.$ext' phải viết thường"
      errors=1
    fi
  fi

  if [[ $base =~ [A-Z] ]]; then
    err "có chữ hoa — toàn bộ tên phải viết thường"
    errors=1
  fi
  if [[ $base == *" "* ]]; then
    err "có dấu cách — dùng '-' thay cho dấu cách"
    errors=1
  fi
  if [[ $base =~ \(|\) ]]; then
    err "có ngoặc đơn — dấu hiệu bản sao do Drive tự sinh, dùng trường vNN"
    errors=1
  fi

  local word
  for word in $BANNED; do
    if [[ $base == *"$word"* ]]; then
      err "chứa từ cấm '$word' — phiên bản phải nằm ở trường vNN"
      errors=1
    fi
  done

  IFS='_' read -r -a f <<< "$base"
  local n=${#f[@]}

  if [ "$n" -lt 4 ] || [ "$n" -gt 5 ]; then
    err "có $n trường, cần 4 (thư mục) hoặc 5 (file): <brand>_<type>_<slug>_<YYYYMMDD>_v<NN>"
    [ "$errors" -eq 1 ] || errors=1
    fail=1
    return
  fi

  in_list "${f[0]}" "$BRANDS" || {
    err "brand '${f[0]}' không có trong bảng mã: $BRANDS"
    errors=1
  }
  in_list "${f[1]}" "$TYPES" || {
    err "type '${f[1]}' không có trong bảng mã: $TYPES"
    errors=1
  }

  if [[ ! ${f[2]} =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
    err "slug '${f[2]}' chỉ được dùng a-z, 0-9 và '-'"
    errors=1
  fi
  if [[ ${f[2]} == "${f[0]}"* || ${f[2]} == *"${f[1]}"* ]]; then
    err "slug '${f[2]}' lặp lại brand hoặc type — bỏ phần lặp đi"
    errors=1
  fi

  if [[ ! ${f[3]} =~ ^[0-9]{8}$ ]]; then
    err "ngày '${f[3]}' phải đúng dạng YYYYMMDD (liền, không gạch)"
    errors=1
  else
    local m=${f[3]:4:2} d=${f[3]:6:2}
    if [ "$((10#$m))" -lt 1 ] || [ "$((10#$m))" -gt 12 ] \
       || [ "$((10#$d))" -lt 1 ] || [ "$((10#$d))" -gt 31 ]; then
      err "ngày '${f[3]}' không phải một ngày có thật"
      errors=1
    fi
  fi

  if [ "$n" -eq 5 ]; then
    if [[ ! ${f[4]} =~ ^v[0-9]{2}$ ]]; then
      err "version '${f[4]}' phải đúng dạng vNN, ví dụ v01"
      errors=1
    fi
  elif [ -n "$ext" ]; then
    err "thiếu trường version — file bắt buộc kết thúc bằng _vNN"
    errors=1
  fi

  if [ "$errors" -eq 0 ]; then
    ok "hợp lệ"
  else
    fail=1
  fi
}

if [ "$#" -eq 0 ]; then
  sed -n '1,8p' "$0" | sed 's/^# \{0,1\}//'
  exit 2
fi

if [ "$1" = "-" ]; then
  while IFS= read -r line; do
    [ -n "$line" ] && check "$line"
  done
else
  for arg in "$@"; do
    check "$(basename "$arg")"
  done
fi

exit "$fail"
