# Resonanceverse シミュレーション実装レポート

**更新日:** 2026年5月3日  
**位置づけ:** 構成的例示・診断用シミュレーション群  
**GitHubリポジトリ:** https://github.com/zyx-corporation/resonanceverse_sim.git

---

## 0. 解釈上の前提

本リポジトリは Resonanceverse 理論を証明するものではない。明示的に定義された力学系において、提案条件がどのように振る舞うかを、再現可能な形で例示・診断するためのシミュレーション群である。

したがって、本レポート中の数値結果は、理論命題の決定的検証ではなく、特定のモデル化条件・パラメータ設定の下で得られた構成的結果として解釈する。

---

## 1. 実装全体概要

| Phase | 実装状況 | 主な目的 | 論文対応 | 解釈 |
|-------|---------|----------|----------|------|
| **Phase 1** | 実装済み | 2-agent illustrative dynamics | Section 2.4 | 有界な非ゼロ差異を保つ相対力学の例示 |
| **Phase 2** | 実装済み | Multi-agent constraint illustration | Section 3 | 制約バイアスが分散低下へ与える影響の例示 |
| **Phase 3** | 実装済み | Resonance-condition diagnostic run | Section 4 | CM・CU・CV 条件と Lyapunov-like 指標の診断 |
| **Phase 4** | 実装済み | Prototype falsifiability diagnostics | Appendix D | 反証可能性を志向した診断プロトコルの雛形 |

---

## 2. Phase別結果

### Phase 1: 2-agent illustrative dynamics

```
‖ΔM(0)‖         : 1.1180
lim_sup ‖ΔM‖    : 0.1009
lim_inf ‖ΔM‖    : 0.0995
後半平均 ‖ΔM‖   : 0.1001 ± 0.0003
後半 d/dt 最大   : 0.0543
```

**解釈:**

この結果は、非収束公理そのものを証明するものではない。明示的に定義した二主体相対力学において、差異がゼロへ崩壊せず、かつ小さな有界帯域に保たれうることを示す構成例である。

論文での位置づけは、`bounded non-convergent regime` の構成的例示である。

---

### Phase 2: Multi-agent constraint illustration

#### Scenario A: 制約なし自由相互作用

```
最終 VarE      : 0.0000
Consensus 条件 : satisfied in this configuration
```

#### Scenario B: 制約バイアスあり（θ_M = 0.2）

```
最終 VarE      : 0.0000
Consensus 条件 : satisfied in this configuration
到達時刻       : Scenario A より短縮
```

#### Scenario C: 外乱注入（t=50で2倍摂動）

```
最終 VarE      : 0.0000
Consensus 条件 : satisfied after recovery in this configuration
```

**解釈:**

Scenario B は、制度的制約一般の有効性を証明するものではない。ここで実装されているのは、`VarE > θ_M` の場合に centroid-attraction 型の制約バイアスを与えるモデルであり、そのバイアスが分散低下を速めうることを例示している。

したがって、この結果は「制度が一般に有効である」ことの経験的証明ではなく、「特定の制度的制約モデルが ΔM 分布へ与える効果」の構成的例示である。

---

### Phase 3: Resonance-condition diagnostic run

#### 条件成立率

```
Resonance 条件成立率 : 98.6%
CM 単独成立率        : 99.5%
CU 単独成立率        : 98.6%
CV 単独成立率        : 100.0%
```

#### 非ゼロ差異と Lyapunov-like 指標

```
lim_sup ‖ΔM‖          : 0.1010
Lyapunov-like 減少率  : 57.8%
mean dV/dt            : -0.0426
```

#### 定常状態での各指標値

```
VarE（CM指標）   : 0.0003   (θ_M = 0.2)
rangeU（CU指標） : 0.0000   (θ_U = 0.3)
VarCV（CV指標）  : 0.0013   (θ_V = 0.1)
```

#### CM・CU・CV の相関診断

```
corr(CM, CU) = 0.525
corr(CM, CV) = 0.609
corr(CU, CV) = 0.215
最大相関     = 0.609
```

**解釈:**

これらの結果は、Lyapunov 安定性の完全証明ではない。`57.8%` の減少率は、対象軌道上での Lyapunov-like 指標の診断的傾向を示すものであり、古典的な意味での負定性や大域安定性を示すものではない。

また、CM・CU・CV の相関は、同一ネットワーク・同一軌道上では構造的結合を持ちうる。これは、定義上の独立性と、動力学上の相関が区別されるべきことを示す診断結果である。

---

### Phase 4: Prototype falsifiability diagnostics

#### Protocol 1: モデル固有の収束挙動診断

```
試行数（総計）   : 300回（100試行 × 3ドメイン）
ドメイン          : legal, scientific, creative

legal       : 収束率 0%
scientific  : 収束率 0%
creative    : 収束率 0%
```

**解釈:**

この結果は、非収束性公理を外部的に検証するものではない。反発項を含む明示的な相互作用関数の下で、指定されたパラメータ範囲において ΔM がゼロへ崩壊しなかったことを示す、モデル固有のストレステストである。

より厳密な収束判定には、最終値だけでなく、tail mean、tail variance、limsup/liminf 近似、tail trend、epsilon 以下滞在時間などを併用する必要がある。

#### Protocol 3: CM・CU・CV 相関診断

```
サンプル数      : 500個のランダム状態
エージェント数  : 各5エージェント
方法            : Pearson 相関係数

corr(CM, CU) = -0.001
corr(CM, CV) = 0.022
corr(CU, CV) = -0.011
最大相関     = 0.022
```

**解釈:**

ランダム状態サンプリングでは、CM・CU・CV の相関が非常に小さい。これは、Phase 3 の同一軌道上で観測される相関が、定義そのものから生じたものではなく、ネットワーク構造および動力学に由来する可能性を示す。

ただし、これは統計的独立性の完全証明ではなく、指定されたサンプリング条件下での診断結果である。

---

## 3. 実装から得られた設計上の示唆

### 3.1 U dynamics の符号規約

実装上、不確実性 $U$ の更新符号は重要である。相互作用により不確実性差を縮小する設計にしなければ、CU 条件は達成しにくい。

```python
# コンセンサス方向の例
delta_U = U_j - U_i
dU_i += gamma_U * alpha * delta_U
```

この点は、理論の証明ではなく、モデル設計上の注意点である。

### 3.2 CM-CV 相関の二層構造

Phase 3 と Phase 4 の対比から、次の二層性が示唆される。

```
同一ネットワーク・同一軌道上  : 相関 = 0.609
ランダム状態サンプリング      : 相関 = 0.022
```

これは、CM・CV が定義上は分離可能であっても、特定の動力学上では構造的に結合しうることを示す。

### 3.3 V 自律ダイナミクスの役割

Phase 3 では、各エージェントに固有の価値目標を与え、M 動態とは部分的に独立した V の変化を導入している。

```python
V_target_i = normalize(random_vector())
dVs[i] += gamma_V_return * (V_targets[i] - a.V)
```

この設計により、M 空間では差異が縮小する一方、V 空間では一定の自律性が保持される。この非対称性が、共鳴条件の非自明性を生む。

---

## 4. リポジトリの状態

```
core/          - Agent, Dynamics, Network, Resonance
analysis/      - 指標計算・Lyapunov-like diagnostics
visualization/ - Figure生成
experiments/   - Phase別実験スクリプト
config/        - scenarios.yaml
outputs/       - 図・ログ・LaTeX論文ファイル
```

### コード品質上の特徴

- 再現性: シード固定により再現可能な実行を意図している。
- 可読性: モジュール分割と型ヒントを用いている。
- 拡張性: 各 Phase を独立に実行できる。
- 限界: 現状の結果は特定パラメータ設定に依存するため、理論全体の一般性を示すものではない。

---

## 5. 今後の改善候補

1. `final_norm` だけでなく、tail window 統計を用いた収束・非収束診断を追加する。
2. Phase 2 の制度モデルを centroid-attraction 以外にも拡張する。
3. Phase 3 の Lyapunov-like 指標を、明確な仮定付きの診断量として再定義する。
4. Phase 4 を「公理支持」ではなく、モデル固有の反証可能性探索として拡張する。
5. `docs/IMPLEMENTATION_NOTES.md`、`examples/quickstart.py`、`CITATION.bib` を追加する。

---

## 6. 総括

本実装は、Resonanceverse 理論の決定的証明ではない。一方で、明示的な力学系の下で、有界な非収束差異、制度的制約モデル、共鳴条件診断、反証可能性プロトコルの雛形を再現可能に示す点に価値がある。

論文本文と同様、本リポジトリのシミュレーションは `constructive illustrations` として扱うのが適切である。

---

**報告日:** 2026年5月3日  
**監督:** Tomoyuki Kano（加納智之）
