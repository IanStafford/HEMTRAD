# FANGS first HiPerGator run (finished 2026-11-04)

Inputs for the validation of FANGS's HPG kit: `pin.env`, `slurm.env` (account, QOS and partition deliberately blank), `params_fangsDiode.csv`, `hang.py`. This did not touch the FLOOXS/Tcl HEMT model.

Result: checklist steps 2-5 passed; step 6 needed test fixes in FANGS, ending at 6570d19. Details and job IDs are in `progress.md` (2026-11-04). The procedure is in the private FANGS repo, `docs/runbooks/hipergator-setup.md`.

On HPG: checkout `/blue/ee1/ianstafford/flooxs-pyplot`, env `/blue/ee1/ianstafford/conda/envs/fangs`, outputs `/blue/ee1/ianstafford/runs`. See `kb/workflow/repo-locations.md`.
