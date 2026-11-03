# Tapret

The `Tapret` scheme is a more complex form of deterministic commitment and represents an improvement in terms of on-chain footprint and privacy of contract operations. The main idea of this approach is to hide the commitment within the `Script Path Spend` of a [Taproot transaction](https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki).

First, before describing how the commitment is actually embedded in a Taproot transaction, we will show the exact **structure of the commitment, a 64-byte string** [constructed](https://github.com/rgb-protocol/rgb-consensus/blob/44e79963aa4603270eee9aa112ef07a512345e98/src/dbc/tapret/tapscript.rs#L35C1-L51C2) as follows:

```
64-byte_Tapret_Commitment =

 OP_RESERVED ...  ... .. OP_RESERVED   OP_RETURN   OP_PUSHBYTES_33 <mpc::Commitment>  <Nonce>
|___________________________________| |_________| |______________| |_______________|  |______|
 OP_RESERVED x 29 times = 29 bytes      1 byte         1 byte          32 bytes        1 byte
|________________________________________________________________| |_________________________|
        TAPRET_SCRIPT_COMMITMENT_PREFIX = 31 bytes                    MPC commitment + NONCE = 33 bytes
```

Thus, the 64-byte `Tapret` commitment is an `Opret` commitment preceded by the 29 bytes of the `OP_RESERVED` operator, and the 1-byte `Nonce` (we will explain why it's used [later](tapret.md#nonce-optimization)).

In order to preserve the highest degree of implementation flexibility, privacy and scalability, **the Tapret scheme is designed to adapt to various cases in accordance with the user's bitcoin spending needs**. Specifically, we can distinguish the following Tapret scenarios:

* The **single incorporation** of a Tapret commitment into a Taproot transaction **without a pre-existing Script Path Spend structure**.
* The **integration** of a Tapret commitment into a Taproot transaction **containing a pre-existing Script Path Spend structure**.

We will analyze each of these scenarios in depth in the next paragraphs.

## **Tapret Incorporation without a pre-existing Script Path Spend**

In this first scenario, we can start describing a Taproot Output Key `Q` consisting only of an Internal Key `P` and **no Script Path Spend**:

```
+---+            +---+   +---+   +---+
| Q |      =     | P | + | t | * | G |
+---+            +---+   +-^-+   +---+
                           |
                    +-------------+
                    | tH_TWEAK(P) |
                    +-------------+
```

* `P` is the Internal Public Key of the _Key Path Spend._
* `G` is the Generator point of [secp256k1](https://en.bitcoin.it/wiki/Secp256k1) elliptic curve.
* `t = tH_TWEAK(P)` = SHA-256(SHA-256(_TapTweak_) || SHA-256(_TapTweak_) || P) is the tweaking factor derived from the tagged hash representing the commitment to the public key `P`. The construction uses [BIP86](https://github.com/bitcoin/bips/blob/master/bip-0086.mediawiki#address-derivation) to show that there is no hidden alternative Script Path Spend.

In order to include the Tapret commitment, **the transaction is modified to include a Script Path Spend containing a single script**, according to the following scheme:

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
         |  tH_LEAF(64-byte_Tapret_Commitment)  |
         +--------------------------------------+
```

* `t = tH_TWEAK(P || Script_root)` = SHA-256(SHA-256(_TapTweak_) || SHA-256(_TapTweak_) || P || Script\_root) is the modified tweaking factor.
* `Script_root = tH_LEAF(`64-byte\_Tapret\_Commitment`)` = SHA-256(SHA-256(_TapLeaf_) || SHA-256(_TapLeaf_) || version\_leaf(64-byte\_Tapret\_Commitment) || size(64-byte\_Tapret\_Commitment) || 64-byte\_Tapret\_Commitment) is the script root of the Script Path Spend.

The proof of inclusion and uniqueness in the Taproot Script Tree is simply the internal key `P`.

## **Tapret incorporation in a pre-existing Script Path Spend**

To analyze the construction of this more complex case, here below we are representing the structure of a Taproot output Key `Q`: in this example, it consists of a Key Path Spend with an internal key `P` and a 3-script tree in the Script Path Spend.

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

* `tH_LEAF(x)` = SHA-256(SHA-256(_TapLeaf_) || SHA-256(_TapLeaf_) || version\_leaf(x) || size(x) || x) is the standard tagged hash of a script leaf in a Taproot Script Path Spend.
* `A, B, C` are some Bitcoin scripts in the Taproot script tree of this example.

The RGB Tapret commitment rule imposes the following requirements:

**1) The Tapret commitment is inserted as an unspendable script at the first level of the Script Tree, shifting all other scripts down one level.**

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
          | tH_BRANCH(tHAB || tHC) |               |  tH_LEAF(64-byte_Tapret_Commitment)  |
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

**2)** According to Taproot rules, **every branch hashing operation is performed in lexicographic order of the two operands**.

Therefore, **three cases** can occur, resulting in two different proofs of uniqueness of the commitment.

**a)** If the hash of the Tapret commitment (`tHT`) **is greater** than the top-level hash of the Script Path Spend (`tHABC`), it will be placed on **the right side of the Script Tree**. In this case, the commitment is accepted as unique without further verification of the left-hand subtree. The related Merkle proof of inclusion and uniqueness consists of `tHABC` and `P` only, as shown in the diagram below.

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
          | tH_BRANCH(tHAB || tHC) |               |  tH_LEAF(64-byte_Tapret_Commitment)  |
          +------------------------+               +--------------------------------------+
</code></pre>

**b)** If the hash of the Tapret commitment (`tHT`) **is smaller** than the top-level hash of the Script Path Spend (`tHABC`), it will be placed on **the left side of the Script Tree**. In this case, it is necessary to show that there are no other Tapret commitments on the right side of the Tree. To do this, two cases must be taken into account:

**b1)** If the old root is itself a Merkle branch node, `tHAB` and `tHC` must be revealed and form the Merkle proof of inclusion and uniqueness along with `P`, as shown in the diagram below:

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
             |  tH_LEAF(64-byte_Tapret_Commitment)  |              | tH_BRANCH(tHAB || tHC) |
             +--------------------------------------+              +------------^-------^---+
                                                                                |       |
                                                                   +------------+       +--------+
                                                                   |                             |
                                                      +------------+----------+           +------+-----+
                                                      | tH_BRANCH(tHA || tHB) |           | tH_LEAF(C) |
                                                      +-----------------------+           +------------+
```
*Note:* although the Tapret commitment is the same length as two concatenated hashes (32+32 = 64 bytes), it cannot be split into two fake subtree roots and hidden as an alternative commitment. The reason is that branches and leaves use different tags in their hashing schemes. Therefore, no extra checks are required on the values of `tHAB` and `tHC`.

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
             |  tH_LEAF(64-byte_Tapret_Commitment)  |                    | tH_LEAF(C) |
             +--------------------------------------+                    +------------+
```


## **Nonce optimization**

When the commitment is on the left side of the tree, the construction is clearly more complex. Besides, the proof is larger, since more details on the rest of the Taproot tree need to be revealed.

In the **b2** scenario in particular, if `tH_LEAF(C)` contains spending conditions that should remain private, one may want to hide them by adding a dummy leaf that turns the tree into a **b1** case. However, this workaround would make spending under those conditions more expensive on-chain, leading to a privacy-versus-cost tradeoff.

To avoid this complexity, the `<Nonce>` encoded in the last byte of the `64-byte_Tapret_Commitment` allows the prover to attempt to "mine" a `tHT` such that `tHT > tHABC`, thus placing it on the right-hand side of the tree and avoiding the need to reveal the constituents of the script branch altogether (in this example: either `tHAB || tHC` or `tH_LEAF(C)`).
***
