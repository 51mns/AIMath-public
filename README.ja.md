# AIMath Public

AIMathの**履歴を引き継がない公開研究リポジトリ**です。private正本のGit履歴・生チャット・メール・個人情報をmirrorしません。

公開snapshotのprivate canonical source: `c8e61e0e398f540bc8c5de79663398d689f37473`

## AIMath Village v1

中心原則は次の3つです。

- **Portfolio decides where to explore.** どこへ研究資源を使うかは人間が統治する。
- **Researchers decide how to explore.** 人間・AI研究者はbounded taskの中で研究方法を選ぶ。
- **Evidence decides what becomes knowledge.** 定理の受理は人気や多数決ではなく証拠で決まる。

Licence（再利用権）とCredit（誰が何をしたか）はこの3層と分離します。

最初に [`AGENTS.md`](AGENTS.md)、[`docs/VILLAGE_CONSTITUTION.md`](docs/VILLAGE_CONSTITUTION.md)、[`docs/RESEARCH_PORTFOLIO.md`](docs/RESEARCH_PORTFOLIO.md) を読んでください。

## ローカル確認

```bash
python3 scripts/public_release_audit.py .
python3 scripts/verify_public_layout.py .
python3 scripts/village.py validate
python3 scripts/village.py status
python3 scripts/village.py test
python3 scripts/reproduce_public_claims.py .
```

## ライセンス

- コード・validator・CI・tooling: `Apache-2.0`
- AIMath独自の証明文・review・解説: `CC-BY-4.0`
- AIMath独自の凍結statement・certificate・claim/task/campaign等machine state: `CC0-1.0`

詳細は [`LICENSING.md`](LICENSING.md) と `REUSE.toml`。外部contributionはDCO 1.1を使います。

## 注意

Campaignの`HOLD`や`CLOSED`は「AIMathが今そこへ資源を使わない」という戦略判断です。外部の人が公開ライセンスの範囲でその数学を研究・再利用することを禁止するものではありません。
