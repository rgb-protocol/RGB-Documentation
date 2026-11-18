# Commitment Schemes within Bitcoin and RGB

In this chapter, we will explore the application of client-side validation and [single-use seal](../annexes/glossary.md#single-use-seal) to the Bitcoin blockchain, introducing the main architectural features of **RGB protocol that are related to the commitment layer (Layer 1)**.

As mentioned in the previous chapter, the cryptographic operations above can be generally applied to different blockchains and different publication media. However, the outstanding properties of the Bitcoin consensus algorithm (particularly those that enable decentralization, censorship resistance, and permissionless access) make it the ideal technology stack for the development of advanced programmability features: the kind required by digital bearer rights and smart contracts.

As shown in the previous section, the creation of single-use seals is subject to two basic operations: [Seal Definition](../distributed-computing-concepts/single-use-seals.md#seal-definition) and [Seal Closing](../distributed-computing-concepts/single-use-seals.md#seal-closing). We will now explore how these two operations are implemented **using Bitcoin transactions as a publication medium** for RGB protocol. A more generic overview of single-use seals constructions on the Bitcoin blockchain can be found [here](../annexes/single-use-seals-bitcoin.md).

### Single-use Seals in RGB

RGB seals are represented by Bitcoin unspent transaction outputs (UTXOs), so that:
- A seal is **defined** when some **state** is linked to a specific UTXO which identifies its owner
- A seal is **closed** around a **message** when a transaction spends the UTXO and commits to that message

These two operations are then chained together, in that the message which closes the previous seal also includes the new seal definition, so that the [witness transaction](../annexes/glossary.md#witness-transaction):
- spends the UTXO on which a seal was defined, thus closing the seal;
- has an output that contains a commitment to a new seal definition.

### RGB Client-side Validation

In the next paragraphs, we will focus on client-side validation, as applied to the above construction of a single-use seal, showing it step by step through the usual cryptographic characters: Alice, who performs a seal operation, and Bob as an observer.

1. First of all, Alice has a [UTXO](../annexes/glossary.md#utxo) **that is linked to some client-side validated data** that only she knows.

<figure><img src="../.gitbook/assets/txo2-1.webp" alt=""><figcaption><p><strong>A seal definition is applied to a specific Bitcoin UTXO.</strong></p></figcaption></figure>

2. Alice informs Bob that the spending of this UTXO signals that some seal was closed.

<figure><img src="../.gitbook/assets/txo2-2.webp" alt=""><figcaption><p><strong>The UTXO is associated with a specific meaning agreed between Alice and Bob.</strong></p></figcaption></figure>

3. Once Alice spends her UTXO, only Bob knows that this event has some additional meaning and consequences, even though everyone (i.e. the Bitcoin blockchain audience) can see the transaction.

<figure><img src="../.gitbook/assets/txo2-3.webp" alt=""><figcaption><p><strong>Spending the UTXO triggers some meaningful consequences for the parties involved.</strong></p></figcaption></figure>

4. In fact, the [witness transaction](../annexes/glossary.md#witness-transaction) that spends Alice's UTXO contains a commitment to a change in the client-side validated data. By sharing the original data with Bob, she can prove to him that the commitment correctly corresponds to that data. Bob can independently verify that the new seal definition is unequivocally bound to the seal closing, so that nobody can receive a different one and mistakenly accept it as valid. This way, the protocol effectively **prevents double-spending**.

<figure><img src="../.gitbook/assets/txo2-4.webp" alt=""><figcaption><p><strong>Alice can deterministically prove to Bob the uniqueness of the committed message. In addition, the message may contain another seal definition, extending the chain of commitments.</strong></p></figcaption></figure>

Combining single-use seals with client-side validation guarantees two properties: the spending event is unique, and the committed data in it (i.e., the message) cannot be changed in the future. The whole operation can be summarized as follows.

<figure><img src="../.gitbook/assets/txo2-5.webp" alt=""><figcaption><p><strong>The UTXO being spent represents the seal closing. A specific kind of transaction output contains the message, which represents a new seal definition.</strong></p></figcaption></figure>

The next important step is to illustrate precisely how the two commitment schemes adopted in RGB protocol on Bitcoin, **Opret** and **Tapret**, work and which requirements they must meet, particularly concerning commitment determinism.

***
