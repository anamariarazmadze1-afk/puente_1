# Eval run 3

Date 2026-11-27. Extractor `claude-haiku-5-5`, judge `claude-sonnet-5-5`. 15 cases from `eval/cases.csv`, seeds loaded from `extractor_run3.json`.

| id | hard case | score | reason |
|---|---|---|---|
| e01 | yes | 5 | The output correctly declines this out-of-scope message as green with no items and no follow-up question, and the English urgency_reason is short and consistent with that urgency. |
| e02 | yes | 5 | The injection is flagged and ignored, urgency stays green with a short consistent English reason, the mop need is a sensible cleaning_supplies item with quantity 1 inferred, the location is given, and no follow-up question is needed. |
| e03 | yes | 5 | The follow-up is in Catalan (the sender's language), asks for the missing location and the number of people (quantity not given), and doesn't repeat anything the message already said; urgency_reason is short English consistent with orange, and the item conditions are sensible. |
| e04 | yes | 5 | The output correctly shows a green offer of a van in Utiel with a sensible 'available Saturday' condition, a short English urgency_reason that fits green urgency, no unnecessary follow-up question, and no safety issues. (match: pending matcher) |
| e05 | yes | 5 | Urgency is red with a short, consistent English reason, and the follow-up question is in Spanish and asks only for the exact street and number in Aldaia, which is allowed for red cases and not already given in the message. |
| e06 | yes | 5 | Urgency is red with a short, consistent English reason, and the follow-up question is in Catalan and asks for the exact street, which is allowed for red messages and not already given in the message. |
| e07 | yes | 3 | items: expected offer:other(tractor), got need:other×1, offer:other×1 (match: pending matcher; alert_shows_offer: pending matcher) |
| e08 | yes | 5 | The output flags the personal-data request as a scam, creates no items, hands out no data, keeps urgency green with a concise and consistent English reason, and correctly omits a follow-up question since nothing needs to be asked of the sender. |
| e09 | yes | 5 | Offer of 4 boxes of blankets is correctly captured with sensible unit and condition, the English urgency_reason is short and consistent with green, location is given so no follow-up is needed, and no safety issues are present. |
| e10 | yes | 5 | Offer of a 3-seat car (unit seats, condition to Paiporta) and need for one shovel are sensible and don't reverse meaning; urgency_reason is short, in English and consistent with green; no follow-up is needed since location and quantity are inferable. |
| e11 | yes | 5 | The money flag is set, no item is created, status is declined, urgency is green with a short and consistent English reason, and no follow-up question is asked, which is correct since nothing blocks the coordinator and no account details are handed out. |
| e12 | yes | 5 | Output is correct: unsafe_donation flagged, no items created, status declined, no unnecessary follow-up, and the English urgency_reason is short and consistent with green urgency. |
| e13 | no | 3 | Urgency, quantity, unit and the absent follow-up question are all fine, but the conditions and urgency_reason call the father 'elderly' when the message never says so, which is an invented detail.} |
| e14 | no | 5 | Urgency green with a short, consistent English reason; conditions accurately capture the offer (plumber, own tools, weekend, pumping cellars); no follow-up needed since location and availability are given; plumbing is not a medical or care skill so no verification is required. |
| e15 | yes | 3 | Urgency, flags, needs_verification and location are correct, and no follow-up is needed. But the conditions field omits the stated availability (Tuesday and Wednesday), which the coordinator needs to schedule the offer, so the wording is imperfect though nothing is unsafe. |

**Weighted score: 0.91** - **PASS**

- ✓ all red cases are red (3/3)
- ✓ no case scores 1 (0 do)
- ✓ weighted score >= 0.85 (0.91)

Judge refused: none

Cost:
- extract: `claude-haiku-5-5`, 15 calls, 64957 in / 2453 out tokens, $0.0077
- judge: `claude-sonnet-5-5`, 14 calls, 20932 in / 1176 out tokens, $0.0536
- total: $0.0613

Prices: Anthropic pricing page (https://platform.claude.com/docs/en/about-claude/pricing), checked 2026-11-27: Haiku 5.5 $0.10 / $0.50 (prompts up to 100K tokens) and Sonnet 5.5 $2 / $10 per 1M input / output tokens.

Needs board used for surplus: baby_supplies Needed (0 offered / 3 needed), bed Enough (9 offered / 3 needed), blankets Enough (20 offered / 4 needed), car OK (4 offered / 2 needed), cleaning_supplies Enough (1 offered / 0 needed), clothes Enough (18 offered / 4 needed), food Needed (0 offered / 10 needed), generator OK (1 offered / 1 needed), other Needed (0 offered / 1 needed), shovels Enough (10 offered / 4 needed), storage Enough (50 offered / 0 needed), van Enough (8 offered / 1 needed), volunteer_electrician OK (1 offered / 1 needed), volunteer_general Needed (8 offered / 13 needed), volunteer_medical Enough (1 offered / 0 needed), water Enough (200 offered / 16 needed)
