"""
エージェントネットワーク管理（Section 3）

隣接行列の生成・ΔMネットワーク構造行列 X(t) の計算を担う。
"""
import numpy as np
import networkx as nx
from .agent import Agent


class AgentNetwork:
    """エージェントのグラフ構造を管理するラッパー"""

    def __init__(self, agents: list[Agent], G: nx.Graph = None):
        self.agents = agents
        self.n = len(agents)
        if G is None:
            G = nx.complete_graph(self.n)
        self.G = G
        self._adj = nx.to_numpy_array(G)

    @property
    def adj(self) -> np.ndarray:
        return self._adj

    @property
    def edges(self) -> list[tuple[int, int]]:
        return list(self.G.edges())

    def delta_M_matrix(self) -> np.ndarray:
        """
        ΔM構造行列 X[i,j] = ‖M_j - M_i‖ （i≠j）
        対角成分は 0。
        """
        Ms = np.stack([a.M for a in self.agents])
        norms = np.linalg.norm(
            Ms[:, None, :] - Ms[None, :, :], axis=-1
        )
        return norms

    def edge_delta_norms(self) -> np.ndarray:
        """エッジ上の ‖ΔM‖ を配列で返す"""
        return np.array([
            np.linalg.norm(self.agents[j].M - self.agents[i].M)
            for (i, j) in self.edges
        ])

    def perturb_agent(self, idx: int, delta: np.ndarray):
        """エージェント idx の意味状態を外乱 delta だけずらす"""
        self.agents[idx].M = self.agents[idx].M + delta
        self.agents[idx].M_history[-1] = self.agents[idx].M.copy()


# --------- ファクトリ ---------

def make_complete_network(agents: list[Agent]) -> AgentNetwork:
    G = nx.complete_graph(len(agents))
    return AgentNetwork(agents, G)


def make_small_world_network(
    agents: list[Agent],
    k: int = 4,
    p_rewire: float = 0.1,
    seed: int = 42,
) -> AgentNetwork:
    G = nx.watts_strogatz_graph(len(agents), k, p_rewire, seed=seed)
    return AgentNetwork(agents, G)


def make_random_network(
    agents: list[Agent],
    p: float = 0.3,
    seed: int = 42,
) -> AgentNetwork:
    G = nx.erdos_renyi_graph(len(agents), p, seed=seed)
    return AgentNetwork(agents, G)
