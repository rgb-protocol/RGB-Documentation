# Schema

An RGB Schema represents a template that can be used to issue contracts having a common structure, embedding the rules of [contract operations](../../annexes/glossary.md#contract-operation) representing its [business logic](../../annexes/glossary.md#business-logic) and thus describing how its [state](../../annexes/glossary.md#contract-state) can be updated. Each contract implementing a schema assigns concrete values to contract fields in its Genesis, defining global state and initial owners for the newly created owned state.

An RGB Schema is the analog of a class for an OOP language. Hence such a construction is used to define the various standards for RGB contracts and assets, for example: fungible assets, collectibles, digital identities, etc.

The [issuer](../../annexes/glossary.md#contract-participant) of an asset on RGB uses (and makes available to the public) a Schema in order to define the issuance properties encoded in the Genesis. This way, the contract can be supported by RGB wallets and become fully operational. Thus, **when the users receive some information about an asset on RGB (data and contract) they must validate them against the Schema distributed by the issuer of that asset.**

In fact, the Schema validation is the very first operation step that a user needs to undergo before interacting in any way with the contract (e.g. to perform the desired contract operations).

From a functional point of view, the **Schema construct addresses the following questions**:

* What kinds of owned states and [Assignments](../../annexes/glossary.md#assignment) exist?
* What [Global State](../../rgb-state-and-operations/components-of-a-contract-operation.md#global-state) does the contract have?
* How is [Genesis](../../annexes/glossary.md#genesis) structured?
* What kind of [State Transitions](../../annexes/glossary.md#state-transition) are possible?
* What [Metadata](../../rgb-state-and-operations/components-of-a-contract-operation.md#metadata) can contract operations have?
* How state data are allowed to change within state transitions?
* What sequences of transitions are allowed?

<figure><img src="../../.gitbook/assets/schema-components (2).png" alt=""><figcaption><p><strong>Elements contained in an RGB Schema</strong></p></figcaption></figure>

**From a technical point of view, an RGB Schema is a functional declarative document that need to be compiled for effective usage inside RGB applications and wallets.**

Among the most important properties, a Schema:

* Defines all the variables used in contract state and transitions using a specific
  [strict type system](https://www.strict-types.org/) encoding. Such variables,
  depending on their scope, may be of different types:
  * Metadata: related to a single operation
  * Owned state: created by an operation and consumed by a second one
  * Global state: created by an operation, which it shares the visibility of
* Defines all the data structures required for Genesis operation, which represents the first instantiation of the contract.
* Defines a list of supported contract Transitions; for each of them:
  * Describes what data types it works with: owned state in input/output and global state/metadata it optionally defines
  * Embeds the **state validation script** and the related functions for the client-side part of RGB.
  The scripts, which executed through the [AluVM](../../annexes/glossary.md#aluvm) engine,
  represent the most fundamental component of the business logic.

**Schema architecture appears to be very different from blockchain-based contracts**, for example those implemented on Ethereum. Indeed, in these systems **the contract itself is provided as executable code** that defines the rules for changing and implementing the state which is eventually directly stored into the blockchain. **In contrast, in RGB the contract is encoded in a purely declarative way.**

In every Contract Operation performed in the client-side validation phase, the Contract Schema is always referenced and checked against. In particular, after compilation, the Schema can provide all the necessary data structure to perform the issuance of the contract represented by the Genesis Operation.

As [mentioned earlier](../../rgb-state-and-operations/features-of-rgb-state.md#the-validation-ownership-paradigm-in-rgb), **Schema clearly differentiates contract developers from issuers**, who may know nothing about coding and programming. This kind of approach makes extensive use of **contract templates** which can be used promptly by issuers who may benefit from avoiding common programming mistakes in the implementation phase.

After compilation, the Schema is encoded in a `.rgb` binary file or in an `.rgba` armored binary file, which can be imported by the wallet software.

An issuer will then create a particular instance of a schema by filling it in with data such as `precision`, `name` and `issuedSupply`. Initial allocations are also defined, and the resulting structure is encoded into a consignment file and shared with the new owners. Once the first state transition happens, the contract will (indirectly) be committed onchain and take full effect.

In the next chapter, we provide a list of currently supported schemas.
