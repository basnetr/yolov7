Recommendation from official repo:
Tested with: Python 3.7.13, Pytorch 1.12.0+cu113

Python 3.7 had issues with imports such as:
ImportError: cannot import name 'Literal' from 'typing' 
This was due to old typing version fixed by upgrading python to 3.8

Environment Setup:
conda create -n pose python=3.8
conda activate pose
python -m pip install torch==1.12.1+cu113 torchvision==0.13.1+cu113 torchaudio==0.12.1 --extra-index-url https://download.pytorch.org/whl/cu113
python -m pip install -r requirements.txt