LeakTrace E1 reader-study kit
1. Give study.html to >= 20 volunteers (any laptop/desktop browser, 100% zoom). Each completes 56 trials (2 languages x 7 offset levels x 4 repetitions, randomised).
2. Each volunteer returns the downloaded responses_*.csv (anonymous random file name).
3. Put all returned CSVs in one folder and run:  python -m eval.reader_study analyse "<folder>/responses_*.csv"
   (trials_key.csv holds the answer key: keep it away from volunteers.)
4. For the PRINTED variant (recommended, closer to the real use): print trial_XXX_L.png / _R.png pairs at 100% scale (3 px/pt = 216 dpi) on a laser printer.
Ethics: anonymous, voluntary, no personal data; get the course instructor's approval before running.
