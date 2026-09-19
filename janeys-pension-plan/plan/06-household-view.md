# 06 — Household View (Janey + Michael)

Retirement is a **household** outcome, so this pulls Janey and Michael together.
Figures from the **Household** tab of
[`janeys-pension-projections.xlsx`](../janeys-pension-projections.xlsx).
Personal identifiers (account numbers, NI, contact details) are kept out of this repo.

## What we have

| | Janey | Michael |
|--|-------|---------|
| Age | 53 (DOB 05/11/1972) | 57 (DOB 02/07/1969) |
| Target retirement | 65 | 65 (assumed) |
| State Pension | £11,973/yr from age 67 (~2039) | **£241/wk ≈ £12,532/yr**, assumed from **Nov 2039** ⚠️ |
| DB / Teachers' Pension | **£7,085/yr** (£6,982 from age 60) + £20,945 lump sum | none |
| Private pension pot today | ~£0 (starting the £3,600/yr) | **£221,974** (Aegon SIPP) ✅ |
| Projected pot at 65 | ~£58,200 | **~£315,670** (existing pot only, no new contributions) |

> ⚠️ **Michael's State Pension date:** a July-1969 DOB normally gives a State Pension age
> of 67 (~July 2036), not Nov 2039 — confirm at gov.uk/check-state-pension. (It doesn't
> change the steady-state total below, only the timing.)
>
> **Not yet in the model:** Michael's newer **NEST pot** (current employer) and his
> **ongoing contributions** (10% salary sacrifice + employer top-up since Apr 2025) —
> both would push the numbers *higher*. Add his salary to quantify (Inputs cell B41).

## Household income — steady state (both retired, both State Pensions in payment)

| Component | Janey | Michael | Household |
|-----------|-------|---------|-----------|
| Private pension (drawdown ~4%) | ~£2,327 | ~£12,627 | ~£14,954 |
| Teachers' / DB pension | £6,982 | — | £6,982 |
| State Pension | £11,973 | £12,532 | £24,505 |
| **Total annual income** | **~£21,282** | **~£25,159** | **~£46,440** |
|  |  | **≈ per month** | **~£3,870** |

## Against the PLSA couple benchmarks (today's money)

| Standard | Couple / year | Household position |
|----------|---------------|--------------------|
| **Minimum** | ~£22,400 | ✅ **~£24,040 above** |
| **Moderate** | ~£43,100 | ✅ **~£3,340 above** |
| **Comfortable** | ~£59,000 | ❌ ~£12,560 short |

*PLSA couple figures are illustrative — verify at
[retirementlivingstandards.org.uk](https://www.retirementlivingstandards.org.uk/).*

## What this tells us

1. **The household is in good shape — already clearing "Moderate."** ~£46,400/year
   (~£3,870/month), and that's a *conservative* figure: it excludes Michael's ongoing
   contributions and his NEST pot.
2. **Michael's ~£222k pot is the single biggest asset** in the plan, providing ~£12,600/year
   of drawdown — roughly half the household's private-pension-plus-drawdown income.
3. **"Comfortable" (~£59k) is within reach.** The ~£12,560/year gap could be closed by:
   Michael's ongoing 10% salary-sacrifice contributions over the next 8 years, his NEST
   pot, stronger investment growth, and/or working slightly longer. Add his salary to see.
4. **Guaranteed income is a strong base.** Two State Pensions (~£24,500) + Janey's
   Teachers' Pension (~£7,000) = ~£31,500/year secure, inflation-linked — ~68% of the
   household total before any investment risk. That's a resilient foundation.
5. **The £500k mortgage-free home is a backstop**, not counted as income.

## To refine further — Michael's remaining numbers

- [ ] **Michael's salary** → to quantify the 10% salary-sacrifice + employer contributions (Inputs B41)
- [ ] **NEST pot current value** → add to his existing pot
- [ ] **Confirm State Pension date & amount** (the Nov 2039 flag above)
- [ ] Confirm his **target retirement age** (assumed 65) → Inputs B36

## Timing note (the bridge years)

Janey's Teachers' Pension (£6,982/yr + £20,945 lump sum from **age 60**) and Michael's
sizeable pot mean the years before the State Pensions start are well covered. Once the
State Pension dates are confirmed, a year-by-year drawdown plan can sequence: Janey's
Teachers' at 60 → both private pots from 65 → State Pensions when they start.
