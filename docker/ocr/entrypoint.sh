#!/bin/sh
set -eu
cd /work
FORCE_ARG=""
if [ "${FORCE:-0}" = "1" ]; then
  FORCE_ARG="--force"
fi
exec python evals/scripts/run_multimodal_ocr.py \
  --slide-dir "${SLIDE_DIR}" \
  --out-dir "${OUT_DIR}" \
  --engine "${ENGINE}" \
  --preprocess "${PREPROCESS}" \
  ${SLIDES:+--slides "$SLIDES"} \
  ${FORCE_ARG}
