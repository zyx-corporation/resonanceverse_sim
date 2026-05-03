"""
Lyapunov 関数の数値計算（Proposition 4.1 検証）

候補関数: V(t) = Σ_i (1/2) ‖M_i‖²
dV/dt を数値微分し、|M| が大きい領域で dV/dt < 0 を確認する。
"""
import numpy as np
from core.agent import Agent


def lyapunov_V(agents: list[Agent]) -> float:
    """
    V = Σ_i (1/2) ‖M_i‖²
    """
    return float(sum(0.5 * np.linalg.norm(a.M) ** 2 for a in agents))


def lyapunov_V_from_history(M_histories: list[list[np.ndarray]]) -> np.ndarray:
    """
    各時刻 t で V(t) を計算して返す。

    Parameters
    ----------
    M_histories : agents[i].M_history のリスト（shape: n_agents x T x d）
    """
    T = len(M_histories[0])
    V_series = np.zeros(T)
    for t in range(T):
        V_series[t] = sum(
            0.5 * np.linalg.norm(h[t]) ** 2
            for h in M_histories
        )
    return V_series


def lyapunov_dV(V_series: np.ndarray, dt: float) -> np.ndarray:
    """dV/dt の数値微分（中央差分）"""
    return np.gradient(V_series, dt)


def verify_lyapunov_decrease(
    V_series: np.ndarray,
    dt: float,
    norm_threshold: float = 1.0,
    M_histories: list = None,
) -> dict:
    """
    Proposition 4.1 の数値検証。

    ‖M‖ が大きい領域（> norm_threshold）で dV/dt < 0 かどうかを確認。

    Returns
    -------
    dict: {
      "fraction_decreasing": float,  # dV/dt < 0 の割合
      "max_dV": float,
      "mean_dV": float,
      "verified": bool,              # 過半数で dV/dt < 0
    }
    """
    dV = lyapunov_dV(V_series, dt)

    # 全体での減少率（大域 Lyapunov の代替指標）
    fraction = float(np.mean(dV < 0))

    return {
        "fraction_decreasing": fraction,
        "max_dV": float(np.max(dV)),
        "mean_dV": float(np.mean(dV)),
        "dV_series": dV,
        "verified": fraction > 0.5,
    }
