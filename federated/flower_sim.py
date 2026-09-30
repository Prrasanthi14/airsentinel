"""Federated learning simulation: city clients train AQI models locally and share only weights (Flower)."""
import flwr as fl
import numpy as np

CITIES = ["delhi", "ludhiana", "lucknow"]


def make_local_data(seed: int, n: int = 500):
    """Synthetic per-city features: wind speed, humidity, upwind fire count -> next-day PM2.5."""
    rng = np.random.default_rng(seed)
    X = rng.uniform([0, 20, 0], [15, 95, 300], size=(n, 3))
    y = 80 - 4 * X[:, 0] + 0.8 * X[:, 1] + 0.6 * X[:, 2] + rng.normal(0, 15, n)
    return X, y


class CityClient(fl.client.NumPyClient):
    def __init__(self, cid: int):
        self.X, self.y = make_local_data(cid)
        self.w = np.zeros(self.X.shape[1] + 1)

    def _xb(self):
        return np.hstack([self.X, np.ones((len(self.X), 1))])

    def get_parameters(self, config):
        return [self.w]

    def fit(self, parameters, config):
        self.w = parameters[0]
        Xb = self._xb()
        for _ in range(50):  # local gradient descent on raw data that never leaves the city
            grad = Xb.T @ (Xb @ self.w - self.y) / len(self.y)
            self.w -= 1e-5 * grad
        return [self.w], len(self.y), {}

    def evaluate(self, parameters, config):
        mse = float(np.mean((self._xb() @ parameters[0] - self.y) ** 2))
        return mse, len(self.y), {"mse": mse}


def client_fn(context):
    cid = int(context.node_config["partition-id"])
    return CityClient(cid).to_client()


if __name__ == "__main__":
    fl.simulation.run_simulation(
        server_app=fl.server.ServerApp(
            config=fl.server.ServerConfig(num_rounds=5),
            strategy=fl.server.strategy.FedAvg(),
        ),
        client_app=fl.client.ClientApp(client_fn=client_fn),
        num_supernodes=len(CITIES),
    )
