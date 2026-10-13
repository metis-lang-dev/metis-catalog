# dog.llp — a hosted day in the REPL (2026-10-13)

Run: `metis --plugin dog_host:make dog.llp`, then `run 60`, `log`, `why done(go)`, `why refused(find)`, `state`.
The person's commands and the world's answers arrive as the host's tick do-lines (`[env]` rows); the dog's rules are the sampled steps. Likelihood 1: every choice is the state's.

```
plugin dog_host:make (DogHost) attached — 0 weight port(s); the env ticks when the world is quiet
metis shell — dog.llp (catalog dog, key 25b6ca7ec675…)
stage serve | 27 atoms, 27 tokens — 'state' tabulates them
type 'help' for commands, 'events' to see what can fire
llp>   [host beat 2] narrated done(sit)
  [host beat 3] narrated refused(go)
  [host beat 4] narrated done(stand)
  [host beat 5] narrated progress(go)
  [host beat 6] narrated refused(find)
  [host beat 7] narrated done(go)
  [host beat 8] narrated refused(move)
  [host beat 9] narrated progress(find)
  [host beat 10] narrated done(query)
  [host beat 11] narrated refused(find)
  [host beat 12] narrated progress(follow)
  [host beat 13] narrated cancelled(follow)
  [host beat 13] narrated done(stop)
  [host beat 14] narrated refused(unknown)
  [host beat 15] narrated done(paw)
  [host beat 16] narrated refused(find)
  [host beat 17] narrated done(sit)
  [host beat 18] narrated refused(turn)
do +cmd_sit sit[P=standing] do -done(sit) +cmd_go(kitchen) go_closed[P=kitchen] do -refused(go) +cmd_stand stand[P=sitting] do -done(stand) +cmd_go(tag3) go[P=tag3] do -progress(go) +cmd_find(keys) find_busy[T=keys,P=tag3] do -refused(find) +arrived(tag3) arrive[P=tag3,Q=door] do -done(go) +cmd_move(backward) move_wall[W=backward] do -refused(move) +cmd_find(extinguisher) find[T=extinguisher] do -progress(find) +cmd_query(chair) query_seen[T=chair] do -done(query) +locked_away(extinguisher) find_locked[T=extinguisher] do -refused(find) +cmd_follow follow do -progress(follow) +cmd_stop stop_follow do -cancelled(follow) -done(stop) +cmd_unknown unknown do -refused(unknown) +cmd_paw paw do -done(paw) -battery_ok +battery_low +cmd_find(bottle) find_low[T=bottle] do -refused(find) +cmd_sit sit[P=standing] do -done(sit) +cmd_turn(left) turn_down[S=left,P=sitting] do -refused(turn)
stage (done) | at(tag3):1 battery_low:1 clear(forward):1 closed(kitchen):1 closed(window_chair):1 floor_dry:1 free(around):1 free(left):1 free(right):1 idle:1 leg_ok:1 mapped(door):1 mapped(kitchen):1 mapped(tag3):1 mapped(window_chair):1 open(door):1 open(tag3):1 person_in_view:1 posture(sitting):1 seen(chair):1 seen(table):1 unmapped(sofa):1 unmapped(tag5):1 unseen(bottle):1 unseen(extinguisher):1 unseen(keys):1 wall(backward):1
llp>   1. do +cmd_sit  [env]
  2. sit[P=standing]
  3. do -done(sit) +cmd_go(kitchen)  [env]
  4. go_closed[P=kitchen]
  5. do -refused(go) +cmd_stand  [env]
  6. stand[P=sitting]
  7. do -done(stand) +cmd_go(tag3)  [env]
  8. go[P=tag3]
  9. do -progress(go) +cmd_find(keys)  [env]
  10. find_busy[T=keys,P=tag3]
  11. do -refused(find) +arrived(tag3)  [env]
  12. arrive[P=tag3,Q=door]
  13. do -done(go) +cmd_move(backward)  [env]
  14. move_wall[W=backward]
  15. do -refused(move) +cmd_find(extinguisher)  [env]
  16. find[T=extinguisher]
  17. do -progress(find) +cmd_query(chair)  [env]
  18. query_seen[T=chair]
  19. do -done(query) +locked_away(extinguisher)  [env]
  20. find_locked[T=extinguisher]
  21. do -refused(find) +cmd_follow  [env]
  22. follow
  23. do -progress(follow) +cmd_stop  [env]
  24. stop_follow
  25. do -cancelled(follow) -done(stop) +cmd_unknown  [env]
  26. unknown
  27. do -refused(unknown) +cmd_paw  [env]
  28. paw
  29. do -done(paw) -battery_ok +battery_low +cmd_find(bottle)  [env]
  30. find_low[T=bottle]
  31. do -refused(find) +cmd_sit  [env]
  32. sit[P=standing]
  33. do -done(sit) +cmd_turn(left)  [env]
  34. turn_down[S=left,P=sitting]
  35. do -refused(turn)  [env]
likelihood 1 over 17 sampled steps (18 env rows — exogenous input, not chance)
llp> why done(go) (last produced by event 12) — not present now: 13 of 36 occurrences
   0 |  0 #init  (the base state)
   1 |  1 do +cmd_sit
   2 |  2 sit[P=standing]  L113: sit [dyn] : cmd_sit * posture(P) * other(P, sitting) * $floor_dry -o posture(sitting) * done(sit).
   3 |  3 do -done(sit) +cmd_go(kitchen)
   4 |  4 go_closed[P=kitchen]  L145: go_closed [dyn] : cmd_go(P) * $mapped(P) * $closed(P) -o refused(go).
   5 |  5 do -refused(go) +cmd_stand
   6 |  6 stand[P=sitting]  L107: stand [dyn] : cmd_stand * posture(P) * other(P, standing) * $battery_ok -o posture(standing) * done(stand).
   7 |  7 do -done(stand) +cmd_go(tag3)
   8 |  8 go[P=tag3]  L141: go [dyn] : cmd_go(P) * idle * $posture(standing) * $mapped(P) * $open(P) -o moving(P) * progress(go).
   9 |  9 do -progress(go) +cmd_find(keys)
  10 | 10 find_busy[T=keys,P=tag3]  L167: find_busy [dyn] : cmd_find(T) * $moving(P) -o refused(find).
  11 | 11 do -refused(find) +arrived(tag3)
  12 | 12 arrive[P=tag3,Q=door]  L155: arrive [dyn] : moving(P) * arrived(P) * at(Q) -o at(P) * idle * done(go).
  pruned: 23 irrelevant events: 13 do -done(go) +cmd_move(backward), 14 move_wall[W=backward], 15 do -refused(move) +cmd_find(extinguisher), 16 find[T=extinguisher], 17 do -progress(find) +cmd_query(chair), 18 query_seen[T=chair], 19 do -done(query) +locked_away(extinguisher), 20 find_locked[T=extinguisher], 21 do -refused(find) +cmd_follow, 22 follow, 23 do -progress(follow) +cmd_stop, 24 stop_follow, 25 do -cancelled(follow) -done(stop) +cmd_unknown, 26 unknown, 27 do -refused(unknown) +cmd_paw, 28 paw, 29 do -done(paw) -battery_ok +battery_low +cmd_find(bottle), 30 find_low[T=bottle], 31 do -refused(find) +cmd_sit, 32 sit[P=standing], 33 do -done(sit) +cmd_turn(left), 34 turn_down[S=left,P=sitting], 35 do -refused(turn)
llp> why refused(find) (last produced by event 30) — not present now: 31 of 36 occurrences
   0 |  0 #init  (the base state)
   1 |  1 do +cmd_sit
   2 |  2 sit[P=standing]  L113: sit [dyn] : cmd_sit * posture(P) * other(P, sitting) * $floor_dry -o posture(sitting) * done(sit).
   3 |  3 do -done(sit) +cmd_go(kitchen)
   4 |  4 go_closed[P=kitchen]  L145: go_closed [dyn] : cmd_go(P) * $mapped(P) * $closed(P) -o refused(go).
   5 |  5 do -refused(go) +cmd_stand
   6 |  6 stand[P=sitting]  L107: stand [dyn] : cmd_stand * posture(P) * other(P, standing) * $battery_ok -o posture(standing) * done(stand).
   7 |  7 do -done(stand) +cmd_go(tag3)
   8 |  8 go[P=tag3]  L141: go [dyn] : cmd_go(P) * idle * $posture(standing) * $mapped(P) * $open(P) -o moving(P) * progress(go).
   9 |  9 do -progress(go) +cmd_find(keys)
  10 | 10 find_busy[T=keys,P=tag3]  L167: find_busy [dyn] : cmd_find(T) * $moving(P) -o refused(find).
  11 | 11 do -refused(find) +arrived(tag3)
  12 | 12 arrive[P=tag3,Q=door]  L155: arrive [dyn] : moving(P) * arrived(P) * at(Q) -o at(P) * idle * done(go).
  13 | 13 do -done(go) +cmd_move(backward)
  14 | 14 move_wall[W=backward]  L131: move_wall [dyn] : cmd_move(W) * $posture(standing) * $wall(W) -o refused(move).
  15 | 15 do -refused(move) +cmd_find(extinguisher)
  16 | 16 find[T=extinguisher]  L163: find [dyn] : cmd_find(T) * idle * $battery_ok -o searching(T) * progress(find).
  17 | 17 do -progress(find) +cmd_query(chair)
  18 | 18 query_seen[T=chair]  L217: query_seen [dyn] : cmd_query(T) * $seen(T) -o done(query).
  19 | 19 do -done(query) +locked_away(extinguisher)
  20 | 20 find_locked[T=extinguisher]  L177: find_locked [dyn] : searching(T) * locked_away(T) -o idle * refused(find).
  21 | 21 do -refused(find) +cmd_follow
  22 | 22 follow  L183: follow [dyn] : cmd_follow * idle * $posture(standing) * $person_in_view -o following * progress(follow).
  23 | 23 do -progress(follow) +cmd_stop
  24 | 24 stop_follow  L203: stop_follow [dyn] : cmd_stop * following -o idle * done(stop) * cancelled(follow).
  25 | 25 do -cancelled(follow) -done(stop) +cmd_unknown
  26 | 26 unknown  L227: unknown [dyn] : cmd_unknown -o refused(unknown).
  27 | 27 do -refused(unknown) +cmd_paw
  28 | 28 paw  L135: paw [dyn] : cmd_paw * $leg_ok -o done(paw).
  29 | 29 do -done(paw) -battery_ok +battery_low +cmd_find(bottle)
  30 | 30 find_low[T=bottle]  L165: find_low [dyn] : cmd_find(T) * $battery_low -o refused(find).
  pruned: 5 irrelevant events: 31 do -refused(find) +cmd_sit, 32 sit[P=standing], 33 do -done(sit) +cmd_turn(left), 34 turn_down[S=left,P=sitting], 35 do -refused(turn)
llp> stage (done)
  at              (tag3)
  battery_low     ·
  clear           (forward)
  closed          (kitchen) (window_chair)
  floor_dry       ·
  free            (around) (left) (right)
  idle            ·
  leg_ok          ·
  mapped          (door) (kitchen) (tag3) (window_chair)
  open            (door) (tag3)
  person_in_view  ·
  posture         (sitting)
  seen            (chair) (table)
  unmapped        (sofa) (tag5)
  unseen          (bottle) (extinguisher) (keys)
  wall            (backward)
llp> ```
