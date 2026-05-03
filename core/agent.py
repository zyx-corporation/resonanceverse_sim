"""エージェント状態の定義（Section 2-4の状態空間）"""
from dataclasses import dataclass, field
import numpy as np


@dataclass
class Agent:
    """
    Resonanceverse エージェント。
    意味状態 M, 不確実性 U, 価値ベクトル V を保持する。
    """
    id: int
    M: np.ndarray          # 意味状態 (d次元)
    U: float = 0.5         # 不確実性 [0, 1]
    V: np.ndarray = None   # 価値ベクトル (dv次元)

    # 軌道履歴（解析用）
    M_history: list = field(default_factory=list, repr=False)
    U_history: list = field(default_factory=list, repr=False)
    V_history: list = field(default_factory=list, repr=False)

    def __post_init__(self):
        self.M = np.asarray(self.M, dtype=float)
        if self.V is None:
            self.V = np.ones(len(self.M)) / len(self.M)
        else:
            self.V = np.asarray(self.V, dtype=float)
        self.record()

    def record(self):
        """現在の状態を履歴に追加"""
        self.M_history.append(self.M.copy())
        self.U_history.append(float(self.U))
        self.V_history.append(self.V.copy())

    def update(self, dM: np.ndarray, dU: float, dV: np.ndarray, dt: float):
        """オイラー法で状態を更新し履歴に記録"""
        self.M = self.M + dM * dt
        self.U = float(np.clip(self.U + dU * dt, 0.0, 1.0))
        self.V = self.V + dV * dt
        self.record()

    @property
    def dim(self) -> int:
        return len(self.M)


def make_agents(
    n: int,
    d: int = 2,
    dv: int = 2,
    init: str = "random",
    seed: int = 42,
    clusters: int = 1,
) -> list[Agent]:
    """
    n エージェントを生成する。

    Parameters
    ----------
    init : "random" | "clustered" | "uniform"
    clusters : クラスタ数（init="clustered" のみ有効）
    """
    rng = np.random.default_rng(seed)

    if init == "random":
        Ms = rng.uniform(-1, 1, (n, d))
        Us = rng.uniform(0.2, 0.8, n)
        Vs = rng.uniform(0, 1, (n, dv))
        Vs = Vs / np.linalg.norm(Vs, axis=1, keepdims=True)

    elif init == "clustered":
        centers = rng.uniform(-1.5, 1.5, (clusters, d))
        labels = rng.integers(0, clusters, n)
        Ms = centers[labels] + rng.normal(0, 0.15, (n, d))
        Us = rng.uniform(0.2, 0.8, n)
        Vs_centers = rng.uniform(0, 1, (clusters, dv))
        Vs_centers /= np.linalg.norm(Vs_centers, axis=1, keepdims=True)
        Vs = Vs_centers[labels] + rng.normal(0, 0.05, (n, dv))
        Vs = Vs / np.linalg.norm(Vs, axis=1, keepdims=True)

    elif init == "uniform":
        Ms = np.linspace(-1, 1, n * d).reshape(n, d)
        Us = np.full(n, 0.5)
        Vs = np.ones((n, dv)) / dv

    else:
        raise ValueError(f"Unknown init: {init}")

    return [Agent(id=i, M=Ms[i], U=Us[i], V=Vs[i]) for i in range(n)]
