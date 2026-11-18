# Multi Protocol Commitments - MPC

Before going into the details, it is useful to give a general definition of Multi Protocol Commitments. The `mpc::Commitment` is the 32-byte tagged hash that anchors RGB operations to the Bitcoin blockchain through the `Opret` or `Tapret` scheme.

The MPC standard addresses the following important requirements:

1. How the tagged `mpc::Commitment` hash is constructed before it is committed to the Bitcoin blockchain.
2. How the state changes of multiple contracts can be included in a single commitment.

Both points are satisfied through an **ordered merklization** of the involved contracts, each represented by its contract ID and [transition bundle](../annexes/glossary.md#transition-bundle) ID, in an [MPC](../annexes/glossary.md#multi-protocol-commitment-mpc) tree. The properties of the tree are described in detail below. Finally, the root of the tree (`mpc::Root`) is hashed once more to obtain the `mpc::Commitment`, which is embedded in an output of the [witness transaction](../annexes/glossary.md#witness-transaction) through the appropriate [Deterministic Bitcoin Commitment](../annexes/glossary.md#deterministic-bitcoin-commitment-dbc) scheme.

<figure><img src="../.gitbook/assets/immagine (1).webp" alt=""><figcaption><p><strong>Each RGB contract has a unique position in the MPC tree, determined by a modulo operation applied to its ContractId and based on the width of the tree. In this example, the MPC tree has a width of 8.</strong></p></figcaption></figure>

## The MPC Commitment Hash

The commitment to the MPC tree, which goes into either an [Opret](deterministic-bitcoin-commitments-dbc/opret.md) or a [Tapret](deterministic-bitcoin-commitments-dbc/tapret.md) commitment, is the `mpc::Commitment`, constructed as a BIP-340 tagged hash as follows:

`mpc::Commitment = SHA-256(SHA-256(mpc_tag) || SHA-256(mpc_tag) || depth || cofactor || mpc::Root)`

Where:

* `mpc_tag = urn:ubideco:mpc:commitment#2024-01-31` follows the [RGB tagging conventions](../annexes/commitments.md#specific-rgb-consensus-commitments).
* `depth` is the depth of the tree, encoded as a single byte.
* `cofactor` is the value used to obtain distinct positions for the contracts in the tree, encoded as a 16-bit little-endian unsigned integer (see [MPC Tree Construction](#mpc-tree-construction)).
* `mpc::Root` is the root of the MPC tree, whose construction is explained in the following sections.

## MPC Tree Construction

To construct the MPC tree, a **unique leaf position must be found deterministically for each contract**.

Let `C` be the number of contracts to include in the MPC, with `i = {0, 1, ..., C-1}`, and let `c_i = ContractId(i)` be the identifier of each contract. The tree has `w` leaves with `w ≥ C`, which corresponds to a depth `d` such that `2^d = w`. Thus, each contract identifier `c_i` is placed in a unique position `pos(c_i)` determined by the modulo operation detailed below.

In essence, building a suitable tree of width `w` that hosts each contract `c_i` in a unique position works like a mining process: the greater the number of contracts `C`, the greater the number of leaves `w` must be. Assuming a random distribution of `pos(c_i)`, as per the [Birthday Paradox](https://en.wikipedia.org/wiki/Birthday\_problem), there is a \~50% probability of a collision in a tree with `w ~ C^2`.

To keep MPC trees from growing too large, and assuming the random nature of collisions, the construction includes an additional optimization.

The actual formula for determining the **leaf position of the contract** is the following:

    pos(c_i) = c_i mod (w - cofactor)

where `c_i` is read as a 256-bit little-endian integer, and `cofactor` is a number that increases the chance of obtaining distinct values of `pos(c_i)` deterministically for a given `w`.

The construction starts from the smallest tree with `w ≥ C`, with a minimal depth of 3 (8 leaves) by default to avoid leaking the exact number of contracts in the tree, and tries a certain number of `cofactor` values. If none of them can produce `C` distinct positions, the construction increases `d` by one and starts a new series of attempts. In particular, `cofactor` goes from `0` up to `w/2`, with a cap of 500 attempts for performance reasons: larger values cannot succeed, since a tree of depth `d-1` would otherwise have hosted all the contracts.

### **Contract Leaves (Inhabited)**

Once the construction finds `C` distinct positions `pos(c_i)`, with `i = 0, ..., C-1`, it fills every corresponding leaf with a tagged hash built in the following way:

`tH_MPC_LEAF(c_i) = SHA-256(SHA-256(merkle_tag) || SHA-256(merkle_tag) || 0x10 || c_i || BundleId(c_i))`

Where:

* `merkle_tag = urn:ubideco:merkle:node#2024-01-31`, chosen according to the [RGB conventions for Merkle tree tagging](../annexes/commitments.md#merklization-procedure).
* `0x10` is the integer identifier of contract leaves, encoded as a single byte.
* `c_i` is the 32-byte `ContractId`, the tagged hash of the contract's [Genesis](../rgb-state-and-operations/state-transitions.md#genesis) operation.
* `BundleId(c_i)` is the 32-byte hash of the [Transition Bundle](../rgb-state-and-operations/state-transitions.md#transition-bundle) that groups the [State Transitions](../annexes/glossary.md#state-transition) of contract `c_i` in the same witness transaction (see [Bundle ID](../annexes/commitments.md#bundle-id)).

### **Entropy leaves (Uninhabited)**

For the remaining `w - C` uninhabited leaves, the tree commits to a dummy value. Each leaf in position `j` that is not occupied by any contract (`j ≠ pos(c_i)` for every `i`) gets a tagged hash built as follows:

`tH_MPC_LEAF(j) = SHA-256(SHA-256(merkle_tag) || SHA-256(merkle_tag) || 0x11 || entropy || j)`

Where:

* `merkle_tag = urn:ubideco:merkle:node#2024-01-31`, chosen according to the [RGB conventions for Merkle tree tagging](../annexes/commitments.md#merklization-procedure).
* `0x11` is the integer identifier of entropy leaves, encoded as a single byte.
* `entropy` is a 64-bit random value chosen by the party constructing the tree.
* `j` is the position of the leaf, encoded as a 32-bit little-endian unsigned integer.

### MPC nodes

After generating the base of the MPC tree with `w` leaves, the construction merklizes the tree by following the [merklization procedure](../annexes/commitments.md#merklization-procedure) of the `commit_verify` module (part of `rgb-consensus`).

Each non-leaf node of the tree, including the root `mpc::Root`, has a tagged hash computed as:

`tH_MPC_BRANCH(tH1 || tH2) = SHA-256(SHA-256(merkle_tag) || SHA-256(merkle_tag) || b || d || w || tH1 || tH2)`

Where:

* `merkle_tag = urn:ubideco:merkle:node#2024-01-31`, chosen according to the [RGB conventions for Merkle tree tagging](../annexes/commitments.md#merklization-procedure).
* `b` is the branching of the node, i.e. the number of its children, encoded as an 8-bit unsigned integer. Since the width of an MPC tree is always a power of two, `b` is always `0x02`.
* `d` is the node depth within the tree (i.e. the length of its path to the root), encoded as an 8-bit unsigned integer.
* `w` is the tree width, encoded as a 256-bit little-endian unsigned integer.
* `tH1` and `tH2` are the hashes of the left and the right child respectively, each computed with the formula for its own type: contract leaf, entropy leaf or MPC node.

The following diagram shows an example MPC tree, where:

* `C = 3` is the number of contracts to place.
* As an example, the contracts occupy the positions `pos(c_0) = 7`, `pos(c_1) = 4`, and `pos(c_2) = 2`.
* `BUNDLE_i = BundleId(c_i)`.
* `d` is `0` for the root and increases by one at each level: for example, `tH_MPC_BRANCH(tHA || tHB)` has `d=2`.
* `w=8` for every node in the tree.

{% code fullWidth="true" %}
```
                                                                                   +---------------------------------+
                                                                   mpc::Root       | tH_MPC_BRANCH(tHABCD || tHEFGH) |
                                                                                   +-----------^---------^-----------+
                                                                                               |         |
                                              +------------------------------------------------+         +--------------------------------------------+
                                              |                                                                                                       |
                                +-------------+---------------+                                                                         +-------------+---------------+
                                | tH_MPC_BRANCH(tHAB || tHCD) |                                                                         | tH_MPC_BRANCH(tHEF || tHGH) |
                                +----------------^--------^---+                                                                         +-----------------^--------^--+
                                                 |        |                                                                                               |        |
                     +---------------------------+        +--------------+                                                   +----------------------------+        +------------+
                     |                                                   |                                                   |                                                  |
       +-------------+-------------+                       +-------------+-------------+                       +-------------+-------------+                      +-------------+-------------+
       | tH_MPC_BRANCH(tHA || tHB) |                       | tH_MPC_BRANCH(tHC || tHD) |                       | tH_MPC_BRANCH(tHE || tHF) |                      | tH_MPC_BRANCH(tHG || tHH) |
       +----------------^------^---+                       +----------------^------^---+                       +----------------^------^---+                      +----------------^------^---+
                        |      |                                            |      |                                            |      |                                           |      |
         +--------------+      +-----+                       +--------------+      +-----+                       +--------------+      +-----+                      +--------------+      +-----+
         |                           |                       |                           |                       |                           |                      |                           |
 +-------+--------+        +---------+------+        +-------+--------+        +---------+------+        +-------+--------+        +---------+------+        +------+---------+        +--------+-------+
 | tH_MPC_LEAF(A) |        | tH_MPC_LEAF(B) |        | tH_MPC_LEAF(C) |        | tH_MPC_LEAF(D) |        | tH_MPC_LEAF(E) |        | tH_MPC_LEAF(F) |        | tH_MPC_LEAF(G) |        | tH_MPC_LEAF(H) |
 +-------------^--+        +-------------^--+        +-------------^--+        +-------------^--+        +-------------^--+        +-------------^--+        +-------------^--+        +-------------^--+
               |                         |                         |                         |                         |                         |                         |                         |
+--------------+-------+  +--------------+-------+  +--------------+----------+  +-----------+----------+ +------------+------------+  +---------+------------+  +---------+------------+  +---------+---------------+
| 0x11 || entropy || 0 |  | 0x11 || entropy || 1 |  | 0x10 || c_2 || BUNDLE_2 |  | 0x11 || entropy || 3 | | 0x10 || c_1 || BUNDLE_1 |  | 0x11 || entropy || 5 |  | 0x11 || entropy || 6 |  | 0x10 || c_0 || BUNDLE_0 |
+----------------------+  +----------------------+  +-------------------------+  +----------------------+ +-------------------------+  +----------------------+  +----------------------+  +-------------------------+
```
{% endcode %}

### MPC Tree Verification

To prove that the client-side validated data of a contract `c_i`, collected in `BUNDLE_i`, is part of the tree, a verifier needs only a Merkle proof that points at the corresponding leaf. As a result, verifiers of different contracts never need the full view of the Merkle tree, unlike the builder. Together with the dummy entropy leaves, this partial view hides the other contracts in the tree from each verifier, and thus provides a high degree of privacy. In the example tree of the diagram above, a verifier of the contract `c_2` would receive the following Merkle proof from the tree builder:

{% code fullWidth="true" %}
```
                                                                            +---------------------------------+
                                                           mpc::Root        | tH_MPC_BRANCH(tHABCD || tHEFGH) |
                                                                            +----------------^---------^------+
                                                                                             |         |
                                       +-----------------------------------------------------+         +---------------------------------------+
                                       |                                                                                                       |
                         +-------------+---------------+                                                                         +-------------+---------------+
                         | tH_MPC_BRANCH(tHAB || tHCD) |                                                                         | tH_MPC_BRANCH(tHEF || tHGH) |
                         +----------------^--------^---+                                                                         +-----------------------------+
                                          |        |
              +---------------------------+        +--------------+
              |                                                   |
+-------------+-------------+                       +-------------+-------------+
| tH_MPC_BRANCH(tHA || tHB) |                       | tH_MPC_BRANCH(tHC || tHD) |
+---------------------------+                       +----------------^------^---+
                                                                     |      |
                                                      +--------------+      +-----+
                                                      |                           |
                                              +-------+--------+        +---------+------+
                                              | tH_MPC_LEAF(C) |        | tH_MPC_LEAF(D) |
                                              +-------------^--+        +----------------+
                                                            |
                                             +--------------+----------+
                                             | 0x10 || c_2 || BUNDLE_2 |
                                             +-------------------------+
```
{% endcode %}

Therefore, the Merkle proof that verifies the existence and uniqueness of the contract commitment in the tree consists of `tH_MPC_LEAF(D)`, `tH_MPC_BRANCH(tHA || tHB)` and `tH_MPC_BRANCH(tHEF || tHGH)`. Together with `pos(c_2)` and `cofactor`, the three hashes allow the verifier to recompute the root of the tree and reproduce the MPC commitment, to compare with the one included in the [anchor](anchors.md).
