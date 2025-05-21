# Schema example: Non-Inflatable Assets

In this section, we will look more closely at an actual example of an RGB Contract Schema written in Rust and contained in the [nia.rs](https://github.com/RGB-WG/rgb-schemata/blob/master/src/nia.rs) file from the [RGB Schemata Repository](../../annexes/rgb-library-map.md#rgb-schemata). The Repository contains an example set of schema templates related to other types of contracts. This Schema, which we will be using as an example in this chapter, allows for the contract setup of N**on-Inflatable Assets** **(NIA)** that can be considered as the RGB analog to Ethereum's fungible tokens created with the ERC20 standard.

We can observe that a Schema can be divided into several general sections:

* A _header_ which contains:
  * &#x20;An optional Root `SchemaId` which indicates a limited form of inheritance from some master schema.&#x20;
  * A reserved `Feature` field which provides room for additional future extensions of contract schema.
* A first section in which all the **State Types** and related variables (both pertaining to [Global](../../rgb-state-and-operations/components-of-a-contract-operation.md#global-state) and [Assignments](../../rgb-state-and-operations/components-of-a-contract-operation.md#assignments)) are declared.
* A second section where all the possible [Contract Operations](../../annexes/glossary.md#contract-operation) referencing the previously declared State Types are encoded.
* A field containing the declaration of the **Strict Type System** being used in the whole schema.
* A last section containing the **validation scripts** for all the operations.

After this layout indication, we provide below the actual Rust Code of the schema. Each code section is provided with a numbered reference to an explanation paragraph reported below.

{% code fullWidth="true" %}
```rust
fn nia_schema() -> Schema { 

    // definitions of libraries and variables

    Schema {
        ffv: zero!(),                                                                            // --+
        name: tn!("NonInflatableAsset"),                                                         //   |  (1)
        meta_types: none!(),                                                                     // --+
        global_types: tiny_bmap! {                                                                       // --+
            GS_NOMINAL => GlobalDetails {                                                                //   |
                global_state_schema: GlobalStateSchema::once(types.get("RGBContract.AssetSpec")),        //   |
                name: fname!("spec"),                                                                    //   |
            },                                                                                           //   |
            GS_TERMS => GlobalDetails {                                                                  //   |
                global_state_schema: GlobalStateSchema::once(types.get("RGBContract.ContractTerms")),    //   |  (2)
                name: fname!("terms"),                                                                   //   |
            },                                                                                           //   |
            GS_ISSUED_SUPPLY => GlobalDetails {                                                          //   |
                global_state_schema: GlobalStateSchema::once(types.get("RGBContract.Amount")),           //   |
                name: fname!("issuedSupply"),                                                            //   |
            },                                                                                           //   |
        },                                                                                               // --+
        owned_types: tiny_bmap! {                                                             // --+
            OS_ASSET => AssignmentDetails {                                                   //   |
                owned_state_schema: OwnedStateSchema::Fungible(FungibleType::Unsigned64Bit),  //   |
                name: fname!("assetOwner"),                                                   //   |  (3)
                default_transition: TS_TRANSFER,                                              //   |
            }                                                                                 //   |
        },                                                                                    // --+
        genesis: GenesisSchema {                                                 //  --+ -------> Contract declaration start here
            metadata: none!(),                                                   //    |
            globals: tiny_bmap! {                                                //    |
                GS_NOMINAL => Occurrences::Once,                                 //    |
                GS_TERMS => Occurrences::Once,                                   //    |
                GS_ISSUED_SUPPLY => Occurrences::Once,                           //    |
            },                                                                   //    |   (4)
            assignments: tiny_bmap! {                                            //    |
                OS_ASSET => Occurrences::OnceOrMore,                             //    |
            },                                                                   //    |
            validator: Some(LibSite::with(FN_NIA_GENESIS_OFFSET, alu_id)),       //    |
        },                                                                       //  --+
        transitions: tiny_bmap! {
            TS_TRANSFER => TransitionDetails {                                   //  --+
                transition_schema: TransitionSchema {                            //    |
                    metadata: none!(),                                           //    |
                    globals: none!(),                                            //    |
                    inputs: tiny_bmap! {                                         //    |
                        OS_ASSET => Occurrences::OnceOrMore                      //    |
                    },                                                           //    |   (5)
                    assignments: tiny_bmap! {                                    //    |
                        OS_ASSET => Occurrences::OnceOrMore                      //    |
                    },                                                           //    |
                    validator: Some(LibSite::with(FN_NIA_TRANSFER_OFFSET, alu_id)//    |
                },                                                               //    |
                name: fname!("transfer"),                                        //    |
            }                                                                    //  --+
        },
        default_assignment: Some(OS_ASSET),               //  --+ (6)
    }
}
```
{% endcode %}

**(1)** In this section:

* &#x20;`ffv` statement indicates the version of the contract.
* `name` provides a human-readable identifier for the schema itself, although it provides no uniqueness guarantees

**(2)** In this section `global_state` and its variables are declared, in particular:

* The token's `GS_NOMINAL` set of specifications which according to the [Strict Type Library](../../annexes/rgb-library-map.md#strict-types-and-strict-encoding) contain: the token full `name` , the `ticker`, some additional `details`, the digit `precision` of the asset.
* `GS_TERMS` containing some additional contract `terms` such as a disclaimer.
* `GS_ISSUED_SUPPLY` which defines the initial supply of the token. In this case, since no inflation is allowed, it also represents the max supply.
* The `Once` statement guarantees that all these declarations are associated with a single value.

**(3)** In `owned_type` section, through the `OS_ASSET` statement, we can find the **StateType declaration** of the fungible token being transferred through the owned state assignment. The quantity of token used in the transfer is declared as a [Fungible Type](../../rgb-state-and-operations/components-of-a-contract-operation.md#owned-states) represented by a 64-bit unsigned integer. Additionally, we provide each assignment type with a default transition, which allows for instance to move it automatically to another seal when spending other allocations on the same UTXO.

**(4)** This section of the contract schema marks the beginning of **Contract Operations' declaration section.** Starting from the operation allowed within `genesis` :

* No `metadata` are declared.
* The instantiation, inside the Genesis state, of all the variables of the Global State variables previously defined in code section (2).&#x20;
* The declaration of the first `assignment(s)` of the token using the previously declared type `OS_ASSET`. Note that the `OnceOrMore` statement allows more than one allocation, in case the issuer wants to split the initial supply among multiple owners.

**(5)** The `transitions` section provides the declaration of a single `TS_TRANSFER` operation which:

* Contains no `metadata`.
* Doesn't update the global state (it was defined only in Genesis).
* Takes as `inputs` at **one or more** assignments of type `OS_ASSET`.
* Allows to declare **one or more** `assignments` of type `OS_ASSET`.
* Points to the `AluVM` script that should be **executed when validating** operations of this type.

**(6)** A **default assignment type** is defined, to be used for example to pay an invoice that doesn't specify one.
