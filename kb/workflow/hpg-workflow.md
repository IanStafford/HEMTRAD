---
title: HiPerGator workflow
tags: [workflow, hpg]
---
# HiPerGator (HPG) workflow

The binding rules (ask before sbatch/scancel, connection-failure procedure) are in `CLAUDE.md` §2; this note holds the details.

**Connection:** only through `ssh hpg`, a multiplexed master (`~/.ssh/config`: `ControlMaster auto`, `ControlPath ~/.ssh/cm-%r@%h:%p`, `ControlPersist yes`, `ServerAliveInterval 60`, `ServerAliveCountMax 3`, `IdentityFile ~/.ssh/id_ed25519_hpg`, `IdentitiesOnly yes`). Check with `ssh -O check hpg`; agent commands use `ssh -o BatchMode=yes` so they fail instead of prompting. The master has survived overnight sometimes and dropped other nights. HPG has **no GitHub credentials** (HEMTRAD is pulled anonymously over HTTPS; private repos need a git bundle copied from the workstation, see [[flooxs-pyplot-regression]]).

**Authentication (since 2026-10-13, per [UFRC SSH keys](https://docs.rc.ufl.edu/access/ssh_keys/)):** workstation key `~/.ssh/id_ed25519_hpg` (ed25519, **no passphrase** — Ian's choice, so it works unattended after reboots; mode 600, never in the repo), public key appended to HPG `~/.ssh/authorized_keys` (backup `authorized_keys.bak.20261013`). Tested: the key is accepted as the first factor (`Authenticated using "publickey" with partial success`) and replaces the UF password, but **Duo is still required** — the server then asks only `Passcode or option (1-3)` (1 = push to XXX-8915, 2 = push to iOS, 3 = phone call).

**Reconnect procedure (`bin/hpg_reconnect.sh`):** push-notify Ian first, then run the script once from inside tmux. It opens `ssh -fN hpg` in a detached tmux window with `SSH_ASKPASS` unset (otherwise `ksshaskpass` grabs the Duo prompt), sends `1` at the Duo menu, and polls `ssh -O check hpg` for 2 min. Exit 0 = master up, 1 = no Duo prompt (anything else, e.g. a password prompt → stop), 2 = push not approved. One attempt; if it fails, log it in `progress.md`, notify Ian and wait. Live-tested 2026-10-13 on a second ControlPath: Duo push approved, `Success. Logging you in...`, commands ran through the new master.

**Persistent sessions ([UFRC](https://docs.rc.ufl.edu/access/persistent_sessions/)):** sessions live on one login node, so we pin `login7`. `~/.ssh/config` aliases (both `ProxyJump hpg`, so they ride on the master with no extra Duo; login7's host key is in `~/.ssh/known_hosts`):
- `ssh hpg-login7 '<cmd>'` — run a command on login7;
- `ssh hpg-tmux` — attach (or create) the tmux session `hemtrad` (`RemoteCommand bash -lc "module load tmux && tmux new -A -s hemtrad"`, tmux 3.5 is a module; `screen` is in `/usr/bin`).
Non-interactive use: `ssh -o BatchMode=yes hpg-login7 'bash -lc "module load tmux; tmux send-keys -t hemtrad \"<cmd>\" Enter"'`, read back with `tmux capture-pane -p -t hemtrad`. The session survives the master dropping (verified: created, then reattached from a separate connection). Use it for long `rsync`s, builds, `srun --pty` interactive jobs (they keep running while detached), HPG-side watchers; **never `flooxs` on the login node**. A login-node reboot (maintenance) kills the session; `sbatch` jobs are unaffected. Ian can attach from his laptop with the same alias if his config has it (`ssh hpg`, then `ssh login7`, `module load tmux`, `tmux attach -t hemtrad`).

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
