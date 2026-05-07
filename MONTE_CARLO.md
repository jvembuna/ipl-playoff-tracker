# Monte Carlo Simulation

## What This Means

Monte Carlo simulation is a simple way to answer a question like this:

`What might happen if we played the rest of the season many times?`

Instead of trying to guess the one true future, the app plays out many possible futures.

## Simple Example

Imagine there are only 2 matches left.

- Match 1: Team A vs Team B
- Match 2: Team C vs Team D

We do not know who will win, so we let the computer make a lot of random trials.

One trial might look like:

- Team A wins
- Team D wins

Another trial might look like:

- Team B wins
- Team C wins

If we repeat this many times, we can count:

- how often each team finishes in the top 4
- how often each team misses out

That count becomes the qualification percentage.

## How This App Uses It

For this IPL tracker, one simulation run does this:

1. Start from today's standings
2. Look at all remaining matches
3. Pick a winner for each match using the chosen probability
4. Update points
5. Update NRR with a small simulated change
6. Rank the teams
7. Mark the top 4 as qualified

Then the app repeats that process thousands of times.

## Why We Repeat It So Many Times

One random run does not tell us much.

But if we run the season:

- 1,000 times
- 5,000 times
- 10,000 times

then patterns start to appear.

Example:

- if CSK qualifies in 7,400 out of 10,000 runs
- then CSK's qualification chance is about `74%`

## Why This Is Useful

Cricket still has uncertainty.

Even if one team looks strong, there are many different paths through the remaining matches.

Monte Carlo simulation helps answer:

- who is almost safe
- who is in danger
- who still has a tiny mathematical chance

## How Match Probabilities Work

By default, every remaining match starts at `50/50`.

That means both teams are given the same chance to win.

The sliders let you change that.

If you move a slider to `70/30`, the simulation will pick the first team more often than the second team.

## How NRR Works In This App

The app uses NRR as a tie-break when teams finish on the same points.

For future simulated matches, it does not recompute official NRR from runs and overs.

Instead, it uses a simple simulation rule:

- winner gets a small positive NRR change
- loser gets a small negative NRR change

The size of that change is random, but usually small.

This keeps the app simple while still making NRR matter.

## Why This Is Still Only A Model

This app is not claiming to predict the future exactly.

It is a model.

That means:

- it is useful
- it is explainable
- it is still an approximation

Real cricket can always surprise us.

## One-Sentence Summary

Monte Carlo simulation means:

`Play the rest of the season in the computer many times, then count what happens most often.`
