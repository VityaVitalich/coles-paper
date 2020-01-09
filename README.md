# Setup

```sh
# download Miniconda from https://conda.io/
curl -OL https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
# execute intall file
bash Miniconda*.sh
# relogin to apply PATH changes
exit

# install pytorch
conda install pytorch -c pytorch
# check CUDA version
python -c 'import torch; print(torch.version.cuda)'
# chech torch GPU
# See question: https://stackoverflow.com/questions/48152674/how-to-check-if-pytorch-is-using-the-gpu
python -c 'import torch; print(torch.rand(2,3).cuda())'

# clone repo
git clone git@bitbucket.org:dllllb/dltranz.git

# install dependencies
cd dltranz
pip install -r requirements.txt

# download datasets
./get-data.sh

# convert datasets from transaction list to features for metric learning
./make-datasets.sh
```

# Run scenario

## Train metric learning model

Run this script for every project: age-pred, tinkoff, gender.
Provide valid dataset description in hocon file and model params in json file

```sh
python metric_learning.py --conf conf/sber_ml_dataset.hocon conf/sber_ml_params_train.json
python metric_learning.py --conf conf/tinkoff_dataset.hocon conf/tinkoff_train_params.json
```

## With pretrained mertic learning model run inference ang take embeddings for each customer

Run this script for every project: age-pred, tinkoff, gender.
Provide valid dataset description in hocon file and model inference params in json file

```sh
python ml_inference.py --conf conf/dataset.hocon conf/ml_params_inference.json
```

## Use embeddings for each customer as a features for specific machine learning problem

See code in notebooks in `notebooks/`.