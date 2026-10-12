---
title: HiPerGator workflow
tags: [workflow, hpg]
---
# HiPerGator (HPG) workflow

The binding rules (ask before sbatch/scancel, connection-failure procedure) are in `CLAUDE.md` §2; this note holds the details.

**Connection:** only through `ssh hpg`, a multiplexed master (`ControlMaster auto`, `ControlPersist yes`, `ServerAliveInterval 60` in `~/.ssh/config`) that Ian authenticates (password typed in tmux + Duo). Check with `ssh -O check hpg`. If it is down, nothing can reopen it remotely. It has survived overnight sometimes and dropped other nights. HPG has **no GitHub credentials** (HEMTRAD is pulled anonymously over HTTPS; private repos need a git bundle copied from the workstation, see [[flooxs-pyplot-regression]]).

**Commands:** always a login shell with a quoted heredoc:
```bash
ssh hpg bash -l <<'REMOTE'
cd /home/ianstafford/blue/ee1/ianstafford/HEMTRAD
git pull --ff-only
squeue -u $USER
REMOTE
```

**Job environment:**
```bash
module restore flooxsenv
eval "$(conda shell.bash hook)"
conda activate flooxs
export FLXSHOME=/home/ianstafford/blue/ee1/ianstafford/flooxs
export PL_LIBRARY=$(find $CONDA_PREFIX/share -maxdepth 3 -type d -name "tcl" | grep -i plplot | head -1)
export PATH=$HOME/.local/flooxs/bin:$PATH
$FLXSHOME/release/flooxs script.tcl
```
- `flooxsenv` brings Intel icx/icpx 2025.1; the conda env `flooxs` has SuiteSparse 6.3.5, OpenBLAS 0.3.33, Tcl 8.6, CMake. Eigen 3.4 is a module (`eigen3/3.4.0`), not in the env.
- A job that dies immediately with a library/Tcl/`PL_LIBRARY`/plplot error is an environment problem, not the deck.
- Never run `flooxs` on a login node.

**SLURM:** `--account=ee1`. QOS `ee1` caps the group at 19 CPUs; burst **`ee1-b` at 171 CPUs** (1.37 TB) — large sweeps. Check `squeue -A ee1` first; throttle arrays with `%N`. An `--exclusive` node counts all its cores against the QOS (Milan 64, Rome 128). Users can lower but not raise a time limit (`scontrol update JobId=<arr>_<i> TimeLimit=…`), which is how one array gets per-task limits. Partitions seen: `hpg-default` (AMD Rome, 128 c), `hpg-milan` (EPYC 75F3, 64 c), `hpg-turin` (96 c, GPU nodes), `bigmem`; whole nodes are often all allocated.

**Resources:** `--cpus-per-task=1 --mem=4gb --time=03:00:00` for a 0–3/0–4 V `pulsedIV` sweep (20–60 min; tasks bisecting through a collapse up to 2 h; Te-ramp/energy-balance runs set 6 h). Raise `--mem` on OOM; don't change the deck. Poll every 5 min with a background `sleep 300` loop.

Related: [[sweep-pattern]], [[repo-locations]].
