import numpy as np


def pretty_depth(depth):
    """Converte l'immagine di profondità in un formato più facile da gestire

    Args:
        depth: Un array numpy che ha 2 byte per pixel

    Returns:
        Un array numpy di tipo uint8
    """
    np.clip(depth, 0, 2**10 - 1, depth)
    depth >>= 2
    depth = depth.astype(np.uint8)
    return depth