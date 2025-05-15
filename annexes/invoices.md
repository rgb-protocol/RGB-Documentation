# Invoices

This section explores **how invoices are structured and operate within a particular** [contract](glossary.md#contract). The initial focus is on RGB identifiers, which are integral to the operation of the system and may be encountered by users in various forms. These identifiers are unique to each component of the system, including contracts and assets, ensuring a standardized method of identification throughout the system.

## Identifiers and their encoding

Each element within the system, be it a contract, schema or asset, is assigned a **unique identifier.** These identifiers are not arbitrary strings but are carefully encoded using base58, a method chosen for its efficiency and readability. Furthermore, these identifiers are prefixed with a descriptor (in the form of a URL or URN) indicating their type, such as <mark style="color:red;">`rgb:`</mark> . This prefixing strategy ensures clarity regarding the nature of each identifier, preventing confusion with other URLs and misuse.

## Enhancing Human Readability through Chunking

The concept of chunking has been introduced as a means to **enhance the readability and verifiability** of these identifiers. This technique, commonly used in phone and credit card numbers, breaks down long strings into smaller, more manageable segments. This feature not only aids in human parsing but also in verification processes, where checking the integrity of an identifier involves examining specific segments, such as the checksum at the end. Chunking, thereby, offers a balance between security and usability, with each chunk providing a certain level of security assurance. For example, having 256-bit strings divided into six blocks means that each chunk adds about 256/6 (\~42) bits of security.

An identifier for an RGB contract could be represented, by the following <mark style="color:orange;">`ContractId`</mark> encoded string:&#x20;

<mark style="color:orange;">`2whK8s5O-b1LG4rR-OhXpDq1-SjyHvKx-OhTEFjQ-aba0V_o`</mark>

which, as we said, is a string in _Base58_ divided into different chunks to make it easier to read. The last group of characters is a _checksum_ of the previous encoding. Finally, Base58 encoding was chosen in favor of [Bech32](https://en.bitcoin.it/wiki/Bech32) encoding which can have some limitations regarding readability and character size limits of the string.

## Use of URLs for Invoices

A significant advantage of this identifier system is its compatibility with URLs, allowing for direct interaction with wallets through simple clicks. This contrasts sharply with the cumbersome process required by other systems, where multiple steps are needed to copy and paste identifiers into wallets.&#x20;

An example of an Invoice URL for fungible tokens might be:&#x20;

<mark style="color:red;">`rgb`</mark>`:`<mark style="color:orange;">`2whK8s5O-b1LG4rR-OhXpDq1-SjyHvKx-OhTEFjQ-aba0V_o`</mark>`/`<mark style="color:blue;">`RWhwUfTMpuP2Zfx1~j4nswCANGeJrYOqDcKelaMV4zU`</mark>`/`<mark style="color:purple;">`cR`</mark>`/`<mark style="color:green;">`bc:utxob:x8H6O_~H-7RyndJZ-CAUUAcF-RJfWg7H-9hew6Zo-pacK97w-gaGhQ`</mark>

Where

* <mark style="color:red;">**`rgb:`**</mark> defines the application identifier of the URL.
* The <mark style="color:orange;">`ContractId`</mark> is the same as in the previous example.
* <mark style="color:blue;">`RWhwUfTMpuP2Zfx1~j4nswCANGeJrYOqDcKelaMV4zU`</mark> defines the schema which the contract should implement.
* The string <mark style="color:purple;">`cR`</mark> represents the amount of the requested tokens encoded in a Base32 alphabet with no digits.
* The string <mark style="color:green;">`bc:utxob:x8H6O_~H...`</mark> is the [concealed form](../rgb-state-and-operations/components-of-a-contract-operation.md#seal-definition) of the [seal definition](glossary.md#seal-definition) that prevents Alice from knowing the UTXO actually held by Bob. The part following the `bc:utxob:` identifier is encoded in Baid64.

The URL format's simplicity and efficiency in opening wallets and facilitating transactions underscore its superiority over alternatives. Alternatives to the direct use of contract IDs, for example by using asset tickers, were considered but ultimately rejected due to security concerns and the potential for confusion. The chosen format prioritizes clarity and security, ensuring that users can easily understand and verify the details of their transactions.

The power of URLs is also expressed in the ease with which parameters such as an **invoice signature** can be introduced:&#x20;

<mark style="color:red;">`rgb`</mark>`:`<mark style="color:orange;">`2whK8s5O-b1LG4rR-OhXpDq1-SjyHvKx-OhTEFjQ-aba0V_o`</mark>`/`<mark style="color:blue;">`RWhwUfTMpuP2Zfx1~j4nswCANGeJrYOqDcKelaMV4zU`</mark>`/`<mark style="color:purple;">`cR`</mark>`/`<mark style="color:green;">`bc:utxob:x8H6O_~H-7RyndJZ-CAUUAcF-RJfWg7H-9hew6Zo-pacK97w-gaGhQ`</mark><mark style="color:yellow;">`?sig=6kzbKKffP6xftkxn9UP8gWqiC41W16wYKE5CYaVhmEve`</mark>

With this invoice URL format each software is to be able to interpret the part of the invoice which it is able to execute while the other parts (e.g. the <mark style="color:yellow;">`?sig`</mark> part relate signature verification) can be safely discarded.

As for an extra example, in the box below an example of NFT transfer invoice is shown:&#x20;

<mark style="color:red;">`rgb:`</mark><mark style="color:orange;">`jgOr8JoA-BSmFO9S-Z0_hGE~-pV6VQf8-d0phP06-obTe8Go`</mark>`/`<mark style="color:blue;">`~6rjymf3GTE840lb5JoXm2aFwE8eWCk3mCjOf_mUztE`</mark>`/`<mark style="color:purple;">`1@0`</mark>`/`<mark style="color:green;">`bc:utxob:x8H6O_~H-7RyndJZ-CAUUAcF-RJfWg7H-9hew6Zo-pacK97w-gaGhQ`</mark>&#x20;

Where, in addition to the already described parts, the <mark style="color:purple;">`1@0`</mark> part shows that a receiver can explicitly ask to for the fraction `1` of an UDA token with index `0`.

***
