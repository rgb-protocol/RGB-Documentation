# Multi Protocol Commitments - MPC

Multi Protocol Commitments address the following important requirements:

1. How the tagged `mpc::Commitment` hash, committed in Bitcoin Blockchain according to `Opret` or `Tapret` schemes, is constructed.
2. How state changes associated with more than one contract can be stored in a single commitment.

The preceding points are addressed through an **ordered merkelization** of the multiple contracts (actually their [transition bundles](../annexes/glossary.md#transition-bundle) IDs) in an [MPC](../annexes/glossary.md#multi-protocol-commitment-mpc) Tree whose properties will be addressed in depth in this section. Eventually, the root of the tree (`mpc::Root`) is hashed once more to get the `mpc:Commitment` which is finally committed in an output of the [witness transaction](../annexes/glossary.md#witness-transaction) using the appropriate [Deterministic Bitcoin Commitment](../annexes/glossary.md#deterministic-bitcoin-commitment-dbc) construction.

<figure><img src="../.gitbook/assets/immagine (1).png" alt=""><figcaption><p><strong>Each RGB contract has a unique position in the MPC Tree determined by a modular division applied to its ContractId according to the width of the tree. In this example, the MPC tree has a width of 8.</strong> </p></figcaption></figure>

## MPC Root Hash

The commitment of the MPC tree - which goes either into [Opret](deterministic-bitcoin-commitments-dbc/opret.md) or into [Tapret](deterministic-bitcoin-commitments-dbc/tapret.md) commitments - is the `mpc::Commitment` constructed in BIP-341 fashion as follows:

`mpc::Commitment = SHA-256(SHA-256(mpc_tag) || SHA-256(mpc_tag) || depth || cofactor || mpc::Root )`

Where:

* `mpc_tag = urn:ubideco:mpc:commitment#2024-01-31` follows[ RGB tagging conventions](https://github.com/RGB-WG/rgb-core/blob/master/doc/Commitments.md).
* `depth` is the depth of the tree as a single byte
* `cofactor` is the value used to obtain distinct positions for the contracts in the tree as a 16-bit Little Endian unsigned integer (see [MPC Tree Construction](#mpc-tree-construction))
* `mpc::Root` is the root of the MPC tree whose construction is explained in the following paragraphs.

## MPC Tree Construction

In order to construct the MPC tree we must **deterministically find a unique leaf position for each contract**, thus:

By setting `C` the number of contracts and `i = {0,1,..,C-1}` and by having a `ContractId(i) = c_i` to be included in the MPC, we can construct a tree with `w` leaves with `w > C` (corresponding to a depth `d` such that `2^d = w`), so that each contract identifier `c_i` representing a different contract is placed in a unique position `pos(c_i)` determined as a modulus operation detailed below.

In essence, the construction of a suitable tree of width `w` that hosts each contract `c_i` in a unique position represents a kind of mining process. The greater the number of contract `C`, the greater should be the number of leaves `w`. Assuming a random distribution of `pos(c_i)`, as per [Birthday Paradox](https://en.wikipedia.org/wiki/Birthday\_problem), we have \~50% probability of a collision occurring in a tree with `w ~ C^2`.

In order to avoid too large MPC trees and assuming that the occurrence of collisions is a random process, an additional optimization has been introduced.

The actual formula for determining the **leaf position of the contract** is:

    pos(c_i) = c_i mod (w - cofactor)

Where `cofactor` is a number that allows to increase the chance of deterministically obtaining distinct values of `pos(c_i)` with a given `w`.

The tree construction process starts from the smallest tree such that `w > C`[^min_depth] and performing a certain number of `cofactor` attempts; if none of them can produce `C` distinct positions, `d` is incremented by one and a new series of `cofactor` trials is attempted. In particular, `cofactor` is chosen starting from `0` and trying every number up to `w/2`[^cofactor_attempts]: larger values cannot succeed since otherwise it would have been possible to build a tree of depth `d-1`.

[^min_depth]: Minimum depth is actually set to 3 to avoid leaking the exact number of contracts in the tree.
[^cofactor_attempts]: `cofactor` is actually capped at 500 for performance reasons since, as it grows, it becomes less and less likely to succeed in producing distinct positions.

### **Contract Leaves (Inhabited)**

Once `C` distinct positions `pos(c_i)` with `i = 0,...,C-1` are found, the corresponding leaves are populated through a tagged hash constructed in the following way:

`tH_MPC_LEAF(c_i) = SHA-256(SHA-256(merkle_tag) || SHA-256(merkle_tag) || 0x10 || c_i || BundleId(c_i))`

Where:

* `merkle_tag = urn:ubideco:merkle:node#2024-01-31` is chosen according to [RGB conventions on Merkle Tree tagging commitments](https://github.com/RGB-WG/rgb-core/blob/master/doc/Commitments.md#merklization-procedure).
* `0x10` is the integer identifier of contract leaves.
* `c_i` is the 32-byte contract\_id which is derived from the hash of the [Genesis](../rgb-state-and-operations/state-transitions.md#genesis) of the contract itself.
* `BundleId(c_i)` is the 32-byte hash that is calculated from the data of the [Transition Bundle](../rgb-state-and-operations/state-transitions.md#transition-bundle) which groups all the [State Transitions](../annexes/glossary.md#state-transition) of the contract `c_i`.

### **Entropy leaves (Uninhabited)**

For the remaining `w - C` uninhabited leaves, a dummy value must be committed. To do that, each leaf in position `j != pos(c_i)` is populated in the following way:

`tH_MPC_LEAF(j) = SHA-256(SHA-256(merkle_tag) || SHA-256(merkle_tag) || 0x11 || entropy || j )`

Where:

* `merkle_tag = urn:ubideco:merkle:node#2024-01-31` is chosen according to [RGB conventions on Merkle Tree tagging commitments](https://github.com/RGB-WG/rgb-core/blob/master/doc/Commitments.md#merklization-procedure).
* `0x11` is the integer identifier of entropy leaves.
* `entropy` is a 64-byte random value chosen by the user constructing the tree.
* `j` is the position of the current leaf as a 32-bit Little Endian unsigned integer.

### MPC nodes

After generating the base of the MPC tree having `w` leaves, merkelization is performed following the rule of `commit_verify` crate detailed [here](https://github.com/RGB-WG/rgb-core/blob/vesper/doc/Commitments.md#merklization-procedure).

The hash for non-leaf nodes in the tree is computed as:

`tH_MPC_BRANCH(tH1 || tH2) = SHA-256(SHA-256(merkle_tag) || SHA-256(merkle_tag) || b || d || w || tH1 || tH2)`

Where:
* `merkle_tag = urn:ubideco:merkle:node#2024-01-31` is chosen according to [RGB conventions on Merkle Tree tagging commitments](https://github.com/RGB-WG/rgb-core/blob/master/doc/Commitments.md#merklization-procedure).
* `b` is the branching of the tree merkelization scheme, i.e. the number of children the current node has, encoded as a 8-bit unsigned integer. If the tree is complete, this is always `0x02`.
* `d` is the node depth within the tree (i.e. the length of the path to the root), encoded as an 8-bit unsigned integer.
* `w` is the tree width, encoded as a 256-bit Little Endian unsigned integer.
* `tH1` and `tH2` are respectively the hash of the left and the right child, calculated according to the appropriate formula depending on their role in the tree (contract leaf, entropy leaf or merkle node).

The following diagram shows the construction of an example MPC tree, where:

* `C = 3` number of contracts to place.
* As an example: `pos(c_0) = 7, pos(c_1) = 4, pos(c_2) = 2`.
* `BUNDLE_i = BundleId(c_i)`.
* `d` depends on the position of the node within the tree; for example, `tH_MPC_BRANCH(tHA || tHB)` has `d=2`.
* `w=8` for every node in the tree.

{% code fullWidth="true" %}
```
                                                                                   +--------------------------+
                                                                   mpc:Root        | th_MPC(tHABCD || tHEFGH) |
                                                                                   +-----------^---------^----+
                                                                                               |         |
                                              +------------------------------------------------+         +--------------------------------------------+
                                              |                                                                                                       |
                                +-------------+---------------+                                                                         +-------------+---------------+
                                | tH_MPC_BRANCH(tHAB || tHCD) |                                                                         | tH_MPC_BRANCH(tHEF || tHGH) |
                                +----------------^--------^---+                                                                         +-----------------+--------+--+
                                                 |        |                                                                                               |        |
                     +---------------------------+        +--------------+                                                   +------------------<---------+        +------------+
                     |                                                   |                                                   |                                                  |
       +-------------+-------------+                       +-------------+-------------+                       +-------------+-------------+                      +-------------+-------------+
       | tH_MPC_BRANCH(tHA || tHB) |                       | tH_MPC_BRANCH(tHC || tHD) |                       | tH_MPC_BRANCH(tHE || tHF) |                      | tH_MPC_BRANCH(tHG || tHH) |
       +----------------^------^---+                       +----------------^------^---+                       +----------------^------^---+                      +----------------^------^---+
                        |      |                                            |      |                                            |      |                                           |      |
         +--------------+      +-----+                       +--------------+      +- ---+                       +--------------+      + ----+                      +--------------+      +-----+
         |                           |                       |                           |                       |                           |                      |                           |
 +-------+--------+        +---------+------+        +-------+--------+        +---------+------+        +-------+--------+        +---------+------+        +------+---------+        +--------+-------+
 | tH_MPC_LEAF(A) |        | tH_MPC_LEAF(B) |        | tH_MPC_LEAF(C) |        | tH_MPC_LEAF(D) |        | tH_MPC_LEAF(E) |        | tH_MPC_LEAF(F) |        | tH_MPC_LEAF(G) |        | tH_MPC_LEAF(H) |
 +-------------^--+        +-------------^--+        +-------------^--+        +-------------^--+        +-------------^--+        +-------------^--+        +-------------^--+        +-------------^--+
               |                         |                         |                         |                         |                         |                         |                         | 
+--------------+-------+  +--------------+-------+  +--------------+----------+  +-----------+---------+  +------------+------------+  +---------+------------+  +---------+------------+  +---------+---------------+ 
| 0x11 || entropy || 0 |  | 0x11 || entropy || 1 |  | 0x10 || c_2 || BUNDLE_2 |  | 0x11 | entropy || 3 |  | 0x10 || c_1 || BUNDLE_1 |  | 0x11 || entropy || 5 |  | 0x11 || entropy || 6 |  | 0x10 || c_0 || BUNDLE_0 | 
+----------------------+  +----------------------+  +-------------------------+  +---------------------+  +-------------------------+  +----------------------+  +----------------------+  +-------------------------+
```
{% endcode %}

### MPC Tree Verification

From a verifier's perspective, in order to prove the presence of client-side validated data related to some contract `c_i` collected in `BUNDLE_i`, **only a Merkle Proof pointing at it inside the tree is needed**. Because of this, different verifiers of different contracts don't need to have the full view of the Merkle Tree as the builder does, and this, together with the dummy entropy leaves, provides a high degree of privacy. Using the example tree in the diagram above, a verifier of, say, the contract `c_2` will receive the following _Merkle Proof_ from the tree builder:

{% code fullWidth="true" %}
```
                                                                            +-------------------------------+
                                                                            | tH_MPC_ROOT(tHABCD || tHEFGH) |
                                                                            +----------------^---------^----+
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
                                                      +--------------+      +- ---+
                                                      |                           |
                                              +-------+--------+        +---------+------+
                                              | tH_MPC_LEAF(C) |        | tH_MPC_LEAF(D) |
                                              +-------------^--+        +-------------^--+
                                                            |                          
                                             +-------------------------+                                                                                                                                    
                                             | 0x10 || c_2 || BUNDLE_2 |                                                                                                                                    
                                             +-------------------------+                                                                                                                                    
```
{% endcode %}

So the Merkle Proof provided to verify the existence and uniqueness of contract commitment in the tree is: `tH_MPC_LEAF(D)`, `tH_MPC_BRANCH(tHA || tHB)` and `tH_MPC_BRANCH(tHEF || tHGH)`. These are enough to recompute the tree root and, together with `pos(c_2)` and `cofacor`, reproduce the MPC commitment to be compared with the one included in the anchor.

### Reference implementation

A python reference implementation for MPC tree construction and verification can be found [here](https://github.com/RGB-Tools/RGB-Documentation/tree/master/reference-implementations/mpc.py).
