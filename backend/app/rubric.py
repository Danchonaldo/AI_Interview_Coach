"""The evaluation rubric shared by the grader prompt, the mock grader and the eval harness.

Each criterion is scored with an integer from 1 to 5.
"""

CRITERIA = ("relevance", "structure", "specificity")

RUBRIC_TEXT = """\
Score each criterion with an integer from 1 to 5.

RELEVANCE - does the answer address the question that was asked, for this role and level?
  1 = off-topic or does not answer the question
  2 = touches the topic but misses the main point of the question
  3 = answers the question partially or generically
  4 = answers the question directly; minor gaps
  5 = answers every part of the question directly and ties it to the target role

STRUCTURE (STAR) - is the answer organised as Situation, Task, Action, Result?
  (For technical/knowledge questions, judge the equivalent logical flow:
   context -> approach/explanation -> outcome or example.)
  1 = no discernible structure, a single vague statement
  2 = some elements present but disordered; no result
  3 = two or three STAR elements present; result missing or vague
  4 = clear STAR flow with a stated result; one element thin
  5 = complete, well-ordered STAR with a clear, preferably measurable result

SPECIFICITY - concrete details: own actions ("I" not "we"), tools, numbers, examples.
  1 = entirely generic, could be said by anyone
  2 = mostly generic, one vague detail
  3 = some concrete details but no numbers or named tools/methods
  4 = concrete actions plus named tools/methods or a number
  5 = rich, verifiable detail: own actions, tools, metrics and outcome
"""
