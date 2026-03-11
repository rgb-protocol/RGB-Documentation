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

This schema defines an inflatable fungible asset, involving the following data:
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
- LinkedFromContract, LinkedToContract: optional `ContractId`s that should be considered
    equivalent economic objects as the current asset, may be used by the issuer to update
    an asset to a different schema or a different version of the IFA schema. The contract link
    from `A` to `B` should only be considered valid if `A.LinkedToContract` is `B`
    AND `B.LinkedFromContract` is `A`; this guarantees that the issuers of both assets
    are willing to consider them the same economic structure

Additionally to the owned state representing the asset's allocation, an IFA asset can
optionally define rights:
- Inflation: allows its owner to inflate the asset by a certain amount, using this right
    will reduce the remaining inflatable amount
- Link: allows its owner to link the current asset to another one, by setting a value to
    the `LinkedToContract` global state

The following operations are supported for the asset:
- Transfer: send some amount of assets to a number of destinations (optionally including
    change); it supports multiple inputs in case multiple allocations should be merged in
    order to build up the desired output amount
- Inflate: use an inflation right to issue a certain amount of assets in circulation,
    which can be optionally split into more than one allocation. The remaining inflation
    right (if any) can also optionally be split into more than one allocation
- Burn: burn (asset or right) allocations by adding them as input to a burn transition.
    Fungible allocations can be burned partially by adding change outputs; the burned
    amount must be non-zero and must be declared in a metadata, which can be used as
    source of truth. Non-fungible allocations must be burned in full, so they have no
    output.

    This transition allows to prove to a third party that some right or a certain amount
    of assets no longer exists, e.g. as part of a protocol with wider scope
- Link: Link this asset to another linkable one. This operation can be done at most once
    in the life of a contract, hence the corresponding right is lost after this operation
    is performed

## PFA (Permissioned Fungible Asset)

This schema defines a permissioned, non-inflatable fungible asset, in which the issuer
needs to explicitly authorize every transfer; e.g. it may be used to represent company shares,
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
