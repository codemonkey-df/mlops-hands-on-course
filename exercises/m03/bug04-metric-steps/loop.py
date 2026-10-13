"""A training loop that logs one loss value per epoch."""

import math

import mlflow


def train_loop(epochs: int) -> None:
    """Pretend to train and log the loss curve."""
    for epoch in range(epochs):
        loss = math.exp(-epoch / 3)
        mlflow.log_metric("train_loss", loss)
