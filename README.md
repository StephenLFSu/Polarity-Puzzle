# Polarity (Magnets) Puzzle Solver

A constraint satisfaction solver for the Magnets puzzle, Problem 3 of the
[UC Berkeley Fall 2012 Programming Contest](https://people.eecs.berkeley.edu/~hilfingr/programming-contest/f2012-contest.pdf).

It started as a course project and turned into a personal project. Brute force can solve very small boards of size 4x4 (3^8 = 6,561 combinations) quickly, but as the search space increases the problem cannot be solved in reasonable time using this method. To improve runtime, backtracking was implemented, then optimizations such as MRV, forward checking, and incremental constraint tracking were added. Arc consistency was added at some point, but its runtime was worse than a well-tuned forward check, because it re-checked the whole board after every change instead of looking just one step ahead.

The Magnets puzzle is NP-complete [1], so no known algorithm solves every
instance in polynomial time, and the worst case remains exponential. Instead,
this project focuses on practical performance: the results below show the
runtime and number of backtracking calls on the included test boards.

For an n×m board, the search space is at most 3^(n*m/2) assignments. Each magnet
covers two adjacent cells, horizontally or vertically, so a fully covered board
holds n*m/2 magnets, and each magnet can be placed in one of three ways: `+-`,
`-+` or `XX` (empty).

[1] J. Kölker, "The Magnets Puzzle is NP-Complete," *J. Inf. Process.*,
vol. 20, no. 3, pp. 707–708, 2012, doi:
[10.2197/ipsjjip.20.707](https://doi.org/10.2197/ipsjjip.20.707).

## Approach

Backtracking search over magnet orientations (`+-`, `-+`, or empty `XX`), with:

- **MRV (minimum remaining values):** always branch on the magnet with the
  fewest valid orientations, using bucketed sets for O(1) selection.
- **Forward checking:** after each placement, reject the branch if any affected
  row or column can no longer reach its required count.
- **Domain pruning:** recompute the valid orientations of magnets sharing a row
  or column with the one just placed, using a precomputed adjacency list.
- **Incremental trackers:** per-row and per-column counts of placed charges and
  remaining capacity, updated in O(1) on place and undo.
- **Preprocessing:** magnets that can never hold a charge (zero constraints)
  are fixed as empty before the search starts.

## Version history + Results 

Times are for test 9 (16×16) unless noted. "Calls" is the number of
recursive backtrack calls.

Search space for the 16×16 board: 3^128 ≈ 1.2 × 10^61 possible assignments

| Version | 16×16 result                | Calls     | Main change                                                     |
|---------|-----------------------------|-----------|-----------------------------------------------------------------|
| V1      | Stopped manually (too long) | –         | Basic grid-order backtracking                                   |
| V2      | Incorrect on tests 4 and 9  | –         | Row/column validation, zero-constraint pruning                  |
| V3      | Stopped manually (too long) | –         | Pair placeability check, local forward check                    |
| V4      | Did not finish              | –         | Global state arrays updated incrementally                       |
| V5      | Stopped manually (too long) | –         | Full-board forward check on state arrays                        |
| V6      | 175.6 s                     | 3,716,836 | MRV variable ordering + neighbour rescoring                     |
| V7      | 173.1 s                     | 3,716,836 | Forward check scoped to magnet + neighbours                     |
| V8      | 41.5 s                      | 864,785   | Precomputed orientations, single option loop                    |
| V9      | 19.2 s                      | 864,785   | Cached backtracking state, local forward check                  |
| V10     | 21.9 s                      | 864,785   | Readability refactor (`updateTrackers()`); ~14% slower than V9  |

## Running

    python Polarity.py

Runs the nine included test boards and prints each solution.


## Future Plans
May try to add a tester to randomly generate boards and move the test cases outside of the same file