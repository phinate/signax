from collections import defaultdict
from typing import List

import jax
import jax.numpy as jnp


@jax.jit
def index_select(input: jnp.ndarray, indices: jnp.ndarray) -> jnp.ndarray:
    """
    Select entries in m-level tensor based on given indices
    This function will help compressing log-signatures

    Args:
        A: size (dim, dim, ..., dim)
        indices: size (dim, n)
    Return:
        A 1D jnp.ndarray
    """

    dim = input.shape[0]
    ndim = input.ndim
    n = indices.shape[1]
    assert n <= ndim
    strides = jnp.array([dim**i for i in range(n)])
    # flatten matrix A in C-style
    flattened = input.ravel()

    def _select(index):
        """index is a `jnp.ndarray` int"""

        # this is the way to compute the position of
        # (C-style) raveled arrays
        position = jnp.sum(index * strides)
        return flattened[position]

    return jax.vmap(_select)(indices)


def lyndon_words(depth, dim) -> List[jnp.ndarray]:

    """Generate Lyndon words of length `depth` over an `dim`-symbol alphabet
    Example in Python: https://gist.github.com/dvberkel/1950267

    Args:
        depth: int
        dim: int
    """
    list_of_words = defaultdict(list)
    word = [-1]
    while word:
        word[-1] += 1
        m = len(word)
        # yield word
        list_of_words[m - 1].append(jnp.array(word))
        while len(word) < depth:
            word.append(word[-m])
        while word and word[-1] == dim - 1:
            word.pop()

    return [jnp.stack(list_of_words[i]) for i in range(depth)]
