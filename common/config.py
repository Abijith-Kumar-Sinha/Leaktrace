"""Global constants. Every tunable lives here or in a CLI flag; nothing is hidden."""
PX_TO_PT = 0.75            # WeasyPrint lays out in CSS px; PDF is in pt
RASTER_SCALE = 4.0         # master raster resolution, pixels per point (288 dpi)
DEFAULT_DELTA_PT = 0.30    # word-gap offset magnitude (pt)   -- final value chosen by E1
DEFAULT_EPS_PT = 0.30      # line-position offset magnitude (pt) -- final value chosen by E1
DEFAULT_ALPHA = 1e-3       # family-wise false-accept level for the accept/reject decision
N_NULL = 4000              # number of wrong keys used to build the null distribution
SEED = 20261031            # fixed seed for every experiment (reproducibility)
