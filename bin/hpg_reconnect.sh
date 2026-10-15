#!/usr/bin/env bash
# Reopen the HPG master connection (ssh hpg) with the workstation key + one Duo push.
# The key (~/.ssh/id_ed25519_hpg) replaces the UF password; Duo is still required,
# so Ian must approve the push on his phone. One attempt only, never a loop.
# Notify Ian BEFORE running this (he gets a Duo push). Uses a tmux window if a tmux
# server is running, else its own detached tmux session.
# Exit 0 = master running; 1 = no Duo prompt appeared; 2 = push not approved in time.
set -u
ssh -O check hpg 2>/dev/null && { echo "master already running"; exit 0; }
W=hpg-auth
CMD="env -u SSH_ASKPASS -u DISPLAY SSH_ASKPASS_REQUIRE=never ssh -fN hpg; sleep 30"
# no askpass GUI: the Duo menu must come up on the tmux pane
if tmux has-session 2>/dev/null; then
    tmux kill-window -t "$W" 2>/dev/null
    tmux new-window -d -n "$W" "$CMD"
    KILL="tmux kill-window -t $W"
else                                     # no tmux server (agent not started via agent-up)
    tmux new-session -d -s "$W" "$CMD"
    KILL="tmux kill-session -t $W"
fi
for i in $(seq 1 15); do
    sleep 2
    tmux capture-pane -p -t "$W" | grep -q "Passcode or option" && break
done
if ! tmux capture-pane -p -t "$W" | grep -q "Passcode or option"; then
    echo "no Duo prompt:"; tmux capture-pane -p -t "$W" | grep -v '^$' | tail -5
    $KILL 2>/dev/null; exit 1
fi
tmux send-keys -t "$W" 1 Enter          # 1 = Duo Push to XXX-XXX-8915 (Ian's choice)
for i in $(seq 1 12); do
    sleep 10
    if ssh -O check hpg 2>/dev/null; then
        $KILL 2>/dev/null; echo "master running"; exit 0
    fi
done
echo "Duo push not approved within 2 min"
$KILL 2>/dev/null; exit 2
