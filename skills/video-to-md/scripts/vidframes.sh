#!/usr/bin/env bash
# vidframes.sh <video> [outdir] [interval_sec] [scene_threshold]
#
# 영상 하나에 대해 (1) 메타데이터 (2) 장면전환 지도 (3) 시각이 파일명에 박힌 프레임
# 세 가지를 한 번에 만든다. 프레임은 <outdir>/<초>s.jpg 로 저장된다.
#
# interval 을 생략하면 재생시간을 보고 40~70장 정도가 나오도록 자동으로 정한다.

set -euo pipefail

VIDEO="${1:?usage: vidframes.sh <video> [outdir] [interval_sec] [scene_threshold]}"
OUTDIR="${2:-./frames}"
INTERVAL="${3:-auto}"
SCENE="${4:-0.06}"

[ -f "$VIDEO" ] || { echo "no such file: $VIDEO" >&2; exit 1; }
command -v ffprobe >/dev/null || { echo "ffprobe not found" >&2; exit 1; }

mkdir -p "$OUTDIR"

echo "=== METADATA ==="
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$VIDEO" | cut -d. -f1)
ffprobe -v error -select_streams v:0 \
  -show_entries stream=codec_name,width,height,r_frame_rate,nb_frames \
  -of default=noprint_wrappers=1 "$VIDEO"
echo "duration_sec=$DUR"

NAUDIO=$(ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$VIDEO" | wc -l | tr -d ' ')
if [ "$NAUDIO" -gt 0 ]; then
  echo "audio=YES ($NAUDIO stream)  -> 전사를 먼저 시도할 것. 말이 핵심 정보일 수 있다."
else
  echo "audio=NO  -> 화면 텍스트가 유일한 정보원. 프레임 판독에 집중할 것."
fi

echo
echo "=== SCENE CHANGES (threshold=$SCENE) ==="
echo "전환이 몰린 구간 = 반드시 판독. 전환이 없는 긴 구간 = 정적/반복 구간(그 길이 자체가 발견)."
ffmpeg -hide_banner -i "$VIDEO" -vf "select='gt(scene,${SCENE})',showinfo" \
  -vsync vfr -f null - 2>&1 | grep -o 'pts_time:[0-9.]*' | cut -d: -f2 | nl || echo "(전환 없음)"

# 간격 자동 결정: 40~70장 목표
if [ "$INTERVAL" = "auto" ]; then
  if   [ "$DUR" -le 200 ];  then INTERVAL=3
  elif [ "$DUR" -le 400 ];  then INTERVAL=5
  elif [ "$DUR" -le 900 ];  then INTERVAL=10
  elif [ "$DUR" -le 1800 ]; then INTERVAL=20
  elif [ "$DUR" -le 3600 ]; then INTERVAL=40
  else                           INTERVAL=60
  fi
fi

echo
echo "=== EXTRACTING (every ${INTERVAL}s -> $OUTDIR) ==="
N=0
for t in $(seq 2 "$INTERVAL" "$DUR"); do
  ffmpeg -hide_banner -v error -ss "$t" -i "$VIDEO" -frames:v 1 -q:v 2 \
    "$OUTDIR/$(printf %05d "$t")s.jpg" -y
  N=$((N+1))
done
echo "$N frames -> $OUTDIR  (파일명 숫자 = 해당 프레임의 초)"
echo
echo "다음: 프레임을 시간 순으로 판독. 글씨가 작으면 잘라서 확대한다:"
echo "  ffmpeg -v error -ss <t> -i \"$VIDEO\" -frames:v 1 \\"
echo "    -vf \"crop=<w>:<h>:<x>:<y>,scale=<w*3>:<h*3>:flags=lanczos\" -q:v 2 zoom.jpg -y"
