# Adapting a Skill (make an existing skill yours)

Read `skill-standards.md` first. Use this whenever the target skill **already exists**: it arrived generic from a
pack, it has drifted away from the project, it never triggers, or it works but not the way this team works.

Adapting is the most common thing anyone does to a skill, and the easiest to do badly. The failure mode is not
timidity, it is **over-reach**: an agent handed "improve this skill" rewrites the whole file, and the author loses
the version they had already tuned. Change what was asked for. Report what moved.

## Step 1 - Read the target and keep a baseline

Read the entire `SKILL.md` plus every file it bundles. An adapt decided from a skim will duplicate something that
is already three sections down.

Then preserve the original, because step 5 compares against it:
- **Repo is clean:** the git history *is* the baseline. Say so; don't litter the folder with copies.
- **Repo is dirty, or the skill is untracked:** copy it aside (`SKILL.md.bak`) and **delete the copy once the
  change is accepted.** Two files that both look like skills in one directory is its own bug: only the real
  `SKILL.md` is loaded, but a stray `SKILL.md.bak` confuses every human who opens the folder next.

Note what the skill currently does well. That list is what must survive.

## Step 2 - Interview

Never start editing from a one-line ask. "Make it better" and "make it mine" carry no information about *what*.

Ask in this order, and skip anything `$ARGUMENTS` already answered:

1. **What happened, or what's missing?**
   Get the concrete case, not a category. *"It gave me a plan with no test strategy"* is workable; *"it's not
   thorough enough"* is not. Good probes: "when did it last disappoint you?", "paste the output you didn't like",
   "what did you have to fix by hand afterwards?"

2. **What should it have done instead?**
   This is the part only the author knows, and it is the actual content of the change. Push until it is specific
   enough to write down: not "follow our conventions" but *which* convention; not "run the tests" but the literal
   command and the directory it runs in.

3. **Always, or just this once?**
   A rule the skill should follow on every run belongs in the skill. A one-off belongs in the prompt. Ask it
   plainly, because authors routinely try to encode a preference they held for one ticket. Every permanent line
   costs context on every future run, so it has to earn the slot.

4. **How will we know it worked?**
   Get a case to re-run: a ticket, a file, a prompt. Without one, step 5 is unverifiable and the change ships on
   optimism.

If the author cannot answer question 2, the change isn't ready. Say so, and offer to run the skill once on real
work so there is something concrete to react to. That is a better use of the turn than guessing.

## Step 3 - Route to a change pattern

Match the interview's answers to the pattern below, and **say which one you're applying** before you edit. Naming
the pattern is what keeps the change scoped, and it teaches the author to reason about their own skills.

### Retarget (it never fires, or fires on the wrong things)

The problem is the `description`, not the body. Claude decides from metadata alone, and it **under-triggers**: a
skill that reads like a summary rarely fires.

- Write the description as a **routing rule**, not a synopsis: what it does, when to fire, and the literal phrases
  the user actually says.
- For genuine under-triggering, be a little pushy: *"Use this whenever the user mentions X, even if they do not
  explicitly ask for Y."*
- For over-triggering, add exclusions (*"Do NOT use for ..."*), tighten the wording, or set
  `disable-model-invocation: true` if it should only ever be run by hand.
- `when_to_use` can carry extra trigger phrases; it is appended to `description` in the listing and counts toward
  the same character cap, so it is a place to put triggers, not a place to be verbose.
- Descriptions are truncated when many skills are installed, so **put the key use case first.**

Verify by describing the task in the author's own words in a fresh session and confirming the skill loads.

### Localize (it runs commands this project doesn't have)

The classic symptom of a skill taken from a pack: plausible commands that are wrong here. Wrong test runner, wrong
entry point, wrong port, a tool that isn't a dependency, POSIX-only utilities on a Windows machine, or the right
command run from the wrong directory.

**Do not transcribe the commands from memory or from the README. Run them.** A localized skill that was never
executed is the same bug with new values. Where the working directory matters, state it in the skill: a monorepo
step that silently runs from the repo root will fail in a way the author reads as "the skill is broken."

### Encode conventions (it ignores how this team works)

Add the constraints a generic skill cannot know: the two-approaches rule, the out-of-scope discipline, the testing
strategy, the architecture boundaries, what always has to be surfaced before it commits to an approach.

Keep them as a short explicit block rather than sprinkling them through the body, so the author can find and edit
them later. Write each as a checkable instruction ("propose two approaches before committing to one"), not an
aspiration ("be thorough").

### Add an interview (it guesses instead of asking)

Most skills inherit a vague line like *"ask the user if anything is unclear."* An agent almost never finds itself
unclear, so that line does nothing. Replace it with a real gate:

- Name the two or three decisions that actually shape the output.
- Place the gate **before** the expensive step, not after.
- Say explicitly that it must wait for the answers before continuing.

This is the same move this skill applies to itself, one level up.

### Compose (it should be driving other primitives)

Have the skill dispatch subagents, run a CLI, or call an MCP tool instead of doing everything inline. The common
win is a research fan-out before an expensive step: exploration happens in the subagents' context and only the
findings come back.

What makes a fan-out actually fire, verified in practice:
- **name the agents in backticks**,
- say **"in parallel, in a single message"**,
- add **"wait for both to report back before continuing."**

Vaguer phrasing ("use subagents when beneficial") reliably produces no subagent at all.

### Shape the output (right process, wrong artifact)

Move the output format into `templates/` and add a **mandatory-read** line at the step that produces output
("Before producing output, read `templates/<x>.md` and follow it exactly"). A format left as a lazy pointer gets
skipped, and the output silently changes.

Before templating a **stateful** section (status markers, a progress checklist, an amendments log), name what
keeps it current. A section nothing maintains is dead weight that quietly lies to the reader.

### Split and trim (the body is long and mostly rarely needed)

The structural pattern, formerly the whole "refactor" mode. Full runbook with a before/after:
`refactoring-skills.md`. Reach for it when the *shape* is the problem, not the behavior: the body is paid for on
every use, and most of it is only sometimes needed.

Do not fold a split into a behavior change in one pass. Split first, verify behavior is unchanged, then make the
behavior change as a separate step, or neither will be reviewable.

## Step 4 - Make the smallest change that does it

Edit in place. Preserve everything the interview didn't justify touching, including wording the author may have
tuned deliberately.

**When a rewrite really is the answer** (the skill is the wrong type for its job, or its process is fundamentally
not what the author wants), say that plainly, explain why an edit won't get there, and get agreement before
starting. Do not arrive at a rewrite by accident.

Report the change as a short list of what moved and why. "Improved the skill" is not a report.

## Step 5 - Verify the change is real

Two checks, both required:

1. **The new behavior happens.** Re-run the case from interview question 4 and confirm the specific thing the
   author asked for. A retarget is verified by the skill loading from a natural request in a **fresh session**;
   leftover context from the editing session will mask a description that doesn't actually work.
2. **Nothing else broke.** The parts noted in step 1 still behave the same. This is the adapt equivalent of a
   refactor's behavior-preservation check, and it is where over-reach gets caught.

Then run `validation.md`. **Gate 5 (change verification) is non-negotiable.**

## Worked example

**Ask:** *"make the planning skill mine."*

**Interview:** it produces plans with no test strategy, and it never asks which approach the author wants (Q1). It
should always propose two approaches and always state how the change will be tested (Q2). Always, on every ticket
(Q3). Re-run it on last week's ticket and see both (Q4).

**Patterns:** *Encode conventions* (the two rules) plus *Add an interview* (the approach question, gated before
planning). Not *Localize*, not *Split and trim*: nothing in the interview pointed there.

**Change:** a four-line constraints block, and the vague "ask if unclear" line replaced with a gate that asks
which of the two approaches to take and waits for the answer.

**Verify:** re-run on the real ticket. Both rules appear, the gate fires, and the rest of the plan is recognizably
the same skill.

Note what did *not* happen: no restructure, no new references, no reworded description. The skill triggered fine
already, so retargeting it would have been change for its own sake.
