# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository

This is a fork/local copy of the official **YOLOv7** object detector (Wang, Bochkovskiy, Liao 2023). The upstream README is at `README.md`. Personal notes from this user's runs live in `readme.txt` (commands actually used, environment versions, training logs from prior runs). Prefer `readme.txt` over `README.md` for "how *this* user runs things on *this* machine."

The user runs this from a conda env named `automl` (see `readme.txt`); deps are pinned via the `AutoMLTraining` and `modelcat` editable installs at `/home/rb/automltraining/`. Notable installed versions: `torch 1.13.1`, `torchvision 0.14.1`, `numpy 1.24.3`, `python 3.10`. The repo's `requirements.txt` is the upstream one and is broader than what's actually installed — don't run `pip install -r requirements.txt` blindly.

## Common commands

**Training (single GPU)** — p5 models (yolov7, yolov7-tiny, yolov7x):
```
python train.py --workers 8 --device 0 --batch-size 32 --data data/coco.yaml --img 640 640 \
  --cfg cfg/training/yolov7.yaml --weights '' --name yolov7 --hyp data/hyp.scratch.p5.yaml
```

**Training p6 models** (yolov7-w6, -e6, -d6, -e6e at 1280px) uses `train_aux.py` instead of `train.py` and `hyp.scratch.p6.yaml`.

**Finetune from a pretrained checkpoint** — pass `--weights yolov7_training.pt` (note: the `_training.pt` variants, not the inference `.pt` variants) and use `cfg/training/yolov7-custom.yaml` + `data/hyp.scratch.custom.yaml` for custom datasets. The user's "retrain" workflow (per `readme.txt`) reduces `lr0` and `lrf` in the hyp YAML by 10x before running.

**Multi-GPU**: prepend `python -m torch.distributed.launch --nproc_per_node N --master_port 9527` and add `--sync-bn --device 0,1,...`.

**Eval / test** (mAP on COCO val):
```
python test.py --data data/coco.yaml --img 640 --batch 32 --conf 0.001 --iou 0.65 \
  --device 0 --weights yolov7.pt --name yolov7_640_val
```
`test.py` also exposes a programmatic `run(...)` function (added locally — see uncommitted diff) supporting tasks `val`/`test`/`speed`/`study`. The `study` task sweeps `--img-size` from 256→1536 and zips the results.

**Inference**:
```
python detect.py --weights yolov7.pt --conf 0.25 --img-size 640 --source <image_or_video_or_dir>
```

**Export** (ONNX with end-to-end NMS for TensorRT):
```
python export.py --weights yolov7-tiny.pt --grid --end2end --simplify \
  --topk-all 100 --iou-thres 0.65 --conf-thres 0.35 --img-size 640 640 --max-wh 640
```

**Dataset prep**: `bash scripts/get_coco.sh` downloads COCO2017 images + YOLO-format labels into `./coco/`. The cwd already has `coco/` populated and a top-level `train2017.zip` left over from a prior download.

There is **no test suite, linter, or build step** — this is a research codebase. Validation is via running `test.py` against COCO and checking mAP.

## Architecture

The codebase has three parallel layers — model definition (YAML), Python model code, and training/eval scripts — all glued through string-keyed YAML configs.

**Model definitions live in YAML, not Python.** Each `cfg/training/*.yaml` (training-time) and `cfg/deploy/*.yaml` (inference-time, fused) describes a network as a list of `[from, number, module, args]` rows. `models/yolo.py::parse_model` reads these and instantiates layers from `models/common.py` (standard blocks: Conv, RepConv, SPPCSPC, etc.) and `models/experimental.py`. The training/deploy split exists because RepConv blocks and IDetect heads get **fused** for inference (RepVGG-style re-parameterization) — see `tools/reparameterization.ipynb` for the conversion. Variants:
- **p5** family (yolov7, yolov7-tiny, yolov7x): 640px input, trained with `train.py`.
- **p6** family (yolov7-w6, -e6, -d6, -e6e): 1280px input with auxiliary heads, **must** use `train_aux.py` (different loss + aux-head plumbing). Don't cross the streams.

**Hyperparameter YAMLs (`data/hyp.scratch.*.yaml`)** are separate from architecture YAMLs and control the optimizer, augmentation, and loss weights. `hyp.scratch.p5.yaml` for p5 training-from-scratch, `hyp.scratch.p6.yaml` for p6, `hyp.scratch.tiny.yaml` for yolov7-tiny, `hyp.scratch.custom.yaml` for finetuning custom datasets.

**Data flow during training**: `train.py` → `utils/datasets.py::create_dataloader` (LoadImagesAndLabels with mosaic, mixup, paste-in augmentation) → `models/yolo.Model` forward → `utils/loss.ComputeLossOTA` (the OTA assigner is the default; `ComputeLoss` is the simpler one) → optimizer → after each epoch calls back into `test.py::test` for mAP. Outputs go to `runs/train/<name>{N}/` (auto-incremented).

**Key util modules to know about**:
- `utils/general.py`: NMS, IoU, file/path helpers, `check_*` validators called all over `train.py`.
- `utils/loss.py`: `ComputeLossOTA` (default; SimOTA-style label assignment), `ComputeLoss` (legacy), `ComputeLossAuxOTA` (for p6/aux-head models).
- `utils/datasets.py`: dataloader and all augmentation logic. Cache files (`*.cache`) are written next to the label dirs — delete them if you change label format or are moving from another YOLO repo.
- `utils/torch_utils.py`: `ModelEMA`, fused-layer helpers, device selection.
- `utils/wandb_logging/`: optional W&B integration; `wandb` is gated behind import-existence checks.

**Inference path** (`detect.py`) uses `attempt_load` from `models/experimental.py`, traces the model via `TracedModel` (utils/torch_utils), then runs NMS from `utils.general.non_max_suppression`. The `traced_model.pt` at the repo root is a leftover from a prior trace.

## Working in this repo — gotchas

- **p5 vs p6 mismatch is silent and slow to fail.** Using `train.py` with a `-w6/-e6/-d6/-e6e` cfg, or vice versa, will train but produce garbage — always pair train script + cfg + hyp.
- **`--weights ''` means train from scratch**, while `--weights yolov7_training.pt` finetunes. Note `_training.pt` is different from `yolov7.pt` (the latter is the *deploy/fused* checkpoint and can't be resumed for training).
- **Cache files in dataset dirs** (`train2017.cache`, `val2017.cache`) are sticky — README explicitly says delete them when switching from another YOLO version.
- **Class count**: `cfg/training/*.yaml` has `nc: 80` hardcoded for COCO. For custom datasets, copy to a new file (e.g., `yolov7-custom.yaml`) and edit `nc` plus the `data/*.yaml` `nc:`/`names:`. Mismatches throw obscure shape errors deep in the model.
- **Outputs auto-increment**: `runs/train/yolov7`, `runs/train/yolov72`, etc. Use `--exist-ok` to overwrite; otherwise expect new numbered dirs each run.
- The user's `readme.txt` documents that they typically reduce `lr0` and `lrf` in the hyp YAML by 10x for retrains — preserve this convention if continuing their training workflow.
