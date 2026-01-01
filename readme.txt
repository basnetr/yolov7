# used automl and installed seaborn

For retraining:
in hyp*.yaml changed lr0 and lrf (divided original by 10)

# Retrain
python train.py --workers 8 --device 0 --batch-size 24 --data data/coco.yaml --img 640 640 --cfg cfg/training/yolov7.yaml --weights 'yolov7_training.pt' --name yolov7_new --hyp data/hyp.scratch.p5.yaml
# Inference on an image
python detect.py --weights /home/ramesh/automltraining/yolov7/runs/train/yolov7_new3/weights/best.pt --conf 0.25 --img-size 640 --source inference/images/horses.jpg

# Retrain yolov7 tiny
python train.py --workers 8 --device 0 --batch-size 24 --data data/coco.yaml --img 640 640 --cfg cfg/training/yolov7-tiny.yaml --weights 'yolov7-tiny.pt' --name yolov7-tiny_new --hyp data/hyp.scratch.tiny.yaml

python detect.py --weights /home/ramesh/automltraining/yolov7/runs/train/yolov7-tiny_new/weights/best.pt --conf 0.25 --img-size 640 --source inference/images/horses.jpg

yolov7 logs:
Starting training for 1 epochs...

     Epoch   gpu_mem       box       obj       cls     total    labels  img_size
       0/0     11.2G   0.02282   0.02438  0.006101    0.0533       330       640: 100%|██████████████████████████████████████████████████████████████████████████████████████████| 4929/4929 [1:47:57<00:00,  1.31s/it]
               Class      Images      Labels           P           R      mAP@.5  mAP@.5:.95:   0%|                                                                                            | 0/105 [00:00<?, ?it/s]/home/ramesh/miniconda3/envs/automl/lib/python3.10/site-packages/torch/functional.py:504: UserWarning: torch.meshgrid: in an upcoming release, it will be required to pass the indexing argument. (Triggered internally at ../aten/src/ATen/native/TensorShape.cpp:3190.)
  return _VF.meshgrid(tensors, **kwargs)  # type: ignore[attr-defined]
               Class      Images      Labels           P           R      mAP@.5  mAP@.5:.95: 100%|██████████████████████████████████████████████████████████████████████████████████| 105/105 [01:51<00:00,  1.06s/it]
                 all        5000       36335       0.728       0.631       0.686       0.491
1 epochs completed in 1.832 hours.

Fusing layers... 
RepConv.fuse_repvgg_block
RepConv.fuse_repvgg_block
RepConv.fuse_repvgg_block
IDetect.fuse
Model Summary: 314 layers, 36907898 parameters, 6194944 gradients
               Class      Images      Labels           P           R      mAP@.5  mAP@.5:.95: 100%|██████████████████████████████████████████████████████████████████████████████████| 105/105 [00:47<00:00,  2.22it/s]
                 all        5000       36335        0.73       0.625       0.682       0.488


yolov7-tiny logs:
Logging results to runs/train/yolov7-tiny_new
Starting training for 1 epochs...

     Epoch   gpu_mem       box       obj       cls     total    labels  img_size
       0/0     3.05G   0.03117   0.04046   0.01683   0.08845       191       640: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 4929/4929 [1:06:26<00:00,  1.24it/s]
               Class      Images      Labels           P           R      mAP@.5  mAP@.5:.95:   0%|                                                                                                                                                                                                     | 0/105 [00:00<?, ?it/s]/home/ramesh/miniconda3/envs/automl/lib/python3.10/site-packages/torch/functional.py:504: UserWarning: torch.meshgrid: in an upcoming release, it will be required to pass the indexing argument. (Triggered internally at ../aten/src/ATen/native/TensorShape.cpp:3190.)
  return _VF.meshgrid(tensors, **kwargs)  # type: ignore[attr-defined]
               Class      Images      Labels           P           R      mAP@.5  mAP@.5:.95: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 105/105 [00:57<00:00,  1.81it/s]
                 all        5000       36335       0.627       0.525       0.546       0.356
1 epochs completed in 1.124 hours.

Fusing layers... 
IDetect.fuse
Model Summary: 208 layers, 6221370 parameters, 0 gradients
               Class      Images      Labels           P           R      mAP@.5  mAP@.5:.95: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 105/105 [00:42<00:00,  2.45it/s]
                 all        5000       36335       0.625       0.514       0.539       0.352
