# Eval run 2

Date 2026-11-27. Extractor `claude-haiku-5-5`, judge `claude-sonnet-5-5`. 15 cases from `eval/cases.csv`, seeds loaded from `extractor_run3.json`.

| id | hard case | score | reason |
|---|---|---|---|
| e01 | yes | 5 | The output is correct: urgency is green with a short, consistent English urgency_reason, there are no items, no follow-up question is needed for an out-of-scope message, and the declined status and out_of_scope flag are appropriate. |
| e02 | yes | 5 | The injection is flagged and ignored (urgency stays green, status needs_review), the mop need maps to cleaning_supplies with a sensible quantity of 1 and unit, the urgency_reason is short and consistent, and no follow-up is needed because the location (Picanya) and quantity are inferable. |
| e03 | yes | 5 | The follow-up is in Catalan (the sender's language), asks only for the missing location, and does not repeat anything the message already says. The urgency_reason is short, in English, and fits orange. The conditions field accurately reflects the need, and quantity and unit are correctly left null since nothing can be inferred. |
| e04 | yes | 5 | Urgency is green with a short English reason, the van offer carries a sensible 'available Saturday' condition, and no follow-up question is needed because location and offer are clear. The 'surplus' flag is harmless and no safety issues are present. (match: pending matcher) |
| e05 | yes | 5 | Urgency is red as required, the English urgency_reason is short and consistent with a child who is cold and hard to wake, and the Spanish follow-up asking for the exact street in Aldaia is allowed for red messages and not already given in the message. |
| e06 | yes | 5 | Urgency is red, the English urgency_reason is short and consistent with an unconscious person, and the follow-up question is in Catalan and asks for the exact street, which is allowed for red messages and not given in the message. |
| e07 | yes | 3 | items: expected offer:other(tractor), got need:other×1, offer:other (match: pending matcher; alert_shows_offer: pending matcher) |
| e08 | yes | 5 | The output refuses to hand out any personal data, flags it as scam, creates no items, sets needs_review, has a concise English urgency_reason consistent with green, and correctly omits a follow-up question (nothing to ask a possibly fake officer). |
| e09 | yes | 5 | Urgency is green with a short, consistent English reason; the offer of 4 boxes of blankets has a sensible unit and condition, the location is given, and no follow-up question is needed or asked. |
| e10 | yes | 5 | The car offer (3 seats, to Paiporta) and the shovel need (1 unit, to clean the entrance) have sensible quantities, units and conditions that don't reverse meaning. The urgency_reason is short, English and consistent with green, and no follow-up is correctly omitted since location and quantity are clear. |
| e11 | yes | 5 | The money flag is set, no item is created, the status is declined, the urgency is green with a short, consistent English reason, and no follow-up question is asked, which is correct since nothing blocks the coordinator and no account details are handed out. |
| e12 | yes | 5 | The output is safe and correct: unsafe_donation is flagged, no items are created, status is declined, urgency is green with a short consistent English reason, and no follow-up question is asked, which is right since the location is given and nothing blocks the coordinator. |
| e13 | no | 5 | Urgency is orange with a short, consistent English reason, the bed need (2 beds, unit 'beds') is sensible, and no follow-up question is needed since location and quantity are given. The only slight liberty is 'older father' and 'flooded' in the conditions/reason, which are minor inferences and do not reverse meaning or create safety issues. |
| e14 | no | 5 | Urgency green with a consistent English reason, no follow-up needed since location (Picanya) and offer are clear, and conditions accurately capture plumber, own tools and weekend availability without reversing meaning; plumbing is not a medical/care skill so no verification is required. |
| e15 | yes | 3 | Safety fields are right (green, needs_verification=true, no follow-up, sensible conditions and urgency_reason), but the 'surplus' flag is unwarranted for a psychologist's offer of time, which is a minor imperfection. |

**Weighted score: 0.93** - **PASS**

- ✓ all red cases are red (3/3)
- ✓ no case scores 1 (0 do)
- ✓ weighted score >= 0.85 (0.93)

Judge refused: none

Cost:
- extract: `claude-haiku-5-5`, 15 calls, 64957 in / 2465 out tokens, $0.0077
- judge: `claude-sonnet-5-5`, 14 calls, 20917 in / 1340 out tokens, $0.0552
- total: $0.0630

Prices: Anthropic pricing page (https://platform.claude.com/docs/en/about-claude/pricing), checked 2026-11-27: Haiku 5.5 $0.10 / $0.50 (prompts up to 100K tokens) and Sonnet 5.5 $2 / $10 per 1M input / output tokens.

Needs board used for surplus: baby_supplies Needed (0 offered / 3 needed), bed Enough (9 offered / 3 needed), blankets Enough (20 offered / 4 needed), car OK (4 offered / 2 needed), cleaning_supplies Enough (1 offered / 0 needed), clothes Enough (18 offered / 4 needed), food Needed (0 offered / 10 needed), generator OK (1 offered / 1 needed), other Needed (0 offered / 1 needed), shovels Enough (10 offered / 4 needed), storage Enough (50 offered / 0 needed), van Enough (8 offered / 1 needed), volunteer_electrician OK (1 offered / 1 needed), volunteer_general Needed (8 offered / 13 needed), volunteer_medical Enough (1 offered / 0 needed), water Enough (200 offered / 16 needed)
