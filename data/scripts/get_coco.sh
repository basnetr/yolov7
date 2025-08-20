#!/bin/bash
# COCO 2017 dataset http://cocodataset.org
# Download command: bash data/scripts/get_coco.sh
# Train command: python train.py --data coco.yaml
# Default dataset location is next to YOLOv5:
#   /parent_folder
#     /coco
#     /yolov5

# bash /home/ubuntu/yolov7_pytorch_pose/yolov7/data/scripts/get_coco.sh
mkdir -p /opt/dlami/nvme/pose/coco/images

cd /opt/dlami/nvme/pose/

# Download/unzip labels
d='/opt/dlami/nvme/pose/coco' # unzip directory
# url=https://github.com/ultralytics/yolov5/releases/download/v1.0/
url=https://github.com/WongKinYiu/yolov7/releases/download/v0.1/
f='coco2017labels-keypoints.zip' # 'coco2017labels.zip' # or 'coco2017labels-segments.zip', 68 MB
echo 'Downloading' $url$f ' ...'
curl -L $url$f -o $f && unzip -q $f -d $d && rm $f & # download, unzip, remove in background

# Download/unzip images
d='/opt/dlami/nvme/pose/coco/images' # unzip directory
url=http://images.cocodataset.org/zips/
f1='train2017.zip' # 19G, 118k images
f2='val2017.zip'   # 1G, 5k images
# f3='test2017.zip'  # 7G, 41k images (optional)
for f in $f1 $f2; do
  echo 'Downloading' $url$f '...'
  curl -L $url$f -o $f && unzip -q $f -d $d && rm $f & # download, unzip, remove in background
done
wait # finish background tasks

# ---------------- uncomment below if you want to train on a sample of the dataset ---------------
# # rename keypoints labels and files - remove suffix if you want to use full dataset
# mv /opt/dlami/nvme/pose/coco/train2017.txt /opt/dlami/nvme/pose/coco/train2017.txt_full_dataset_keypoints
# mv /opt/dlami/nvme/pose/coco/val2017.txt /opt/dlami/nvme/pose/coco/val2017.txt_full_dataset_keypoints

# # comment this if you want to use full dataset
# # prepare small sample dataset
# cp /home/ubuntu/automltraining/yolov7/data/train2017.txt /opt/dlami/nvme/pose/coco/train2017.txt
# cp /home/ubuntu/automltraining/yolov7/data/test2017.txt /opt/dlami/nvme/pose/coco/val2017.txt