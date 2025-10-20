# Tapret

The `Tapret` scheme is a more complex form of deterministic commitment and represents an improvement in terms of chain footprint and privacy of contract operations. The main idea of this application is to hide the commitment within the `Script Path Spend` of a [taproot transaction](https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki).

First, before describing how the commitment is actually embedded in a taproot transaction, we will show the exact **form of the commitment which must match exactly a 64-byte string size** [constructed](https://github.com/BP-WG/bp-core/blob/master/dbc/src/tapret/mod.rs#L179-L196) as follows:

```
64-byte_Tapret_Commitment =

 OP_RESERVED ...  ... .. OP_RESERVED   OP_RETURN   OP_PUSHBYTE_33  <mpc::Commitment>  <Nonce>
|___________________________________| |_________| |______________| |_______________|  |______|
 OP_RESERVED x 29 times = 29 bytes      1 byte         1 byte          32 bytes        1 byte
|________________________________________________________________| |_________________________|
        TAPRET_SCRIPT_COMMITMENT_PREFIX = 31 bytes                    MPC commitment + NONCE = 33 bytes
```

Thus the 64-byte `Tapret` commitment is an `Opret` commitment preceded by 29 bytes of the `OP_RESERVED` operator and to which is added a 1-byte `Nonce` whose usefulness will be addressed [later](tapret.md#nonce-optimization).

In order to preserve highest degree of implementation flexibility, privacy and scalability, **the Tapret scheme is designed to integrate many different cases that occur according to the user's bitcoin spending needs**. Specifically we distinguish the following Tapret scenarios:

* **Single incorporation** of a Tapret commitment into a taproot transaction **without a pre-existing Script Path Spend structure**.
* **Integration** of a Tapret commitment into a taproot transaction **containing a pre-existing Script Path Spend structure**.

We will analyze each of these scenarios in depth in the next paragraphs.

## **Tapret Incorporation without pre-existing Script Path Spend**

In this first scenario, we start with a Taproot Output Key `Q` consisting only of an Internal Key `P` and **no Spending script path**:

```
+---+            +---+   +---+   +---+
| Q |      =     | P | + | m | * | G |
+---+            +---+   +-^-+   +---+
                           |
                    +-------------+
                    | tH_TWEAK(P) |
                    +-------------+
```

* `P` is the Internal Public Key of the _Key Path Spend._
* `G` is the Generator point of [secp256k1](https://en.bitcoin.it/wiki/Secp256k1) elliptic curve.
* `t = tH_TWEAK(P)` = SHA-256(SHA-256(_TapTweak_) || SHA-256(_TapTweak_) || P) is the tweaking factor derived from the tagged hash representing the commitment to the public key `P`. The construction makes use of [BIP86](https://github.com/bitcoin/bips/blob/master/bip-0086.mediawiki#address-derivation) to show that there is no hidden alternative Script Path Spend.

In order to include the Tapret commitment, **the transaction is modified to include a Script Path Spend containing a single script** according to the following scheme:

```
+---+            +---+   +---+   +---+
| Q |      =     | P | + | t | * | G |
+---+            +---+   +-^-+   +---+
                           |
             +----------------------------+
             | tH_TWEAK(P || Script_root) |
             +---------------------^------+
                                   |
         +-------------------------+------------+
         | tH_BRANCH(64-byte_Tapret_Commitment) |
         +--------------------------------------+
```

* `t = tH_TWEAK(P || Script_root)` = SHA-256(SHA-256(_TapTweak_) || SHA-256(_TapTweak_) || P || Script\_root) is the modified tweaking factor.
* `Script_root = tH_BRANCH(`64-byte\_Tapret\_Commitment`)` = SHA256(SHA-256(_TapBranch_) || SHA-256(_TapBranch_) || 64-byte\_Tapret\_Commitment) is the script root of the Script Path Spend.&#x20;

The proof of inclusion and uniqueness in the Taproot Script Tree is only the internal key `P`.

## **Tapret incorporation in pre-existing Script Path Spend**

To move on to the construction of this more complex case, we show below the structure of a taproot output Key `Q`, which in this example consists of a Spend Key Path with internal key `P` and a 3-script tree in the Spend Script Path.

```
+---+            +---+   +---+   +---+
| Q |      =     | P | + | t | * | G |
+---+            +---+   +-^-+   +---+
                           |
             +----------------------------+
             | tH_TWEAK(P || Script_root) |
             +---------------------^------+
                                   |
                     +-------------+----------+
                     | tH_BRANCH(tHAB || tHC) |
                     +------------^-------^---+
                                  |       |
                        +---------+       +---------+
                        |                           |
           +------------+----------+         +------+-----+
           | tH_BRANCH(tHA || tHB) |         | tH_LEAF(C) |
           +------------^------^---+         +------^-----+
                        |      |                    |
                 +------+      +------+             |
                 |                    |             |
           +-----+------+       +-----+------+      |
           | tH_LEAF(A) |       | tH_LEAF(B) |      |
           +-----^------+       +-----^------+      |
                 |                    |             |
               +-+-+                +-+-+         +-+-+
               | A |                | B |         | C |
               +---+                +---+         +---+
```

Where:

* `tH_LEAF(x)` = SHA-256(SHA-256(_TapLeaf_) || SHA-256(_TapLeaf_) || version\_leaf(x) || size(x) || x) is the standard tagged hash of a script leaf in taproot Script Path Spend.
* `A, B, C` are some Bitcoin scripts of this example taproot script tree.

The RGB Tapret commitment rule imposes the following requirements:

**1) Tapret Commitment is entered as an unspendable script at the 1st level of the Script Tree, shifting all other scripts 1 level below.**&#x20;

The new Taproot Output Key `Q` including the Tapret commitment is built as follows:

```
+---+            +---+   +---+   +---+
| Q |      =     | P | + | t | * | G |
+---+            +---+   +-^-+   +---+
                           |
                           +--------------------+
                                                |
                                +---------------+------------+
                                | tH_TWEAK(P || Script_root) |
                                +---------------------^------+
                                                      |
                                       +--------------+----------+
                                       | tH_BRANCH(tHABC || tHT) |
                                       +-------------^-------^---+
                                                     |       |
                     +-------------------------------+       +-------+
                     |                                               |
          +----------+-------------+               +-----------------+--------------------+
          | tH_BRANCH(tHAB || tHC) |               | tH_BRANCH(64_byte_Tapret_Commitment) |
          +------------^-------^---+               +--------------------------------------+
                       |       |
             +---------+       +-----------+
             |                             |
+------------+----------+           +------+-----+
| tH_BRANCH(tHA || tHB) |           | tH_LEAF(C) |
+------------^------^---+           +------^-----+
             |      |                      |
      +------+      +------+               |
      |                    |               |
+-----+------+       +-----+------+        |
| tH_LEAF(A) |       | tH_LEAF(B) |        |
+-----^------+       +-----^------+        |
      |                    |               |
    +-+-+                +-+-+           +-+-+
    | A |                | B |           | C |
    +---+                +---+           +---+
```

**2)** According to Taproot rules, **every branch and leaf hashing operation is performed in lexicographic order of the two operands**.&#x20;

Therefore, **three cases** that lead to two different proofs of uniqueness of the commitment can occur.

**a)** If the hash of the Tapret commitment (`tHT`) **is greater** than the top-level hash of the Script Path Spend (`tHABC`), it will be put on **the right side of the Script Tree**. In this case, the commitment at this position is considered as a valid proof of uniqueness. The related Merkle Proof of inclusion and uniqueness consists of `tHABC` and `P` only, as shown in the diagram below.

<pre><code><strong>* tHABC &#x3C; tHT case
</strong>
+---+            +---+   +---+   +---+
| Q |      =     | P | + | t | * | G |
+---+            +---+   +-^-+   +---+
                           |
                           +--------------------+
                                                |
                                +---------------+------------+
                                | tH_TWEAK(P || Script_root) |
                                +---------------------^------+
                                                      |
                                       +--------------+----------+
                                       | tH_BRANCH(tHABC || tHT) |
                                       +-------------^-------^---+
                                                     |       |
                     +-------------------------------+       +-------+
                     |                                               |
          +----------+-------------+               +-----------------+--------------------+
          | tH_BRANCH(tHAB || tHC) |               | tH_BRANCH(64_byte_Tapret_Commitment) |
          +------------------------+               +--------------------------------------+
</code></pre>

**b)** If the hash of the tapret commitment (`tHT`) **is smaller** than the top-level hash of the Script Path Spend (`tHABC`), it will be placed on **the left side of the Script Tree**. In this case, it is necessary to show that there are no other Tapret commitments on the right side of the Tree. To do this, two cases must be taken into account:

**b1)** If the old root is a merkle node with two branches, `tHAB` and `tHC` must be revealed and form the Merkle proof of inclusion and uniqueness along with `P`, as shown in the diagram below:

```
* tHABC > tHT case (branch)

+---+            +---+   +---+   +---+
| Q |      =     | P | + | t | * | G |
+---+            +---+   +-^-+   +---+
                           |
                           +--------------------+
                                                |
                                +---------------+------------+
                                | tH_TWEAK(P || Script_root) |
                                +---------------------^------+
                                                      |
                                       +--------------+----------+
                                       | tH_BRANCH( tHT || tHABC)|
                                       +-------------^-------^---+
                                                     |       |
                                  +------------------+       +------------------+
                                  |                                             |
             +--------------------+-----------------+              +------------+-----------+
             | tH_BRANCH(64_byte_Tapret_Commitment) |              | tH_BRANCH(tHAB || tHC) |
             +--------------------------------------+              +------------^-------^---+
                                                                                |       |
                                                                   +------------+       +--------+
                                                                   |                             |
                                                      +------------+----------+           +------+-----+
                                                      | tH_BRANCH(tHA || tHB) |           | tH_LEAF(C) |
                                                      +-----------------------+           +------------+
```
*Note:* although the tapret commitment is the same length of two concatenated hashes (64
bytes), it's not possible to hide an alternative commitment by splitting it into two fake
subtree roots since the taproot hashing strategy (tag + encoded data) for branches is
different from the one for leaves. Therefore, no extra checks are required on the values
of `tHAB` and `tHC`.

**b2)** If the old root is itself a leaf node, then the leaf content must be revealed and form the Merkle proof of inclusion and uniqueness along with `P`, as shown in the diagram below:

```
* tHABC > tHT case (leaf)

+---+            +---+   +---+   +---+
| Q |      =     | P | + | t | * | G |
+---+            +---+   +-^-+   +---+
                           |
                           +--------------------+
                                                |
                                +---------------+------------+
                                | tH_TWEAK(P || Script_root) |
                                +---------------------^------+
                                                      |
                                       +--------------+----------+
                                       | tH_BRANCH( tHT || tHC)|
                                       +-------------^-------^---+
                                                     |       |
                                  +------------------+       +------------------+
                                  |                                             |
             +--------------------+-----------------+                    +------+-----+
             | tH_BRANCH(64_byte_Tapret_Commitment) |                    | tH_LEAF(C) |
             +--------------------------------------+                    +------------+
```


## **Nonce optimization**

The above construction is clearly more complex and the proof is larger when the tapret commitment lies in the
left side of the tree, since more details on the rest of the taproot tree need to be revealed.
In particular, in the **b2** scenario, in case `tH_LEAF(C)` contains
spending conditions that should remain private, one may want to hide it by adding a
dummy leaf that turns this into a **b1** case. However, this would make such spending
conditions more expensive to spend onchain, leading to a privacy vs cost tradeoff.

To avoid this complexity, the `<Nonce>` encoded in the last byte of the
`64_byte_Tapret_Commitment` allows the prover to attempt at "mining" a `tHT` such that
`tHABC < tHT`, thus placing it in the right-hand side of the tree and definitely
avoiding revealing the constituents of the script branch (in this example: either
`tHAB || tHC` or `tH_LEAF(C)`).
***
