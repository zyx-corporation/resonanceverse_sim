# Resonanceverse Simulation Suite

Resonanceverse 理論（意味的共鳴の数理モデル）の数値シミュレーション実装。

## 構成

```
resonanceverse_sim/
├── core/              # コアモジュール（エージェント・ダイナミクス・共鳴判定）
├── experiments/       # 各フェーズの実験スクリプト
├── analysis/          # 指標計算・Lyapunov解析
├── visualization/     # 可視化モジュール
├── config/            # 実験パラメータ設定
└── outputs/           # 生成図・ログの出力先
```

## フェーズ概要

| Phase | 目的 | 論文対応 |
|-------|------|----------|
| 1 | 2-agent基礎検証・Lemma 2.1の実証 | Section 2.4 Toy Example |
| 2 | Multi-agent Consensus・制度的制約 | Section 3 |
| 3 | 共鳴条件 CM∧CU∧CV・Lyapunov検証 | Section 4 |
| 4 | Falsifiability Protocol実証 | Appendix D |

## 使い方

```bash
pip install -r requirements.txt

# Phase 1: 2-agent基礎検証
python -m experiments.phase1_basic

# Phase 2: Multi-agent Consensus
python -m experiments.phase2_multi

# Phase 3: 共鳴条件
python -m experiments.phase3_resonance

# Phase 4: Falsifiability Protocol
python -m experiments.phase4_falsify
```

出力図は `outputs/phaseN/` に保存されます。
