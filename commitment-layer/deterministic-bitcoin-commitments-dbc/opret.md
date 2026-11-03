# Opret

Opret represents the simplest and most straightforward scheme. The commitment is inserted into the first `OP_RETURN` output of the [witness transaction](../../annexes/glossary.md#witness-transaction) in the following way:

```
34-byte_Opret_Commitment =
 OP_RETURN   OP_PUSHBYTES_32   <mpc::Commitment>
|_________| |_______________| |_________________|
  1-byte        1-byte           32 bytes                      
```

The `mpc::Commitment` is the 32-byte tagged hash resulting from the [MPC tree](../multi-protocol-commitments-mpc.md#mpc-tagged-hash) (this concept is covered in detail in the [next section](../multi-protocol-commitments-mpc.md)). Hence an opret commitment will have a total size of 34 bytes.

***
