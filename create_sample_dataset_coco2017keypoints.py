import json

# Load your COCO annotation JSON
with open('/home/ubuntu/tfds_datasets/coco_keypoints_2017/annotations/coco_test.json', 'r') as f:  # _train, _test
    coco = json.load(f)

# Output file path
output_txt = '/home/ubuntu/tfds_datasets/coco_keypoints_2017/annotations/test2017.txt'  # train, test

# Mapping from original folder prefix to new prefix
prefix_map = {
    'train': 'train2017',
    'val': 'train2017',
    'test': 'val2017'
}

with open(output_txt, 'w') as out_file:
    for img in coco['images']:
        filename = img['file_name']  # e.g., 'train/000000061960.jpg'

        # Split into prefix and filename parts
        parts = filename.split('/')
        if len(parts) == 2:
            prefix, file = parts
            new_prefix = prefix_map.get(prefix, prefix)  # default to original if not mapped
            new_path = f'./images/{new_prefix}/{file}'
            out_file.write(new_path + '\n')
        else:
            # If format unexpected, just write as is or handle accordingly
            out_file.write(f'./images/{filename}\n')

print(f'Done! Wrote filenames to {output_txt}')

# cp /home/ubuntu/tfds_datasets/coco_keypoints_2017/annotations/train2017.txt /opt/dlami/nvme/pose/coco/train2017.txt
# cp /home/ubuntu/tfds_datasets/coco_keypoints_2017/annotations/test2017.txt /opt/dlami/nvme/pose/coco/val2017.txt