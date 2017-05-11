# Distributed TensorFlow

```sh
gcloud ml-engine local train --module-name trainer.task \
  --package-path trainer \
  --distributed \
  --parameter-server-count 1 \
  --worker-count 1 \
  -- \
  --model-dir mnist_model
```
