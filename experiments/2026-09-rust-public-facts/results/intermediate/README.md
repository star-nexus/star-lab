# Incorrect fixture expectation, not a gameplay regression

The first targeted run at290de0a returned full results equal to Python, but its new test incorrectly expected all37mapped tiles to be emitted. Historical oracle behavior excludes external entity ID0, yielding36tiles.94f7b0c changes only the expected counter to the oracle visible list length. No runtime code changed or wheel rebuild required. The retained log is diagnostic, excluded from final validation; targeted-fixed.log is the89-test passing run. All other cases in the first run passed.
