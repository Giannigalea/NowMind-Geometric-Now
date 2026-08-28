# G2.3.2 Regime A Chronological Win Analysis

Frozen Regime A remains unchanged: Chronological `8`, NowMind `0`, ties `242`.

All eight C wins were action-choice cases in the `H50` cohort. In each case the NowMind output parsed successfully and usually selected the right action, but gave the wrong status and source label, commonly `CONTRADICTORY` plus `hypothetical_future`. Chronological gave an `ACTION` status, so it scored correct.

Categories used: B NowMind too verbose; C NowMind fragments causal context; D model follows chronology more naturally; F source-label misunderstanding; G token/context pressure.

| Trial | Family | History | Categories | Short diagnosis |
| --- | --- | --- | --- | --- |
| `g2_3_eval_00044_action_choose_next_move` | action_choose_next_move | H50 | B,C,D,F,G | N chose the action but wrong status/source; C kept an action-like sequence the tiny model followed. |
| `g2_3_eval_00062_action_safe_vs_conditional_route` | action_safe_vs_conditional_route | H50 | B,C,D,F,G | N chose the action but wrong status/source; C kept an action-like sequence the tiny model followed. |
| `g2_3_eval_00080_action_verify_scan_vs_act` | action_verify_scan_vs_act | H50 | B,C,D,F,G | N chose the action but wrong status/source; C kept an action-like sequence the tiny model followed. |
| `g2_3_eval_00098_action_after_hidden_change_observed` | action_after_hidden_change_observed | H50 | B,C,D,F,G | N chose the action but wrong status/source; C kept an action-like sequence the tiny model followed. |
| `g2_3_eval_00146_action_choose_next_move` | action_choose_next_move | H50 | B,C,D,F,G | N chose the action but wrong status/source; C kept an action-like sequence the tiny model followed. |
| `g2_3_eval_00182_action_verify_scan_vs_act` | action_verify_scan_vs_act | H50 | B,C,D,F,G | N chose the action but wrong status/source; C kept an action-like sequence the tiny model followed. |
| `g2_3_eval_00200_action_after_hidden_change_observed` | action_after_hidden_change_observed | H50 | B,C,D,F,G | N chose the action but wrong status/source; C kept an action-like sequence the tiny model followed. |
| `g2_3_eval_00248_action_choose_next_move` | action_choose_next_move | H50 | B,C,D,F,G | N chose the action but wrong status/source; C kept an action-like sequence the tiny model followed. |

No case shows evaluator-truth leakage, omitted relevant Regime-A information, or a scoring bug. The evidence points to the tiny model handling chronological action phrasing more naturally than the explicit NowMind action/source structure.
