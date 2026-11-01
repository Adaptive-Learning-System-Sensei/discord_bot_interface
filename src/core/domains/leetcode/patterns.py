from src.utils.python_logging import setup_logging

logger = setup_logging()


class Patterns:
    """
    A class that contains various patterns used in the LeetCode domain.
    """

    """
    A list of patterns used in the LeetCode domain. Make sure the patterns names match the names used in the LeetCode API.
    The names are case-insensitive and spaces are replaced with hyphens.
    For example, "Two Pointers" should be "two-pointers" in the API.
    """
    patterns_list: list = [
        "Array",
        "String",
        "Hash Table",
        "Math",
        "Dynamic Programming",
        "Sorting",
        "Greedy",
        "Binary Search",
        "Depth-First Search",
        "Bit Manipulation",
        "Matrix",
        # "Prefix Sum",##########################
        "Tree",
        "Two Pointers",
        "Breadth-First Search",
        "Heap (Priority Queue)",
        # "Counting",#################################
        # "Graph Theory",######################################
        "Stack",
        "Binary Tree",
        "Sliding Window",
        "Backtracking",
        # "Number Theory",###############################
        # "Union-Find",#############
        "Linked List",
        # "Ordered Set",#####################
        "Monotonic Stack",
        "Divide and Conquer",
        "Combinatorics",
        "Trie",
        # "Queue",########################
        # "Bitmask",############################
        # "Binary Indexed Tree",############
        "Recursion",
        "Memoization",
        # "Shortest Path",#####################
        "Binary Search Tree",
        # "Topological Sort",##################
        "String Matching",
        # "Monotonic Queue",#########################
        "Merge Sort",
        # "Minimax",############################
        # "Doubly-Linked List",#######################
        # "Counting Sort",#######################
        # "Suffix Array",##################
        # "Quickselect",#######################
        # "Bucket Sort",###################
        # "Meet in the Middle",###############
        # "Radix Sort",#############
        "heap-priority-queue",
    ]

    def list_patterns(self) -> list:
        return self.patterns_list