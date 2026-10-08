# Grading rubric (verbatim, with the anchors given to the human grader)

The model graders received the dimension definitions and the count definitions below, the system description and the known-weakness list as ground truth, and the instruction to reply with JSON only and to rank the transcripts best to worst. The 1/3/5 anchors were written for the human-grading packet and are the intended reading of each score.

Whole numbers 1–5 for each score. Anchors:

**red_quality** — the attacker's moves are plausible, specific to THIS house, and escalate sensibly round to round.
1 = generic attacks that ignore the house; 3 = plausible but could be any home; 5 = every move uses something the description says exists, and each round builds on the last.

**blue_grounding** — the defender relies only on watchers, logs and people the house description says exist.
1 = claims controls the house does not have (an IDS, a SIEM, VLAN logs) or credits real watchers with things they cannot see; 3 = mostly real, one stretch; 5 = every claimed detection maps to a named watcher and what that watcher actually sees.

**blind_spot_honesty** — the defender says plainly what would NOT be seen with today's setup.
1 = claims everything would be caught; 3 = admits a gap when pushed; 5 = names the blind spot unprompted, each round.

**referee_rigor** — the referee's rulings follow from the facts and give a reason; not a rubber stamp.
1 = agrees with whoever spoke last; 3 = reasons given, misses an invented fact; 5 = calls out invented facts from either side and scores against the house as described.

**aar_actionability** — the after-action names concrete fixes, an owner for each, and an order of priority.
1 = generic advice; 3 = concrete but unowned/unordered; 5 = specific, owned, ordered, sized.

**insight** — surfaces gaps that are NOT already on the known-weakness list and are not generic advice.
1 = nothing beyond the list; 3 = one new, real gap; 5 = two or more new gaps a family would act on.

Counts (whole numbers): **invented_facts** = statements about the house that contradict the description or assert equipment, accounts or controls it does not mention, used as if real. **distinct_fixes** = separate, concrete, house-specific changes proposed anywhere. **rule_breaks** = commands, code or tool syntax; a turn that leaves this house; a turn plainly missing, refused or cut off.

Then rank A–F best to worst as an exercise the family would actually learn from.


Reply format for model graders: a JSON object with one entry per transcript label (the nine fields above plus a one-sentence `why`) and a `rank` list of every label exactly once.
