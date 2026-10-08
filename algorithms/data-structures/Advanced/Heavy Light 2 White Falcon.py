from operator import attrgetter

MOD = 10**9 + 7

def solve(edges, queries):
    nodes, leaves = make_tree(edges)
    hld(leaves)

    results = []
    for query in queries:
        if query[0] == 1:
            update(nodes[query[1]], nodes[query[2]], query[3])
        elif query[0] == 2:
            results.append(sum_range(nodes[query[1]], nodes[query[2]]))

    return results

def make_tree(edges):
    nodes = [
        Node(i)
        for i in range(len(edges) + 1)
    ]

    # the tree is a graph for now
    # as we don't know the direction of the edges
    for edge in edges:
        nodes[edge[0]].children.append(nodes[edge[1]])
        nodes[edge[1]].children.append(nodes[edge[0]])

    # pick the root of the tree
    root = nodes[0]
    root.depth = 0

    # for each node, remove its parent of its children
    stack = []
    leaves = []
    for child in root.children:
        stack.append((child, root, 1))
    for node, parent, depth in stack:
        node.children.remove(parent)
        node.parent = parent
        node.depth = depth

        if len(node.children) == 0:
            leaves.append(node)
            continue

        for child in node.children:
            stack.append((child, node, depth + 1))

    return nodes, leaves


def hld(leaves):
    leaves = sorted(leaves, key=attrgetter('depth'), reverse=True)

    for leaf in leaves:
        leaf.chain = Chain()
        leaf.chain_i = 0

        curr_node = leaf
        while curr_node.parent is not None:
            curr_chain = curr_node.chain
            if curr_node.parent.chain is not None:
                curr_chain.init_fenwick_tree()
                curr_chain.parent = curr_node.parent.chain
                curr_chain.parent_i = curr_node.parent.chain_i
                break

            curr_node.parent.chain = curr_chain
            curr_node.parent.chain_i = curr_chain.size
            curr_node.chain.size += 1
            curr_node = curr_node.parent

        if curr_node.parent is None:
            curr_chain.init_fenwick_tree()


def update(node1, node2, x):
    path_len = 0
    chain1 = node1.chain
    chain_i1 = node1.chain_i
    depth1 = node1.depth
    chains1 = []
    chain2 = node2.chain
    chain_i2 = node2.chain_i
    depth2 = node2.depth
    chains2 = []

    while chain1 is not chain2:
        step1 = chain1.size - chain_i1
        step2 = chain2.size - chain_i2

        if depth1 - step1 > depth2 - step2:
            path_len += step1
            chains1.append((chain1, chain_i1))
            depth1 -= step1
            chain_i1 = chain1.parent_i
            chain1 = chain1.parent
        else:
            path_len += step2
            chains2.append((chain2, chain_i2))
            depth2 -= step2
            chain_i2 = chain2.parent_i
            chain2 = chain2.parent

    path_len += abs(chain_i1 - chain_i2) + 1

    curr_val1 = 0
    for (chain, chain_i) in chains1:
        chain.ftree.add(chain_i, chain.size-1, curr_val1, x)
        curr_val1 += (chain.size - chain_i) * x

    curr_val2 = (path_len + 1) * x
    for (chain, chain_i) in chains2:
        chain.ftree.add(chain_i, chain.size-1, curr_val2, -x)
        curr_val2 -= (chain.size - chain_i) * x

    if chain_i1 <= chain_i2:
        chain1.ftree.add(chain_i1, chain_i2, curr_val1, x)
    else:
        chain1.ftree.add(chain_i2, chain_i1, curr_val2, -x)


def sum_range(node1, node2):
    sum_ = 0
    chain1 = node1.chain
    chain_i1 = node1.chain_i
    depth1 = node1.depth
    chain2 = node2.chain
    chain_i2 = node2.chain_i
    depth2 = node2.depth
    while chain1 is not chain2:
        step1 = chain1.size - chain_i1
        step2 = chain2.size - chain_i2
        if depth1 - step1 > depth2 - step2:
            sum_ += chain1.ftree.range_sum(chain_i1, chain1.size - 1)

            depth1 -= step1
            chain_i1 = chain1.parent_i
            chain1 = chain1.parent
        else:
            sum_ += chain2.ftree.range_sum(chain_i2, chain2.size - 1)

            depth2 -= step2
            chain_i2 = chain2.parent_i
            chain2 = chain2.parent

    if chain_i1 > chain_i2:
        chain_i1, chain_i2 = chain_i2, chain_i1

    sum_ += chain1.ftree.range_sum(chain_i1, chain_i2)

    return int(sum_ % MOD)

class Node():
    __slots__ = ['i', 'val', 'parent', 'children', 'depth', 'chain', 'chain_i']

    def __init__(self, i):
        self.i = i
        self.val = 0
        self.parent = None
        self.depth = None
        self.children = []
        self.chain = None
        self.chain_i = -1


class Chain():
    __slots__ = ['size', 'ftree', 'parent', 'parent_i']

    def __init__(self):
        self.size = 1
        self.ftree = None
        self.parent = None
        self.parent_i = -1

    def init_fenwick_tree(self):
        self.ftree = RURQFenwickTree(self.size)

def g(i):
    return i & (i + 1)

def h(i):
    return i | (i + 1)

class RURQFenwickTree():
    def __init__(self, size):
        self.tree1 = RUPQFenwickTree(size)
        self.tree2 = RUPQFenwickTree(size)
        self.tree3 = RUPQFenwickTree(size)

    def add(self, l, r, k, x):
        k2 = k * 2
        self.tree1.add(l, x)
        self.tree1.add(r+1, -x)
        self.tree2.add(l, (3 - 2*l) * x + k2)
        self.tree2.add(r+1, -((3 - 2*l) * x + k2))
        self.tree3.add(l, (l**2 - 3*l + 2) * x + k2 * (1 - l))
        self.tree3.add(r+1, (r**2 + 3*r - 2*r*l) * x + k2 * r)

    def prefix_sum(self, i):
        sum_ = i**2 * self.tree1.point_query(i)
        sum_ += i * self.tree2.point_query(i)
        sum_ += self.tree3.point_query(i)

        return ((sum_ % (2 * MOD)) / 2) % MOD

    def range_sum(self, l, r):
        return self.prefix_sum(r) - self.prefix_sum(l - 1)

class RUPQFenwickTree():
    def __init__(self, size):
        self.size = size
        self.tree = [0] * size

    def add(self, i, x):
        j = i
        while j < self.size:
            self.tree[j] += x
            j = h(j)

    def point_query(self, i):
        res = 0
        j = i
        while j >= 0:
            res += self.tree[j]
            j = g(j) - 1

        return res

if __name__ == '__main__':
    nq = input().split()

    n = int(nq[0])

    q = int(nq[1])

    tree = []

    for _ in range(n-1):
        tree.append(list(map(int, input().rstrip().split())))

    queries = []

    for _ in range(q):
        queries.append(list(map(int, input().rstrip().split())))

    results = solve(tree, queries)

    print('\n'.join(map(str, results)))
