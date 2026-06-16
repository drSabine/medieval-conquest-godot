import maptools as mt, generate_map as gm, os
# rebuild without writing, no grid
import importlib
text, existing = mt.read_main_layers()
# monkey-call generate by replicating its body quickly via composite of a fresh run:
# easiest: temporarily patch composite grid off by re-running generate logic
