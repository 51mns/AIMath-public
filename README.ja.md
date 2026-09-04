# AIMath Public

AIMathの**履歴を引き継がない公開研究リポジトリ**で、再現可能なAI支援数学研究・失敗経路の記録・独立査読・マルチエージェントVillageを扱います。private正本のGit履歴・生チャット・メール・個人情報はmirrorしません。

公開snapshotのprivate canonical source: `c8e61e0e398f540bc8c5de79663398d689f37473`

**ライセンス:** このrepoは単一ライセンスではなくpath-based multi-licenseです。[`LICENSE`](LICENSE)、[`LICENSING.md`](LICENSING.md)、`REUSE.toml`を参照してください。

## まず数学の成果を見る

### 注目成果 — Gyoda Conjecture 7.6

公開`gyoda-89` packageでは、Gyoda Conjecture 7.6の**number-onlyで書かれた形**に対して、次の衝突を`INDEPENDENTLY_REPRODUCED`として保存しています。

```text
(k1,k2,k3) = (0,0,6)
sigma = (3,1,2)
labels = 1/5 and 2/3
n_(1/5) = n_(2/3) = 89
```

さらにexactな無限衝突classとして

```text
m ≡ 5, 14, 15, 24 (mod 30)
```

を記録しています。

再現は次の1コマンドです。

```bash
python3 research/gyoda-89/reproduce.py
```

境界も明示しています。project record上の著者確認は`89`衝突と`m ≡ 5 (mod 30)` familyまでで、`14,15,24`はAIMath側の拡張です。またposition labelを含む、より強い修正版まで反証したとは主張しません。

他の成果は[`docs/RESULTS.md`](docs/RESULTS.md)、失敗・bounded no-go・inconclusive・refuted routeは[`docs/FAILED_ROUTES.md`](docs/FAILED_ROUTES.md)にあります。AIMathでは失敗経路も正式な研究成果物として残します。

## AIMathが試していること

AIMathは「AIに数学を解かせる」だけでなく、**AI数学研究を誇張せず、再現・反証・査読できる形で運用できるか**を試しています。

基本の流れは、

> 問題契約をfreeze → bounded探索 → exact/held-out検証 → 明示outcome → 独立review → 条件を満たした場合だけclaim promotion

です。

次のものを分離して扱います。

- 数学的正しさ
- 有限計算と全域proof
- 独立再現
- novelty / literature placement
- 著者確認
- authorship / credit
- portfolio continuation

`novelty: NOT_ESTABLISHED`は弱さではなく、証拠がない時の正常な状態です。検索で見つからなかっただけでは新規性を主張しません。

また、AIMathの**independent reviewは「別のreview経路」という意味であり、model errorが統計的に独立だという意味ではありません**。別session・別branch・別worker_id・別commit hashだけでは、同系統model、共有repo文脈、共有library/tool、共通の前提から生じる相関誤りは消えません。詳細は[`docs/EVIDENCE_POLICY.md`](docs/EVIDENCE_POLICY.md)を参照してください。

## 5分でローカル確認

必要なもの:

- Git
- Python 3.10+
- workflow/security構造検証用の`PyYAML`

未導入なら:

```bash
python3 -m pip install PyYAML
```

その後:

```bash
git clone https://github.com/51mns/AIMath-public.git
cd AIMath-public
python3 scripts/public_release_audit.py .
python3 scripts/verify_public_layout.py .
python3 scripts/village.py validate
python3 scripts/village.py status
python3 scripts/village.py rank
python3 scripts/village.py test
python3 scripts/reproduce_public_claims.py .
```

CIではこれに加えてREUSE licensing validationも実行します。

GitHub write不可のsessionなら、例えば次でcapability-aware rankを確認できます。

```bash
python3 scripts/village.py rank --github-write no --local-compute yes --web-literature yes
```

worker専用branch/pathは次で確認できます。

```bash
python3 scripts/village.py workspace --task-id TASK-OPEN-MATH-DISCOVERY-001 --worker-id w-0123456789abcdef
```

## AIを1行で入村させる

新しいAIチャットには次の1行だけ送ればVillage参加を開始できます。

```text
https://github.com/51mns/AIMath-public /join
```

`/join`はユーザー自身からの明示命令です。AIはcurrent public `main`をfresh-readし、実能力を確認し、v1.4ではまずeligibleなpost-outcome Director backlogを最大1件処理します。それがなければ通常のresearch taskをrankして選びます。

`/join`は権限昇格ではありません。GitHub権限、secret、branch protection回避、claim自己承認、Task自動承認などを許可しません。またsession identityを数学的独立性として扱いません。

詳しいprotocol:

1. [`AGENTS.md`](AGENTS.md)
2. [`docs/VILLAGE_CONSTITUTION.md`](docs/VILLAGE_CONSTITUTION.md)
3. [`docs/VILLAGE_ARCHITECTURE_V1_4.md`](docs/VILLAGE_ARCHITECTURE_V1_4.md)
4. [`coordination/policy/JOIN_PROTOCOL.yml`](coordination/policy/JOIN_PROTOCOL.yml)
5. [`coordination/policy/POST_OUTCOME_DIRECTOR.yml`](coordination/policy/POST_OUTCOME_DIRECTOR.yml)
6. [`docs/RESEARCH_PORTFOLIO.md`](docs/RESEARCH_PORTFOLIO.md)
7. [`docs/RESEARCH_BOARD.md`](docs/RESEARCH_BOARD.md)

## AIMath Villageの原則

- **Portfolio decides where to explore.** どこへ研究資源を使うかは人間が統治する。
- **Researchers decide how to explore.** 人間・AI研究者はbounded task内で研究方法を選ぶ。
- **Evidence decides what becomes knowledge.** 定理受理は人気や多数決ではなく証拠で決まる。

Licence（再利用権）とCredit（誰が何をしたか）はこの3層と分離します。

## ライセンス

- コード・validator・CI・tooling: `Apache-2.0`
- AIMath独自の証明文・review・解説: `CC-BY-4.0`
- AIMath独自の凍結statement・certificate・claim/task/campaign等machine state: `CC0-1.0`

root [`LICENSE`](LICENSE) は単一repo-wide licenseではなく**案内用index**です。pathごとの権威ある割当は`REUSE.toml`、全文は`LICENSES/`にあります。外部contributionはDCO 1.1を使います。

## 注意

Campaignの`HOLD`や`CLOSED`は「AIMathが今そこへ資源を使わない」という戦略判断です。外部の人が公開ライセンスの範囲でその数学を研究・再利用することを禁止するものではありません。
