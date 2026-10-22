# Fluid Mechanics study notes

Open [index.html](index.html) in a browser. Keep the `assets` folder beside the HTML files for offline reader controls and mathematics. Recording and external source links require internet access.

The learning route connects all seventeen chapters. Each chapter states its model assumptions, source boundaries, executable checks, exercises and worked solutions. The [numerical laboratory](numerical-lab.html) adds two constructed-model studies and links to every chapter example.

Run `python numerical_lab.py` from this folder. The downloadable laboratory uses only the Python standard library and was checked with Python 3.13.5. It prints refinement errors and deliberate sign-error probes, ending in PASS when its internal checks succeed. Chapter examples list their own imports; some require NumPy.

The studies check implementation against prescribed fields and an exact laminar profile. They do not validate real flows, predict transition or resolve entrance development. [reader-validation.json](reader-validation.json) records the local reader validation scope and results; it should be read with the source qualifications in each chapter and the [source map](source-map.html).
