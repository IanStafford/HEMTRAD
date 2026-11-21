"""Re-export of the radIV metrics and measured-data guards, which now live in analysis/common.py (clean-up stage 3a).
radFit.py and plot_radFinal.py import guard_private_output from here; new code imports from common.
  vth_gm                Vth by linear extrapolation at the peak gm, and that peak
  ron_step              Ron for 0 < Vd <= 0.5 V and the largest neighbour drop of an Id-Vd (Id_ext column)
  guard_private_output  refuses to write a figure with measured data under figures/ or dashboard/
  load_pre_scalars      measured pre-irradiation scalars from the untracked pre_scalars.csv
"""
from common import PRIVATE_DIRS, guard_private_output, load_pre_scalars, ron_step, vth_gm  # noqa: F401
