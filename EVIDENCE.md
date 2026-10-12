# Evidence: Rubric on GenLayer StudioNet

Every row below was read back from the chain by `scripts/evidence.mjs`: the
sender, the status and the outcome come from the node's answer for each hash,
not from the deployment record. Every outcome on chain matches the record.

- **Contract:** [`0x180a2aF66032CE523E2bab92Fc5e1E0427D9Da0B`](https://explorer-studio.genlayer.com/address/0x180a2aF66032CE523E2bab92Fc5e1E0427D9Da0B)
- **Deploy transaction:** [`0x1edb206a…5482`](https://explorer-studio.genlayer.com/tx/0x1edb206a5b5a424c44a19870662a2466f8659169cada261bdabd52f771025482)
- **Source sha256:** `2522c79aa6e36c00174d07a10b4341a563465f7113e61f225d351a4e47f77eed`
- **Transactions:** 17, from 6 different wallets
- **Generated:** 2026-10-12 07:49 UTC

## Wallets

Each wallet was made in memory for this run, and its key was never written
anywhere. Click an address to see every transaction it sent.

| Role | Address | Transactions sent |
|---|---|---|
| sponsor | [`0x9901A7b34e2867C2CdFD3518E166b59557B963bD`](https://explorer-studio.genlayer.com/address/0x9901A7b34e2867C2CdFD3518E166b59557B963bD) | 4 |
| ann | [`0x0FaaE5e6de55Ca5fF589F541b5fF01f9675a9CEd`](https://explorer-studio.genlayer.com/address/0x0FaaE5e6de55Ca5fF589F541b5fF01f9675a9CEd) | 4 |
| ben | [`0x88E1879A08e0EE42a93Ed3a3b53532aE757229c2`](https://explorer-studio.genlayer.com/address/0x88E1879A08e0EE42a93Ed3a3b53532aE757229c2) | 1 |
| cal | [`0x7D7DbBDfB28BC4AA71782035e555FC7D1f3EcB60`](https://explorer-studio.genlayer.com/address/0x7D7DbBDfB28BC4AA71782035e555FC7D1f3EcB60) | 2 |
| dev | [`0xCf2F8f189db2050fdaECDA48ebeBD989b888A645`](https://explorer-studio.genlayer.com/address/0xCf2F8f189db2050fdaECDA48ebeBD989b888A645) | 2 |
| stranger | [`0xCA6C57a56D215832b8C3d53F9F751b0E6031445E`](https://explorer-studio.genlayer.com/address/0xCA6C57a56D215832b8C3d53F9F751b0E6031445E) | 4 |

## Transactions, in order

"refused" is a transaction the contract was meant to refuse: the committee
agreed on the refusal, and the sentence is the contract's own.

| # | Step | Sent by | Method | On chain | Outcome | Tx |
|---|---|---|---|---|---|---|
| 0 | deploy | sponsor [`0x9901…63bD`](https://explorer-studio.genlayer.com/address/0x9901A7b34e2867C2CdFD3518E166b59557B963bD) | `deploy` | FINALIZED · MAJORITY_AGREE | executed | [`0x1edb206a…5482`](https://explorer-studio.genlayer.com/tx/0x1edb206a5b5a424c44a19870662a2466f8659169cada261bdabd52f771025482) |
| 1 | prize 0 opened: 0.5 GEN, three criteria | sponsor [`0x9901…63bD`](https://explorer-studio.genlayer.com/address/0x9901A7b34e2867C2CdFD3518E166b59557B963bD) | `open` | FINALIZED · MAJORITY_AGREE | executed | [`0xae757dfc…6e0e`](https://explorer-studio.genlayer.com/tx/0xae757dfc46d11edd9947b837bd3fcfe7f2a2dc3cbd9356ca69cf81f639d36e0e) |
| 2 | the sponsor enters its own prize | sponsor [`0x9901…63bD`](https://explorer-studio.genlayer.com/address/0x9901A7b34e2867C2CdFD3518E166b59557B963bD) | `enter` | FINALIZED · MAJORITY_AGREE | refused: the sponsor cannot enter its own prize | [`0x4483394a…a271`](https://explorer-studio.genlayer.com/tx/0x4483394a29ea436d6a52572ef6c59f1c73220ceb329e4f7aae70ecfd709ca271) |
| 3 | entry 0: Ann | ann [`0x0Faa…9CEd`](https://explorer-studio.genlayer.com/address/0x0FaaE5e6de55Ca5fF589F541b5fF01f9675a9CEd) | `enter` | FINALIZED · MAJORITY_AGREE | executed | [`0x3a513fb1…982c`](https://explorer-studio.genlayer.com/tx/0x3a513fb16e860884367426d28481faf16f299f82f300c969abe5b9ae8b49982c) |
| 4 | entry 1: Ben, leaves out appeals | ben [`0x88E1…29c2`](https://explorer-studio.genlayer.com/address/0x88E1879A08e0EE42a93Ed3a3b53532aE757229c2) | `enter` | FINALIZED · MAJORITY_AGREE | executed | [`0x178933a0…351c`](https://explorer-studio.genlayer.com/tx/0x178933a079a5d05a48ef2cc1842b1bd0f5aeeee3867c6a33430458ebf319351c) |
| 5 | entry 2: Cal, hype | cal [`0x7D7D…cB60`](https://explorer-studio.genlayer.com/address/0x7D7DbBDfB28BC4AA71782035e555FC7D1f3EcB60) | `enter` | FINALIZED · MAJORITY_AGREE | executed | [`0x0300c94d…a4ad`](https://explorer-studio.genlayer.com/tx/0x0300c94d3d7f3775a33f23ca1c8a7a607da6515bf533854bed902ef11504a4ad) |
| 6 | entry 3: Dev | dev [`0xCf2F…A645`](https://explorer-studio.genlayer.com/address/0xCf2F8f189db2050fdaECDA48ebeBD989b888A645) | `enter` | FINALIZED · MAJORITY_AGREE | executed | [`0xc04daa47…0237`](https://explorer-studio.genlayer.com/tx/0xc04daa47102494beda8cc734848ea1ead89958822ae126bbc7aaed14a86d0237) |
| 7 | Ann enters a second time | ann [`0x0Faa…9CEd`](https://explorer-studio.genlayer.com/address/0x0FaaE5e6de55Ca5fF589F541b5fF01f9675a9CEd) | `enter` | FINALIZED · MAJORITY_AGREE | refused: an entrant enters once per prize | [`0x7ff48e85…c225`](https://explorer-studio.genlayer.com/tx/0x7ff48e856c93b3732b02e747e0c805dbc3a7826ee7b87d52a7975fc3e5c0c225) |
| 8 | a judging before entries close | ann [`0x0Faa…9CEd`](https://explorer-studio.genlayer.com/address/0x0FaaE5e6de55Ca5fF589F541b5fF01f9675a9CEd) | `judge` | FINALIZED · MAJORITY_AGREE | refused: judging opens when entries close at 2026-10-12T06:48:42Z | [`0xda2e7007…4c01`](https://explorer-studio.genlayer.com/tx/0xda2e7007f407db543ade66e8383f61afd9c8ae0e22de90bca49180b6a8744c01) |
| 9 | an entry after entries closed | stranger [`0xCA6C…445E`](https://explorer-studio.genlayer.com/address/0xCA6C57a56D215832b8C3d53F9F751b0E6031445E) | `enter` | FINALIZED · MAJORITY_AGREE | refused: entries closed at 2026-10-12T06:48:42Z | [`0x1b2da61d…4f1f`](https://explorer-studio.genlayer.com/tx/0x1b2da61da086024903bcde814c04b981d89ec136cb5885f3921fc3f1726f4f1f) |
| 10 | a stranger asks for a judging | stranger [`0xCA6C…445E`](https://explorer-studio.genlayer.com/address/0xCA6C57a56D215832b8C3d53F9F751b0E6031445E) | `judge` | FINALIZED · MAJORITY_AGREE | refused: only the sponsor or an entrant on this prize may ask for a judging | [`0x5dcfe38d…e537`](https://explorer-studio.genlayer.com/tx/0x5dcfe38d92a16dee539bbf16ccb3abe47c456b2e0820f6ca2a0419e3f1dee537) |
| 11 | entry 1 judged: both orders | sponsor [`0x9901…63bD`](https://explorer-studio.genlayer.com/address/0x9901A7b34e2867C2CdFD3518E166b59557B963bD) | `judge` | FINALIZED · MAJORITY_AGREE | executed | [`0x5ec297c4…7b9c`](https://explorer-studio.genlayer.com/tx/0x5ec297c49c6933fa7542c5098748a83033fdcf1daadcd1ab8c50d08bd47e7b9c) |
| 12 | entry 0 judged: both orders | ann [`0x0Faa…9CEd`](https://explorer-studio.genlayer.com/address/0x0FaaE5e6de55Ca5fF589F541b5fF01f9675a9CEd) | `judge` | FINALIZED · MAJORITY_AGREE | executed | [`0xf0b8f7fe…248a`](https://explorer-studio.genlayer.com/tx/0xf0b8f7fef6352f3f6ae9da98a5588bda4e093e78c880227f62e8962bd41d248a) |
| 13 | entry 2 judged: both orders | cal [`0x7D7D…cB60`](https://explorer-studio.genlayer.com/address/0x7D7DbBDfB28BC4AA71782035e555FC7D1f3EcB60) | `judge` | FINALIZED · MAJORITY_AGREE | executed | [`0x80ab936d…1e8b`](https://explorer-studio.genlayer.com/tx/0x80ab936d281c35b71c01df92acd869a8b9943b86bf4d163511795e00ef6b1e8b) |
| 14 | an award while entry 3 waits | stranger [`0xCA6C…445E`](https://explorer-studio.genlayer.com/address/0xCA6C57a56D215832b8C3d53F9F751b0E6031445E) | `award` | FINALIZED · MAJORITY_AGREE | refused: entry 3 is waiting to be judged until 2026-10-12T07:13:42Z | [`0x9e87e5db…a423`](https://explorer-studio.genlayer.com/tx/0x9e87e5db5093650628a8ed4198285d9cda5a02c70306efb7c5059457e51fa423) |
| 15 | entry 3 judged after judging closed | dev [`0xCf2F…A645`](https://explorer-studio.genlayer.com/address/0xCf2F8f189db2050fdaECDA48ebeBD989b888A645) | `judge` | FINALIZED · MAJORITY_AGREE | refused: judging closed at 2026-10-12T07:13:42Z; an entry nobody judged scores nothing at the award | [`0xd45a6e69…e912`](https://explorer-studio.genlayer.com/tx/0xd45a6e692a178e29750a67b8932d915f5056fa28de73c8b6604d706dd042e912) |
| 16 | prize 0 awarded | stranger [`0xCA6C…445E`](https://explorer-studio.genlayer.com/address/0xCA6C57a56D215832b8C3d53F9F751b0E6031445E) | `award` | FINALIZED · MAJORITY_AGREE | executed | [`0x9757501d…c4da`](https://explorer-studio.genlayer.com/tx/0x9757501ddecd8ef097817faa94e012e364f069fd1d4690e0a746d2742808c4da) |
