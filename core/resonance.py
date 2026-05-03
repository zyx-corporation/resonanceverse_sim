"""
共鳴条件の判定（Section 4）

CM : 意味整合性条件  — VarE(ΔM) < θ_M
CU : 不確実性共有条件 — max(U) - min(U) < θ_U
CV : 価値方向整合性条件 — Var(cos_sim) < θ_V
Resonance = CM ∧ CU ∧ CV
"""
import numpy as np
from .agent import Agent


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def check_CM(
    agents: list[Agent],
    edges: list[tuple[int, int]],
    theta_M: float = 0.2,
) -> tuple[bool, float]:
    """
    意味整合性条件 CM。
    Returns (satisfied, VarE_value)
    """
    if not edges:
        return True, 0.0
    norms = np.array([
        np.linalg.norm(agents[j].M - agents[i].M)
        for (i, j) in edges
    ])
    var_e = float(np.var(norms))
    return var_e < theta_M, var_e


def check_CU(
    agents: list[Agent],
    theta_U: float = 0.3,
) -> tuple[bool, float]:
    """
    不確実性共有条件 CU。
    Returns (satisfied, range_U)
    """
    U_vals = np.array([a.U for a in agents])
    range_U = float(np.max(U_vals) - np.min(U_vals))
    return range_U < theta_U, range_U


def check_CV(
    agents: list[Agent],
    edges: list[tuple[int, int]],
    theta_V: float = 0.1,
) -> tuple[bool, float]:
    """
    価値方向整合性条件 CV。
    Returns (satisfied, Var(cos_sim))
    """
    if not edges:
        return True, 0.0
    cos_sims = np.array([
        _cosine_similarity(agents[i].V, agents[j].V)
        for (i, j) in edges
    ])
    var_cv = float(np.var(cos_sims))
    return var_cv < theta_V, var_cv


def check_resonance(
    agents: list[Agent],
    edges: list[tuple[int, int]],
    theta_M: float = 0.2,
    theta_U: float = 0.3,
    theta_V: float = 0.1,
) -> dict:
    """
    三条件を一括チェックし結果を辞書で返す。

    Returns
    -------
    {
      "CM": bool, "VarE": float,
      "CU": bool, "rangeU": float,
      "CV": bool, "VarCV": float,
      "resonance": bool,
    }
    """
    cm, var_e  = check_CM(agents, edges, theta_M)
    cu, range_u = check_CU(agents, theta_U)
    cv, var_cv  = check_CV(agents, edges, theta_V)
    return {
        "CM": cm, "VarE": var_e,
        "CU": cu, "rangeU": range_u,
        "CV": cv, "VarCV": var_cv,
        "resonance": cm and cu and cv,
    }
