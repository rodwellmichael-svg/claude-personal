# 04 — Projections & Scenarios

Numbers from [`janeys-pension-projections.xlsx`](../janeys-pension-projections.xlsx).
Based on: **£3,600 gross/year** (the non-earner max), **12 years** (age 53→65),
starting pot **£0**, charges **0.5%/year**, medium risk. **Illustrative, not guarantees.**

## How the model works

Each year's £3,600 is invested and grows at the assumed net rate; the pot at 65 is then
turned into income via ~4% drawdown (or a rough annuity), on top of the State Pension
and the deferred DB pension once those start.

## Pot at retirement (age 65)

| Scenario | Net growth | Pot at 65 (future money) | ≈ in today's money |
|----------|-----------|--------------------------|--------------------|
| Cautious | 2.5% | **£50,900** | ~£37,900 |
| **Central** | **4.5%** | **£58,200** | **~£43,300** |
| Optimistic | 6.5% | **£66,600** | ~£49,500 |

*Of the £58,200 central pot, £43,200 is Janey's contributions and ~£15,000 is growth.*
*(Today's-money column divides by 1.025^12 ≈ 1.34 for 2.5% inflation.)*

## What the central pot provides as income

| From the pot | Amount |
|--------------|--------|
| Tax-free cash (25%, from age 65) | **£14,500** (one-off) |
| Sustainable drawdown (~4%/year) | **~£2,300/year** |
| *or* a rough annuity (~6%/year) | ~£3,500/year |

## Total annual income

| Component | Age 65–66 (bridge) | Age 67+ (State Pension starts) |
|-----------|--------------------|-------------------------------|
| Private pension (drawdown) | ~£2,300 | ~£2,300 |
| Deferred DB (school) pension | *to trace* | *to trace* |
| State Pension (if full) | £0 | £11,973 |
| **Total** | **~£2,300/year** | **~£14,300/year** |

## What this tells us

1. **The State Pension does the heavy lifting.** ~£12,000 of the ~£14,300 total comes
   from the State Pension — which is exactly why **securing the full amount (filling any
   NI gaps) is the highest-value action**, worth far more than tweaking the pot.
2. **The private pot is a useful top-up, not the foundation.** £3,600/year for 12 years
   is real money (and the tax relief is free), but on its own it adds only ~£2,300/year
   of income. That's the honest picture of starting at 53 with the non-earner cap.
3. **The 65–67 bridge is thin.** With only ~£2,300/year from the pot before the State
   Pension starts, those two years need the household's income, savings, or a larger
   early drawdown. Worth planning deliberately.
4. **The DB pension will improve this.** Once traced, the school pension adds guaranteed,
   inflation-linked income on top — update cell `Inputs!B32` and the totals refresh.
5. **This is Janey's slice, not the household's.** Combined with the husband's pension
   and income, and a **£500k mortgage-free home**, the couple's overall position is much
   stronger than Janey's standalone figures suggest.

## Against the benchmarks (single person, today's money)

Janey's own ~£13,700/year in today's money (State Pension + drawdown) sits around the
PLSA **"Minimum"** single-person standard (~£13,400). Reaching **"Moderate"** (~£31,700)
as an individual isn't realistic from this pot alone — that comes from the **household**
picture (both pensions + assets), which is the right frame for the couple.

## Levers to improve the outcome (change these in the spreadsheet)

- **Secure full State Pension** → set `Inputs!B30` to 100% only once the forecast confirms it; fill gaps if not.
- **Trace the DB pension** → enter it in `Inputs!B32`.
- **Retire slightly later / bridge differently** → change `Inputs!B6`.
- **Lower charges** → `Inputs!B21`; even 0.3% vs 0.5% helps over 12 years.
- **Household contributions** → consider the husband's allowance and ISAs (outside this model).

> Revisit the spreadsheet yearly and after any change in income, contributions, or the
> State Pension forecast.
