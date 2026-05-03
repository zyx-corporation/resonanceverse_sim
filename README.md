# Resonanceverse Simulation Suite

Resonanceverse 理論（意味的共鳴の数理モデル）に関連する、再現可能な数値シミュレーション群です。

本リポジトリは Resonanceverse 理論を証明するものではありません。明示的に定義された力学系において、提案条件がどのように振る舞うかを再現可能な形で例示・診断するためのシミュレーション群です。

This repository does not prove the Resonanceverse theory. It provides reproducible illustrative simulations for explicitly specified dynamics that satisfy or probe selected Resonanceverse-inspired conditions.

## 対応論文

**意味の非収束と共鳴条件――誤配に基づく Resonanceverse の基礎理論**
https://doi.org/10.5281/zenodo.19972880

## 構成

```
resonanceverse_sim/
├── core/              # コアモジュール（エージェント・ダイナミクス・共鳴判定）
├── experiments/       # 各フェーズの実験スクリプト
├── analysis/          # 指標計算・Lyapunov-like diagnostics
├── visualization/     # 可視化モジュール
├── config/            # 実験パラメータ設定
└── outputs/           # 生成図・ログ・論文LaTeXの出力先
```

## フェーズ概要

| Phase | 目的 | 論文対応 |
|-------|------|----------|
| 1 | 2-agent illustrative dynamics | Section 2.4 Toy Example |
| 2 | Multi-agent constraint illustration | Section 3 |
| 3 | Resonance-condition diagnostic run | Section 4 |
| 4 | Prototype falsifiability diagnostics | Appendix D |

## 使い方

```bash
pip install -r requirements.txt

# Phase 1: 2-agent illustrative dynamics
python -m experiments.phase1_basic

# Phase 2: Multi-agent constraint illustration
python -m experiments.phase2_multi

# Phase 3: Resonance-condition diagnostic run
python -m experiments.phase3_resonance

# Phase 4: Prototype falsifiability diagnostics
python -m experiments.phase4_falsify
```

出力図は `outputs/phaseN/` に保存されます。

## 解釈上の注意

各 Phase の結果は、理論命題の決定的証明ではなく、特定のモデル化条件・パラメータ設定の下で得られる構成的例示です。

- Phase 1 は、非収束公理そのものの証明ではなく、有界な非ゼロ差異が維持されうる相対力学の例を示します。
- Phase 2 は、制度的制約一般の有効性の証明ではなく、centroid-attraction 型の制約バイアスが分散低下に与える影響を例示します。
- Phase 3 は、Lyapunov 安定性の完全証明ではなく、Resonance 条件と Lyapunov-like 指標の診断的挙動を示します。
- Phase 4 は、非収束公理の外部的検証ではなく、反証可能性を志向した診断プロトコルのプロトタイプです。

論文本文では、これらの結果を `constructive illustrations` として扱っています。
