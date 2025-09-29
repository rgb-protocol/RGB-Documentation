# List of supported Schemas

This section lists the schemas that have been officially implemented so far, describing the data
they work with and the list of supported operations.

## NIA (Non Inflatable Asset)

This schema defines a non-inflatable fungible asset, involving the following data:
- AssetSpec: groups basic asset information, namely:
    - Ticker: short identifier of the asset, to be displayed on wallets and exchanges
    (e.g.: BTC, USDT, ...). Note that there is no guarantee of uniqueness
    - Name: extended name of the asset (e.g.: Bitcoin, Tether, ...)
    - Details: optional string describing the asset in more detail
    - Precision: Number of decimal places of the standard representation of the asset (e.g.
    would be 8 for BTC and 2 for USD)
- Contract Terms: contains a string describing the contract and an optional media
    attachment
- Issued Supply: total amount of tokens created at issuance. Since the asset is not
    inflatable, it also serves as an upper bound on the circulating supply

The following operations are supported for the asset:
- Transfer: send some amount of assets to a number of destinations (optionally including
    change); it supports multiple inputs in case multiple allocations should be merged in
    order to build up the desired output amount

## UDA (Unique Digital Asset)

This schema defines a unique non-fungible asset (NFT), involving the following data:
- AssetSpec: groups basic asset information, namely:
    - Ticker: short identifier of the asset, to be displayed on wallets and exchanges. Note
    that there is no guarantee of uniqueness
    - Name: extended name of the asset
    - Details: optional string describing the asset in more detail
    - Precision: Number of decimal places of the standard representation of the asset
- Contract Terms: contains a string describing the contract and an optional media
    attachment
- EmbeddedMedia: a media type associated with a binary blob (max. ~64KiB),
    can be used to embed some media (e.g. a small image) into the contract
- Attachments: a list of media types associated with a hash digest,
    can be used to attach some large media (e.g. videos or HD images), without including
    them in the contract as a whole. The data itself should be made available by other means,
    while its digest can be checked against the one in the contract
- ProofOfReserves: a bitcoin outpoint paired with a binary proof, can be used to show
    that some tokens are locked as a reserve for the UDA asset

The following operations are supported for the asset:
- Transfer: send the assets to a destination.

## CFA (Collectible Fungible Asset)

This schema defines a collectible fungible asset. It is similar to NIA, with an
additional string (Article) that represents the collectible.

The following operations are supported for the asset:
- Transfer: send some amount of assets to a number of destinations (optionally including
    change); it supports multiple inputs in case multiple allocations should be merged in
    order to build up the desired output amount.

## IFA (Inflatable Fungible Asset)

This schema defines a non-inflatable fungible asset, involving the following data:
- AssetSpec: groups basic asset information, namely:
    - Ticker: short identifier of the asset, to be displayed on wallets and exchanges
    (e.g.: BTC, USDT, ...). Note that there is no guarantee of uniqueness
    - Name: extended name of the asset (e.g.: Bitcoin, Tether, ...)
    - Details: optional string describing the asset in more detail
    - Precision: Number of decimal places of the standard representation of the asset (e.g.
    would be 8 for BTC and 2 for USD)
- Contract Terms: contains a string describing the contract and an optional media
    attachment
- Issued Supply: amount of issued tokens in a certain operation, which can be either
    Genesis or an Inflation Transition. It represents the amount of the initial issuance and of each
    secondary issuance, respectively
- Total Supply: the sum of the issued supply and the allowed inflation amount.
    It serves as an upper bound on the circulating supply, which can be more closely
    estimated through other means
- RejectListUrl: an optional URL where the issuer can provide a list of operations that
    should be considered invalid. This cannot be enforced by the issuer due to the nature
    of client side validation, and wallets are free to ignore it


Additionally to the owned state representing the asset's allocation, an IFA asset can
optionally define two rights:
- Inflation: represents the right to inflate the asset by a certain amount, using this
    right will reduce the remaining inflation amount
- Replace: represents the right to "stamp" an allocation, so that wallets trusting the
    replace right owners can avoid validating the history from this operation back to
    genesis. It's always possible, provided that the CSV data is available, to perform
    full trustless validation

The following operations are supported for the asset:
- Transfer: send some amount of assets to a number of destinations (optionally including
    change); it supports multiple inputs in case multiple allocations should be merged in
    order to build up the desired output amount
- Inflate: use an inflation right to issue a certain amount of assets in circulation,
    which can be optionally split into more than one allocation. The remaining inflation
    right (if any) can also optionally be split into more than one allocation
- Replace: use a replace right to certify that the history of a set of allocations back
    to genesis is valid. This "stamp" can be used by wallets to skip part of the
    consignment validation, provided that they trust the issuer (or their delegates for
    replace operations)
- Burn: burn a number of (asset or right) allocations by adding them as input to a
    transition with no outputs. It allows to prove to a third party that those
    allocations no longer exist, e.g. as part of a protocol with wider scope

## PFA (Permissioned Fungible Asset)

This schema defines a permissioned, non-inflatable fungible asset, in which the issuer
needs to explicitly authrize every transfer; e.g. it may be used to represent company shares,
for which there are legal constraints on the potential owners. It involves the following data:
- AssetSpec: groups basic asset information, namely:
    - Ticker: short identifier of the asset, to be displayed on wallets and exchanges.
    Note that there is no guarantee of uniqueness
    - Name: extended name of the asset
    - Details: optional string describing the asset in more detail
    - Precision: Number of decimal places of the standard representation of the asset
- Contract Terms: contains a string describing the contract and an optional media
    attachment
- Issued Supply: total amount of tokens created at issuance. Since the asset is not
    inflatable, it also serves as an upper bound on the circulating supply
- Pubkey: public key identifying the entity that needs to sign every transfer

The following operations are supported for the asset:
- Transfer: send some amount of assets to a number of destinations (optionally including
    change); it supports multiple inputs in case multiple allocations should be merged in
    order to build up the desired output amount and it must have a metadata containing the
    issuer's signature, which is checked by the receiving wallet using the Pubkey in Genesis

---

In the next subsection, we will provide an example of an actual Schema used for the
issuance of a **Non Inflatable Asset.**
