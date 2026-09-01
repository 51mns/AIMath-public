# AIMath Public 日本語ガイド

これはAIMathの**公開専用・履歴なし版**です。private研究リポジトリをそのまま公開したものではありません。

公開スナップショットの基準SHAは `c8e61e0e398f540bc8c5de79663398d689f37473` です。

## 最初に見る場所

- [`docs/RESULTS.md`](docs/RESULTS.md): 何が確認済みか
- [`docs/FAILED_ROUTES.md`](docs/FAILED_ROUTES.md): すでに失敗・停止・反証された研究ルートと再開条件
- [`docs/EXPORT_GAPS.md`](docs/EXPORT_GAPS.md): private正本にはあるが、まだpublicへ証明・再現物まで完全輸出できていない成果
- [`docs/CLAIM_LEVELS.md`](docs/CLAIM_LEVELS.md): `INDEPENDENTLY_REPRODUCED` などの意味
- [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md): 再現方法
- [`CONTRIBUTING.md`](CONTRIBUTING.md): 証明の検証、反例、改善案の出し方

新しい証明ルートを始める前に `FAILED_ROUTES.md` を確認してください。単に計算量、探索深度、多項式次数などを増やしただけで、既に閉じたアーキテクチャを繰り返さないためです。

`RESULTS.md` に名前があるだけでは完全公開とは扱いません。第三者がpublic repoだけで statement・proof/certificate・reproduction・independent review・novelty status を追えないものは `EXPORT_GAPS.md` で未完として管理します。

AIMathでは「数学的に正しいか」「別の人が再現したか」「既知結果か新規結果か」「原著者確認があるか」を別々に扱います。

公開版には、生のChatGPT会話、個人情報、メール、認証情報、private添付、内部調整ログ、private Git履歴は含めません。
