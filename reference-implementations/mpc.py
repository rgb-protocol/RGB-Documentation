from hashlib import sha256
from dataclasses import dataclass
from typing import Mapping, Sequence
from math import log2

NODE_TAG = b"urn:ubideco:merkle:node#2024-01-31"
MPC_TAG = b"urn:ubideco:mpc:commitment#2024-01-31"


def tagged_hash(tag, *elems: bytes):
    th = sha256(tag).digest()
    return sha256(th + th + b"".join(elems)).digest()


@dataclass
class Node:
    def hash(self) -> bytes:
        return NotImplemented


@dataclass
class Leaf(Node):
    pass


@dataclass
class PopulatedLeaf(Leaf):
    protocol: bytes
    message: bytes
    ident = b"\x10"

    def hash(self) -> bytes:
        return tagged_hash(NODE_TAG, self.ident, self.protocol, self.message)


@dataclass
class EntropyLeaf(Leaf):
    entropy: int
    pos: int
    ident = b"\x11"

    @property
    def entropy_bytes(self) -> bytes:
        return self.entropy.to_bytes(8, "little")

    @property
    def pos_bytes(self) -> bytes:
        assert self.pos is not None, "Leaf does not belong to a tree"
        return self.pos.to_bytes(4, "little")

    def hash(self) -> bytes:
        return tagged_hash(NODE_TAG, self.ident, self.entropy_bytes, self.pos_bytes)


@dataclass
class MerkleNode(Node):
    left: Node
    right: Node
    depth: int
    tree_width: int

    @classmethod
    def from_cross_section(cls, leaves: Sequence[Leaf]) -> "MerkleNode":
        tree_width = len(leaves)
        tree_depth = int(log2(tree_width))
        assert 2**tree_depth == tree_width, f"tree must have 2^h leaves, {tree_depth}"
        return cls._from_cross_section(leaves, 0, tree_width)

    @classmethod
    def _from_cross_section(
        cls, leaves: Sequence[Leaf], depth: int, tree_width: int
    ) -> "MerkleNode":
        subtree_width = len(leaves)
        if subtree_width == 2:
            left, right = leaves
        else:
            # recursively build the two subtrees before creating the current node
            half = subtree_width // 2
            left = MerkleNode._from_cross_section(leaves[:half], depth + 1, tree_width)
            right = MerkleNode._from_cross_section(leaves[half:], depth + 1, tree_width)
        return MerkleNode(left, right, depth, tree_width)

    @property
    def branching(self) -> bytes:
        if self.left is None and self.right is None:
            return b"\x00"
        if self.left is None or self.right is None:
            return b"\x01"
        return b"\x02"

    @property
    def depth_bytes(self) -> bytes:
        assert self.depth is not None, "Node does not belong to a tree"
        return self.depth.to_bytes(1)

    @property
    def tree_width_bytes(self) -> bytes:
        assert self.tree_width is not None, "Node does not belong to a tree"
        return self.tree_width.to_bytes(32, "little")

    def hash(self) -> bytes:
        return tagged_hash(
            NODE_TAG,
            self.branching,
            self.depth_bytes,
            self.tree_width_bytes,
            self.left.hash(),
            self.right.hash(),
        )


@dataclass
class MerkleTree:
    depth: int
    cofactor: int
    root: Node

    @classmethod
    def from_entropy_messages(
        cls,
        depth: int,
        cofactor: int,
        entropy: int,
        message_map: Mapping[int, tuple[bytes, bytes]],
    ) -> "MerkleTree":
        cross_section = [
            (
                PopulatedLeaf(*message_map[pos])
                if pos in message_map
                else EntropyLeaf(entropy, pos)
            )
            for pos in range(2**depth)
        ]
        return cls(depth, cofactor, MerkleNode.from_cross_section(cross_section))

    @property
    def depth_bytes(self):
        return self.depth.to_bytes(1)

    @property
    def cofactor_bytes(self):
        return self.cofactor.to_bytes(2, "little")

    def hash(self):
        return tagged_hash(
            MPC_TAG, self.depth_bytes, self.cofactor_bytes, self.root.hash()
        )


def _get_bin_path(contract_pos, tree_depth) -> list[bool]:
    """
    Describes the path from the root of a tree of depth 'tree_depth' down to 'contract_pos', where:
    - True -> left
    - False -> right
    """
    return [c == "0" for c in f"{contract_pos:0{tree_depth}b}"]


@dataclass
class HiddenNode(Node):
    leaf_hash: bytes

    def hash(self) -> bytes:
        return self.leaf_hash


@dataclass
class MerkleProof:
    pos: int
    cofactor: int
    path: list[Node]

    @classmethod
    def from_merkle_tree(cls, tree: MerkleTree, contract_pos: int) -> "MerkleProof":
        path = []
        node = tree.root
        for is_left in _get_bin_path(contract_pos, tree.depth):
            assert isinstance(node, MerkleNode)
            node, sibling = (
                (node.left, node.right) if is_left else (node.right, node.left)
            )
            path.append(HiddenNode(sibling.hash()))
        return cls(contract_pos, tree.cofactor, path)

    @property
    def depth(self) -> int:
        return len(self.path)

    @property
    def depth_bytes(self):
        return self.depth.to_bytes(1, "big")

    @property
    def tree_width(self):
        return 2**self.depth

    @property
    def tree_width_bytes(self):
        return self.tree_width.to_bytes(32, "little")

    @property
    def cofactor_bytes(self):
        return self.cofactor.to_bytes(2, "little")

    def partial_tree(self, protocol: bytes, message: bytes) -> MerkleTree:
        node = PopulatedLeaf(protocol, message)
        bin_path = _get_bin_path(self.pos, self.depth)
        for height, sibling in enumerate(reversed(self.path)):
            node_depth = self.depth - height - 1
            is_left = bin_path[node_depth]
            left, right = (node, sibling) if is_left else (sibling, node)
            node = MerkleNode(left, right, node_depth, self.tree_width)
        return MerkleTree(self.depth, self.cofactor, node)

    def hash(self, protocol: bytes, message: bytes) -> bytes:
        return self.partial_tree(protocol, message).hash()
