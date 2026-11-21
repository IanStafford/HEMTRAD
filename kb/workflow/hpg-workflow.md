---
title: HiPerGator workflow
tags: [workflow, hpg]
---
# HiPerGator (HPG) workflow

The binding rules (ask before sbatch/scancel, connection-failure procedure) are in `CLAUDE.md` §2; this note holds the details.

**Connection:** only through `ssh hpg`, a multiplexed master (`~/.ssh/config`: `ControlMaster auto`, `ControlPath ~/.ssh/cm-%r@%h:%p`, `ControlPersist yes`, `ServerAliveInterval 60`, `ServerAliveCountMax 3`, `IdentityFile ~/.ssh/id_ed25519_hpg`, `IdentitiesOnly yes`). Check with `ssh -O check hpg`; agent commands use `ssh -o BatchMode=yes` so they fail instead of prompting. The master has survived overnight sometimes and dropped other nights. HPG has **no GitHub credentials** (HEMTRAD is pulled anonymously over HTTPS; private repos need a git bundle copied from the workstation, see [[flooxs-pyplot-regression]]).

**Authentication (since 2026-10-13, per [UFRC SSH keys](https://docs.rc.ufl.edu/access/ssh_keys/)):** workstation key `~/.ssh/id_ed25519_hpg` (ed25519, **no passphrase** — Ian's choice, so it works unattended after reboots; mode 600, never in the repo), public key appended to HPG `~/.ssh/authorized_keys` (backup `authorized_keys.bak.20261013`). Tested: the key is accepted as the first factor (`Authenticated using "publickey" with partial success`) and replaces the UF password, but **Duo is still required** — the server then asks only `Passcode or option (1-3)` (1 = push to XXX-8915, 2 = push to iOS, 3 = phone call).

**Reconnect procedure (`bin/hpg_reconnect.sh`):** push-notify Ian first, then run the script once. If `ssh -O check hpg` already succeeds it exits 0. Otherwise it kills any old tmux session `hpg-master` and starts a new detached one that runs `ssh -N hpg` in the foreground, with `SSH_ASKPASS` and `DISPLAY` unset and `SSH_ASKPASS_REQUIRE=never` (otherwise `ksshaskpass` grabs the Duo prompt). It waits up to 30 s for `Passcode or option`, sends `1` (push to XXX-8915) and polls `ssh -O check hpg` every 10 s for 2 min. After success the session is kept, so the master does not depend on the agent's own terminal; when `ssh` exits, the session closes 30 s later. This replaced the first version (`ssh -fN hpg` in a tmux window or a session `hpg-auth`) on 2026-10-23, after a master opened with `-f` outside tmux dropped after about 6 h. Exit 0 = master running, 1 = no Duo prompt (the script prints the last pane lines; anything else, e.g. a password prompt, means stop), 2 = push not approved within 2 min. On exit 1 or 2 it kills the session. One attempt; if it fails, log it in `progress.md`, notify Ian and wait. The first version was live-tested 2026-10-13 on a second ControlPath (Duo push approved, `Success. Logging you in...`); the current one reconnected with one push on 2026-11-14. On 2026-11-12 it failed inside the Claude desktop app, where snap `tmux` could not start under NoNewPrivs, and the master was reopened by hand with `ssh -fN hpg` from the app's Terminal panel.

**Ian's start-up script `~/bin/agent-up`** (workstation, outside the repo; Ian runs it himself at the start of the day, after a reboot or when the link dropped): creates/repairs the local tmux session `agent` (windows `hpg` and `claude`). If `ssh -O check hpg` fails it starts `ssh -MN hpg` in the `hpg` window with `SSH_ASKPASS`/`DISPLAY` unset, waits up to 30 s for `Passcode or option`, answers `1` (push to XXX-8915) and waits up to 2 min for Ian to approve; then it makes sure the login7 tmux session `hemtrad` exists. A **password prompt** means the key was not accepted: the script stops and leaves the prompt to Ian (only Ian ever types his password). It then starts `claude --continue --remote-control` (after `git pull --ff-only`) if not already running and attaches. Agents use `bin/hpg_reconnect.sh` instead (notify first, once).

**Persistent sessions ([UFRC](https://docs.rc.ufl.edu/access/persistent_sessions/)):** sessions live on one login node, so we pin `login7`. `~/.ssh/config` aliases (both `ProxyJump hpg`, so they ride on the master with no extra Duo; login7's host key is in `~/.ssh/known_hosts`):
- `ssh hpg-login7 '<cmd>'` — run a command on login7;
- `ssh hpg-tmux` — attach (or create) the tmux session `hemtrad` (`RemoteCommand bash -lc "module load tmux && tmux new -A -s hemtrad"`, tmux 3.5 is a module; `screen` is in `/usr/bin`).
Non-interactive use: `ssh -o BatchMode=yes hpg-login7 'bash -lc "module load tmux; tmux send-keys -t hemtrad \"<cmd>\" Enter"'`, read back with `tmux capture-pane -p -t hemtrad`. The session survives the master dropping (verified: created, then reattached from a separate connection). Use it for long `rsync`s, builds, `srun --pty` interactive jobs (they keep running while detached), HPG-side watchers; **never `flooxs` on the login node**. A login-node reboot (maintenance) kills the session; `sbatch` jobs are unaffected. Ian can attach from his laptop with the same alias if his config has it (`ssh hpg`, then `ssh login7`, `module load tmux`, `tmux attach -t hemtrad`).

**Paths:** `/home/ianstafford/blue/ee1/ianstafford` (the HEMTRAD checkout and worktrees, stock FLOOXS, every sweep's `results/`) is in the 40 GB NFS home. `/blue/ee1/ianstafford` is the real `/blue`: the HEMTRAD stress library (`stress/`, [[stress-library]]), FANGS (`flooxs-pyplot/`, `runs/`, `conda/envs/fangs`) and HEMTRAD-FANGS. They are separate directories. Write each path exactly as [[repo-locations]] and the params files give it; a `stressLoad=/blue/ee1/ianstafford/stress/...` path is correct.

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

**Resources:**
- `pulsedIV` (Oct era): `--cpus-per-task=1 --mem=4gb --time=03:00:00` for a 0–3/0–4 V sweep (20–60 min; tasks bisecting through a collapse up to 2 h; Te-ramp/energy-balance runs set 6 h).
- `radIV.slurm` asks for 1 CPU, 4 GB and 24 h; override `--mem`/`--time` on the `sbatch` line ([[sweep-pattern]]). A run that loads a saved 28 V state (`stressLoad`) and measures takes a few hours; recent ones ask 8 GB and a 2-day limit (16 GB on the 2.5 nm mesh).
- A 28 V stress solve on 1 CPU takes about a day on the mesh-check meshes (m5fix 24 h); the 2.5 nm mesh (157k points) reached Vd 20 in 21.6 h. Stress jobs ask 8 GB (16 GB on 2.5 nm) and the 4-day limit. In the 84 V library (stressLib 51459840) the SiN task hit that limit and was resumed with `stressResume` (stressLibResume 51998839); HighK finished.
- 3D slices (`deviceDim 3`): the rad3dTrack1 track runs (51061334, z spacing 20 nm at the track, BiCGSTAB) took about 1-1.5 h per Vd point. UMFPACK already fails at 5 z lines (test 51061333, 128 GB): above roughly 50k points it hits its 32-bit index limit, not RAM. Those runs used stock FLOOXS before the brick-gradient bug was found; 3D now needs a build with the brick fix (`~/flooxs-brickfix` locally, or FANGS with the fix on HPG; `CLAUDE.md` §6, [[3d-plan]]).
- Raise `--mem` on OOM; don't change the deck. Poll every 5 min with a background `sleep 300` loop.

Related: [[sweep-pattern]], [[repo-locations]].
