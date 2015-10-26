# TempCauseRelPro
Temporal and Causal Relation extraction modules for the Newsreader project.

Check test.sh on how to use both modules (TempRelPro and CauseRelPro) to extract relations between events, given the dataset in column format (e.g. Wikinews dataset in 'data' directory).

The path to YAMCHA (executable file) must be set in both `temprel-pipeline-per-file.sh` and `causalrel-pipeline-per-file.sh` files, e.g.
```
yamcha="../../../Dropbox/PhDStuff/Event_Relation/tools/fbk/yamcha-0.33/usr/local/bin/yamcha"
```
