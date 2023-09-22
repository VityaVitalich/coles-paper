PYTHONPATH=../.. LUIGI_CONFIG_PATH=conf/luigi.cfg python -m embeddings_validation \
    --conf conf/embeddings_validation_baselines_unsupervised.hocon --workers 10 --total_cpu_count 20
