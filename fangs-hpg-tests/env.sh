#!/bin/bash
# HPG: create (once) and activate the conda environment of this campaign. Sourced by build.slurm, hpg_tier.slurm and
# compare.slurm; can also be run by hand on login7 (tmux session hemtrad) if a compute node cannot reach conda-forge:
#   source fangs-hpg-tests/config.env; bash fangs-hpg-tests/env.sh create
# It follows flooxs-pyplot docs/runbooks/hipergator-setup.md (the conda route), with the environment and its package
# cache inside $BASE so that ~/.condarc and the group's other environments are not touched.
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
source "$here/config.env"

module purge >/dev/null 2>&1 || true
module load conda
export CONDA_PKGS_DIRS=$PKGS

if [ ! -x "$ENV/bin/python" ]; then
  mkdir -p "$BASE" "$PKGS"
  installer=$(command -v mamba || command -v conda)
  "$installer" create -y -p "$ENV" -c conda-forge --override-channels \
      python=3.12 cmake make c-compiler cxx-compiler \
      "eigen=3.4" suitesparse "libblas=*=*openblas" liblapack openblas \
      hdf5 fftw tk numpy matplotlib nanobind
fi
[ "${1:-}" = create ] && exit 0

eval "$(conda shell.bash hook)"
conda activate "$ENV"
export FLXSHOME=$FLX
