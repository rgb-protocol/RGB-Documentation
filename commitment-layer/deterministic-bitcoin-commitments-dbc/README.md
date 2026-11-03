# Deterministic Bitcoin Commitments - DBC

To perform RGB commitment operations, the main requirement for a Bitcoin commitment scheme to be valid is the following:

> The witness transaction must provably contain a single commitment.

Due to this requirement, it is not possible to construct an "alternative history" of the client-side data committed to the same transaction. Thus, the message which the single-use seal encloses is unique. To meet the above requirement, regardless of the number of outputs in a transaction, a valid commitment (either Opret or Tapret) must be contained in _one and only one output_:

> The only valid output that can contain an RGB message commitment is the first DBC-compatible output, i.e. the first that either has:
> 1. an OP\_RETURN output; in this case the Opret commitment will be encoded inside it
> 2. a Taproot output; in this case the Tapret commitment will be encoded in the corresponding Taproot tree

It is worth observing that a transaction has to **only contain either a single** `Opret` **OR a single** `Tapret` commitment in the first applicable output. This approach guarantees that the seal closing strategy is always unique, no matter how the seal was created in the first place. As a consequence, if a witness transaction contained both a Taproot and an OP\_RETURN output, the second one would be ignored by the RGB validation process.

***
