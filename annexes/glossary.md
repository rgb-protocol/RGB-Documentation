---
description: Terminology used in RGB sorted in alphabetical order
---

# Glossary

### Anchor

Set of client-side data that proves the inclusion of a unique [commitment](glossary.md#commitment) inside a transaction. In RGB protocol it is constituted by:

* The Bitcoin transaction ID of the [witness transaction](glossary.md#witness-transaction).
* The Multi Protocol Commitment - [MPC](glossary.md#multi-protocol-commitment-mpc).
* The Deterministic Bitcoin Commitment - [DBC](glossary.md#deterministic-bitcoin-commitment-dbc).
* The [ETP](glossary.md#extra-transaction-proof-etp) in the case of [Tapret](../commitment-layer/deterministic-bitcoin-commitments-dbc/tapret.md) commitment scheme.

### AluVM

Acronym of Algorithmic logic unit Virtual Machine, it is a register-based virtual machine for smart contract validation and distributed computing, used but not limited to RGB contract validation.

[Link](https://www.aluvm.org/)

### Assignment

The RGB-equivalent of a transaction output modifying, updating or creating some properties of the state of a [contract](glossary.md#contract). It is formed by:

* A [Seal Definition](glossary.md#seal-definition)
* An [Owned State](../rgb-state-and-operations/components-of-a-contract-operation.md#owned-states)

[Link](../rgb-state-and-operations/components-of-a-contract-operation.md#assignments-of-an-owned-state)

### Business Logic

The set of operations and rules contained in a contract [Schema](glossary.md#schema) which allows for the rightful update of the [contract state](glossary.md#contract-state).

### Client-side Validation

The operation which allows the verification of some data exchanged between parties according to some defined protocol rules. In RGB protocol these data are in form of [consignment](glossary.md#consignment); the above data can be exchanged privately between the parties involved as, unlike Bitcoin protocol, they don't need to be registered on a public medium (e.g. the blockchain).

### Commitment

A defined mathematical object $$C$$,  deterministically derived from applying a cryptographic operation to some structured input data $$m$$, called the message. The commitment can be registered in a defined publication medium (e.g. the blockchain) and embeds two operations:

* _**Commit** operation, which_ takes as inputs a public message $$m$$ and a random value $$r$$, and by applying to them the chosen cryptographic algorithm returns a value $$C = \text{commit}(m, r)$$.
* _**Verify** operation, which_ takes the value returned by the commit algorithm $$C$$, the public message $$m$$ and the secret value $$r$$ and returns True/False. $$\text{verify}(m, r, com) \rightarrow (\text{True} / \text{False})$$.

The commitment is required to possess two fundamental security properties:

* _**Binding**_: requires that there cannot be two valid messages of the same commitment $$C$$. That is, it is computationally unfeasible to produce different $$m' \: | \: m' \neq m$$ and $$r' \: | \: r' \neq r$$ such that: $$\text{verify}(m,r,C)=\text{verify}(m',r',C) \rightarrow \text{True}$$
* _**Hiding**_: requires that the message $$m$$ cannot be easily discovered by commitment attempts, i.e., that $$r$$ be uniformly sampled in a set $$R$$ such that it is statistically independent of $$m$$.

### Consignment

The data transferred between parties that are subject to [client-side validation](glossary.md#client-side-validation). In RGB there are 2 types of consignment:

* Contract Consignment: provided by the contract issuer including the information about the contract setup, such as the [Schema](glossary.md#schema), the [Genesis](glossary.md#genesis), the [Interface](glossary.md#interface), and the [Interface Implementation](glossary.md#interface-implementation).
* Transfer Consignment: provided by the payer user party and containing all the state transition history up to the [terminal consignment](glossary.md#terminal-consignment-consignment-endpoint).

### Contract

A set of [rights](glossary.md#contract-rights) established and executed digitally between certain parties through RGB protocol. A contract possesses an [active state](../rgb-state-and-operations/state-transitions.md#state-generation-and-active-state) and [business logic](glossary.md#business-logic), expressed in terms of ownership rights and executive rights. The contract state, rights and conditions of valid operations are defined using RGB [schema](glossary.md#schema). Only state and operations which allowed by the schema declarations and validation scripts are allowed to happen within the contract scope.

### Contract Operation

An update to the [contract state](glossary.md#contract-state) performed according to the rules defined in the contract [schema](glossary.md#schema).

Contract operations include:

* [Genesis](glossary.md#genesis)
* [State Transition](glossary.md#state-transition)

### Contract Participant

An actor who participates in contract operations. Contract parties are classified into the following categories:

* **Contract issuer**: an actor creating contract [Genesis](glossary.md#genesis).
* **Contract party**: all actors who have some [ownership](glossary.md#ownership) rights over RGB [contract state](glossary.md#contract-state) which have been provided through an [Assignment](glossary.md#assignment).

### Contract Rights

RGB contract parties have different rights as a part of the contract conditions defined through RGB [Schema](glossary.md#schema). The rights under RGB contracts can be classified into the following categories:

* Ownership rights: the rights associated with the [ownership](glossary.md#ownership) of some UTXO referenced by a [Seal Definition](glossary.md#seal-definition).
* Executive rights: the ability to construct the [contract state](glossary.md#contract-state) in a final form, i.e. to construct a valid [state transition](glossary.md#state-transition) satisfying [schema](glossary.md#schema) validation rules.

### Contract State

The set of up-to-date, private, and public information that manifests the condition of a contract at a certain point in history. In RGB, the contract state is constituted by:

* [Global State](../rgb-state-and-operations/components-of-a-contract-operation.md#global-state)
* [Owned State(s)](../rgb-state-and-operations/components-of-a-contract-operation.md#owned-states)

### Deterministic Bitcoin Commitment - DBC

The set of rules which allows for the registration of a provably single [commitment](glossary.md#commitment) in a Bitcoin transaction. Specifically, RGB protocol embeds 2 forms of DBC:

* [Opret](../commitment-layer/deterministic-bitcoin-commitments-dbc/opret.md)
* [Tapret](../commitment-layer/deterministic-bitcoin-commitments-dbc/tapret.md)

### Directed Acyclic Graph - DAG

A directed graph that does not contain any directed cycle thus allowing topological ordering. A Blockchain or an RGB Contract [Shard](glossary.md#shard) are examples of DAG.

[Wikipedia link](https://en.wikipedia.org/wiki/Directed\_acyclic\_graph)

### Engraving

An optional data string that past owners of a contract can register in the contract history. It is implemented in the RGB21 [interface](glossary.md#interface).

### Extra Transaction Proof - ETP

The part of the [Anchor](../commitment-layer/anchors.md) that embeds the additional data necessary for the validation of [Tapret](../commitment-layer/deterministic-bitcoin-commitments-dbc/tapret.md) commitment contained in a [taproot](glossary.md#taproot) transaction, such as the internal PubKey and the Script Path Spend.

### Genesis

The set of data, regulated by a contract [schema](glossary.md#schema), which represents the starting state of every contract of RGB. It's the equivalent of Bitcoin Genesis Block at the client-side level.

[Link](../rgb-state-and-operations/state-transitions.md#genesis)

### Interface

The set of code instructions that allow for the parsing of the compiled binary data contained in [Schema](glossary.md#schema), [Contract Operation](glossary.md#contract-operation), and [States](glossary.md#contract-state) in user and wallet-readable information.

[Link](../rgb-contract-implementation/interface/)

### Interface Implementation

The set of code declarations that bind an [Interface](glossary.md#interface) to a [Schema](glossary.md#schema) and make possible the semantic translation operated by the Interface itself.

### Invoice

A [base58](https://en.wikipedia.org/wiki/Binary-to-text\_encoding#Base58) URL-encoded string embedding the necessary data in order to allow a payer counterpart to construct a [State Transition](glossary.md#state-transition).

### Global State

The set of public properties included in the [state](glossary.md#contract-state) of a [contract](glossary.md#contract), defined in [Genesis](glossary.md#genesis) and optionally updatable according to the rule defined therein, which are not [owned](glossary.md#ownership) by any party.

[Link](../rgb-state-and-operations/components-of-a-contract-operation.md#global-state)

### Lightning Network

A decentralized network of bidirectional payment (state) channels constituted by 2-of-2 mutisig wallet constructing and updating off-chain transactions. It represents a popular Bitcoin Layer 2 scaling solution.

[Link](https://lightning.network/)

### Multi Protocol Commitment - MPC

The Merkle Tree structure used in RGB to include in a single Bitcoin Blockchain commitment the multiple [Transition Bundles](glossary.md#transition-bundle) of different contracts.

[Link](commitment-layer/multi-protocol-commitments-mpc.md)

### Owned State

Part of the [state](glossary.md#contract-state) of a [contract](glossary.md#contract) enclosed into an [Assignment](glossary.md#assignment) that contains the definition of the digital property being subjected to someone's [ownership](glossary.md#ownership).

[Link](../rgb-state-and-operations/components-of-a-contract-operation.md#owned-states)

### Ownership

The control and thus the possibility to spend a [UTXO](glossary.md#utxo) to which some client-side property isthat [assigned](glossary.md#assignment).

### Partially Signed Bitcoin Transaction - PSBT

A transaction which lacks some element of its signature and which can be completed/finalized with some additional elements later in time.

[Link](https://github.com/bitcoin/bips/blob/master/bip-0174.mediawiki)

### Schema

A declarative piece of code that contains the set of variables, rules, and [business logic](glossary.md#business-logic) according to which an RGB contract works.

[Link](../rgb-contract-implementation/schema/)

### Seal Definition

The reference part of an [Assignment](glossary.md#assignment) which binds the commitment to a [UTXO](glossary.md#utxo) belonging to the new [owner](glossary.md#ownership).

[Link](../rgb-state-and-operations/components-of-a-contract-operation.md#seal-definition)

### Shard

A branch of the [DAG](glossary.md#directed-acyclic-graph---dag) chain of the RGB [State Transitions](glossary.md#state-transition).

### Single-Use Seal

A promise to [commit](glossary.md#commitment) to a yet unknown message in the future, once and only once, such that commitment fact will be provably known to all members of a certain audience.

[Link](../distributed-computing-concepts/single-use-seals.md)

### Stash

The set of client-side data related to one or more [contracts](glossary.md#contract) that undergo [validation](glossary.md#client-side-validation) and are stored by the users.

### State Transition

The most important [contract operation](glossary.md#contract-operation) that makes possible the transition of an RGB State to a New State, changing [state](glossary.md#contract-state) data and/or ownership.

[Link](../rgb-state-and-operations/state-transitions.md#state-transitions-and-their-mechanics)

### Taproot

The Bitcoin's Segwit v1 transaction format detailed in [BIP341](https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki) and [BIP342](https://github.com/bitcoin/bips/blob/master/bip-0342.mediawiki).

### Terminal Consignment - Consignment Endpoint

A [transfer consignment](glossary.md#consignment) that includes the last state of a contract embedding the [State Transition](glossary.md#state-transition) constructed from a payee counterparty [invoice](glossary.md#invoice).

### Transition Bundle

A set of RGB [State Transitions](glossary.md#state-transition) that belong to the same contract and that are committed in the same [witness transaction](glossary.md#witness-transaction).

[Link](../rgb-state-and-operations/state-transitions.md#transition-bundle)

### UTXO

A Bitcoin Unspent Transaction Output. It is defined by a transaction hash and a _vout_ index which, collectively, constitute an [outpoint](https://en.bitcoin.it/wiki/Protocol\_documentation#tx).

### Witness Transaction

The transaction that provides the [Seal](glossary.md#single-use-seal) closing operation around a message that contains a [Multi Protocol Commitment](glossary.md#multi-protocol-commitment-mpc) an [MPC](glossary.md#multi-protocol-commitment-mpc) Tree.

***
