# director — activation from context as a lifted domain (the canonical base)

`director_domain.llp` is the LIFTED base of the director (metis-agent docs/DIRECTOR.md; built and
measured on ALFWorld in alf-hierarchy s-ee212820, 20/20 by the person's words): a domain whose
output port is the agent's own activation. An INSTANCE names the specialists, what each handles
(`handles/2`, generated from the specialists' declared ports), the results, the ends, the detours
and escalations, the renames the orchestrator's frames use, and the start — and includes this base.

This directory is the base alone, not a package (no manifest): a world's generator writes the
instances (metis-worlds alfworld/world/gen_hier.py `generate_director_package`, `install`); the
loop's refactor (metis-loop pi/policy/hier.py `director_base_path`) reads this file first and a
world's copy after. The worlds carry a COPY of this file (copies, not dependencies: the user's
rule); a test in each world keeps the copy byte-equal to this one.
