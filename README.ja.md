# AIMath Public 日本語ガイド

これはAIMathの**公開専用・履歴なし版**です。private研究リポジトリをそのまま公開したものではありません。

公開スナップショットの基準SHAは `c8e61e0e398f540bc8c5de79663398d689f37473` です。

## 最初に見る場所

- [`docs/RESULTS.md`](docs/RESULTS.md): 受理済み成果と公開claim package
- [`docs/CONTRIBUTION_TARGETS.md`](docs/CONTRIBUTION_TARGETS.md): 外部から手伝いやすい現在の限定タスク
- [`docs/FAILED_ROUTES.md`](docs/FAILED_ROUTES.md): すでに失敗・停止・反証された研究ルートと再開条件
- [`docs/EVIDENCE_POLICY.md`](docs/EVIDENCE_POLICY.md): 証明・有限計算・独立再現・noveltyを混同しないための証拠ルール
- [`docs/EXPORT_GAPS.md`](docs/EXPORT_GAPS.md): まだpublicへ完全輸出していない再現物
- [`docs/CLAIM_LEVELS.md`](docs/CLAIM_LEVELS.md): `INDEPENDENTLY_REPRODUCED` などの意味
- [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md): 再現方法
- [`CONTRIBUTING.md`](CONTRIBUTING.md): 証明の検証、反例、改善案の出し方

新しい証明ルートを始める前に `FAILED_ROUTES.md` を確認してください。単に計算量、探索深度、多項式次数などを増やしただけで、既に閉じたアーキテクチャを繰り返さないためです。

## 一括確認

Python 3.10+ を使える通常のGit checkoutでは、次で公開版の主要チェックを実行できます。

```bash
python3 scripts/public_release_audit.py .
python3 scripts/verify_public_layout.py .
python3 scripts/reproduce_public_claims.py .
```

`reproduce_public_claims.py` は、公開されている実行可能なclaim packageをまとめて再現します。純粋な数学証明が本体のclaimについて、無理に「計算が通ったから証明」と置き換えることはしません。

## claimの読み方

AIMathでは次を別々に扱います。

- 数学的に正しいか
- 有限計算が再現できるか
- 別reviewerが独立再現したか
- 文献上の新規性があるか
- 原著者確認があるか
- 外部の未解決問題のfrontierを実際に動かしたか

そのため、`INDEPENDENTLY_REPRODUCED` でも自動的に「世界初」「新定理」という意味にはなりません。

`RESULTS.md` に名前があるだけでは完全公開とは扱いません。第三者がpublic repoだけで statement・proof/certificate・reproduction・independent review・novelty status を追えないものは `EXPORT_GAPS.md` で未完として管理します。

## プライバシー

公開版には、生のChatGPT会話、個人情報、メール/DM、生の原著者対応、認証情報、private添付、内部調整ログ、private Git履歴を含めません。private上の有用な数学は、private branch/historyを露出するのではなく、固定された数学的証拠からcleanな公開claim packageとして再構成します。
