"""Tagentacle InferenceMux SDK — inference trigger mechanism for agent nodes.

Q27: Inbox moved to tagentacle-py-core. This package provides InferenceMux only.
"""

from tagentacle_py_inferencemux.mux import InferenceMux, MuxState, TriggerSignal

__all__ = [
    "InferenceMux",
    "MuxState",
    "TriggerSignal",
]
