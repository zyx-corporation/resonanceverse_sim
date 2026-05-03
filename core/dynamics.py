"""
相互作用関数と状態更新ダイナミクス（Section 2-3）

interaction_f : 意味差 ΔM に対する非線形相互作用
  - 近距離（‖ΔM‖ < r_rep）: 反発（差異の維持）
  - 遠距離（‖ΔM‖ > r_rep）: 引力（過剰分散の抑制）
"""
import numpy as np
from .agent import Agent


def interaction_f(
    alpha: float,
    delta_M: np.ndarray,
    r_rep: float = 0.1,
    c_rep: float = 0.5,
    c_att: float = 0.3,
) -> np.ndarray:
    """
    非線形相互作用 f(α, ΔM)。

    Parameters
    ----------
    alpha  : 文脈親和性 α_{ij}(t)
    delta_M: ΔM = M_j - M_i
    r_rep  : 反発半径（近距離閾値）
    c_rep  : 反発係数
    c_att  : 引力係数
    """
    norm = np.linalg.norm(delta_M)
    if norm < 1e-12:
        return np.zeros_like(delta_M)
    if norm < r_rep:
        return -c_rep * alpha * delta_M
    else:
        return c_att * alpha * delta_M


def interaction_g(
    alpha: float,
    delta_U: float,
    gamma_U: float = 0.1,
) -> float:
    """
    不確実性の相互作用 g(α, ΔU)。
    近隣との相互作用で不確実性レベルが収束（コンセンサス）する。
    delta_U = U_j - U_i: 正なら i の U が増加方向（引力）
    """
    return gamma_U * alpha * delta_U


def alpha_periodic(t: float, base: float = 0.7, amp: float = 0.2, freq: float = 0.1) -> float:
    """時間変動する文脈親和性 α(t) = base + amp * sin(freq * t)"""
    return base + amp * np.sin(freq * t)


def alpha_constant(t: float, value: float = 0.7) -> float:
    """定数の文脈親和性"""
    return value


def compute_agent_derivatives(
    agents: list[Agent],
    adj: np.ndarray,
    t: float,
    alpha_func=None,
    gamma_U: float = 0.05,
    gamma_V: float = 0.1,
    r_rep: float = 0.1,
    c_rep: float = 0.5,
    c_att: float = 0.3,
) -> tuple[list[np.ndarray], list[float], list[np.ndarray]]:
    """
    全エージェントの微分 (dM, dU, dV) を一括計算。

    Parameters
    ----------
    adj       : 隣接行列 adj[i,j] = 1 iff (i→j) エッジあり
    alpha_func: alpha_func(t, i, j) -> float （デフォルト: 定数0.7）
    """
    if alpha_func is None:
        alpha_func = lambda t, i, j: 0.7  # noqa: E731

    n = len(agents)
    dMs = [np.zeros(agents[i].dim) for i in range(n)]
    dUs = [0.0] * n
    dVs = [np.zeros(len(agents[i].V)) for i in range(n)]

    for i in range(n):
        for j in range(n):
            if i == j or adj[i, j] == 0:
                continue
            alpha = alpha_func(t, i, j)
            delta_M = agents[j].M - agents[i].M
            delta_U = agents[j].U - agents[i].U
            delta_V = agents[j].V - agents[i].V

            dMs[i] += interaction_f(alpha, delta_M, r_rep, c_rep, c_att)
            dUs[i] += interaction_g(alpha, delta_U, gamma_U)
            # V は線形引力 + 固有の非線形ドリフト（CM との構造的従属を回避）
            dVs[i] += gamma_V * alpha * delta_V

        # 孤立ペナルティ: 隣接なしなら不確実性上昇
        if adj[i].sum() == 0:
            dUs[i] += 0.05

    return dMs, dUs, dVs
