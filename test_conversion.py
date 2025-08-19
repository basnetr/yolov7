import torch
from models.yolo import Detect, Model
from models.common import Conv

weights = "/home/ubuntu/yolov7_pytorch_pose/run_outputs/train/yolov7-w6-pose_experiment3/weights/best.pt"
ckpt = torch.load(weights, map_location="cpu")

class Ensemble(torch.nn.ModuleList):
    # Ensemble of models
    def __init__(self):
        super(Ensemble, self).__init__()

    def forward(self, x, augment=False):
        y = []
        for module in self:
            y.append(module(x, augment)[0])
        # y = torch.stack(y).max(0)[0]  # max ensemble
        # y = torch.stack(y).mean(0)  # mean ensemble
        y = torch.cat(y, 1)  # nms ensemble
        return y, None  # inference, train output

model = Ensemble()
model.append(ckpt['ema' if ckpt.get('ema') else 'model'].float().fuse().eval())  # FP32 model

# Compatibility updates
inplace = True
for m in model.modules():
    if type(m) in [torch.nn.Hardswish, torch.nn.LeakyReLU, torch.nn.ReLU, torch.nn.ReLU6, torch.nn.SiLU, Detect, Model]:
        m.inplace = inplace  # pytorch 1.7.0 compatibility
    elif type(m) is Conv:
        m._non_persistent_buffers_set = set()  # pytorch 1.6.0 compatibility
        
model = model[-1]
pass