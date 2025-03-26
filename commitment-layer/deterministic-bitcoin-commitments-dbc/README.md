# Deterministic Bitcoin Commitments - DBC

For RGB commitment operations, the main requirement for a Bitcoin commitment scheme to be valid is that:

> The witness transaction must provably contain a single commitment.

With this requirement, it is not possible to construct an "alternative history" related to client-side data commitment in the same transaction. Thus, the message around which the single-use seal is closed is unique. To meet the above requirement, regardless of the number of outputs in a transaction, _one and only one output_ contains a valid commitment (either Opret or Tapret):

> The only valid output that can contain an RGB message commitment is the first output that has either:
> 1. an OP\_RETURN spending script; in this case it will encode its Opret commitment there
> 2. a taproot spending script; in this case it will encode its Tapret commitment in the corresponding taproot tree

It is worth observing that a transaction **only contains either a single** `Opret` **OR a single** `Tapret` commitment in the first applicable output. This approach guarantees uniqueness of the seal closing strategy without committing to it at seal creation, allowing to avoid the complexity of transfers involfing multiple commitment schemes. This means that, in case a witness transaction contains both a taproot and an OP\_RETURN output, the second one will be ignored by the RGB validation.

***
