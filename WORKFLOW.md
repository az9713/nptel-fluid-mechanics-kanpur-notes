# Lecture-note production workflow

This textbook rewrite uses a transcript-grounded lecture-note workflow. The actual
skills applied are `transcript-grounded-textbook`, `rigorous-explainer`, and
`science-editor`. The course recordings provide the chronological spine.
Definitions, derivations, worked examples and research extensions are original
exposition with separate evidence labels.

The nine passes are recorded through the source manifests, chapter sidecars,
accepted-body digests and validation artifacts:

1. Identify the actual course and enumerate the playlist. Preserve recording
   positions and lecture labels, including the seven lectures split into two parts.
2. Acquire preferred transcripts and source evidence. Record caption provenance,
   hashes, durations, segment boundaries and acquisition limitations. Publisher
   caption labels do not establish how the captions were produced.
3. Read complete assigned transcripts sequentially and develop chapter claims,
   prerequisites and notation. Titles alone are insufficient source material.
4. Inspect primary sources at the actual pages, sections and figures required
   by a claim. Record unavailable material and restrict claims accordingly.
5. Write substantial textbook exposition directly in HTML, with stated model
   assumptions, runnable constructions and six fully worked problems per chapter.
6. Complete independent scientific editing, source/visual review and citation
   checks. Authors cannot accept their own scientific manuscripts. Repairs are
   rebound to the exact accepted body; scientific changes require renewed review.
7. Check textbook parity, chronological coverage and consistency across the
   entire book, including stress conventions, reference frames, force signs,
   dimensional definitions and the limits of empirical correlations.
8. Build the shared reader without rewriting authored bodies. Reuse local CSS,
   JavaScript and MathJax assets; verify digests, links, timestamps, executable
   listings, solutions, controls and desktop/mobile rendering offline.
9. Check the assembled package and retain local Git checkpoints. Publication
   requires a separate instruction. Keep raw media, transcripts, downloaded
   papers and private acquisition/editorial records outside the book repository.

Chapter assignments preserve author ownership; a separate scientific editor
reviews stable manuscripts, followed by repairs and renewed review as required.
Accepted authored-body hashes are preserved through reader wrapping and final
assembly. Chapter 2 retains its historical acceptance at commit `036936b`:
its legacy review has no hash header, and no retrospective header or new review
has been invented. Both normalized and preserved-newline body hashes are recorded
in [completion.json](completion.json).

Six worked solutions in each of 17 chapters give 102 chapter problems. The
numerical lab adds two constructed-model studies: finite-volume continuity for
a prescribed field, and quadrature and force closure for an exact laminar-pipe
profile. Its downloadable code and numerical audit use the Python standard
library; some chapter listings use NumPy. Synthetic values are teaching
constructions, not inferred empirical measurements. These checks do not validate
real flows, predict transition or resolve pipe entrance development.

Independent review accepted each chapter and the supporting learning route and
laboratory. The final assembled-book audit verifies acceptance records and
mechanical consistency; it does not constitute a new independent whole-book
mathematical review. Fourteen nonblocking metadata warnings preserve useful
additional revision evidence. Current reader, code, package, source-free export
and publication results are recorded separately in the linked evidence in
[README.md](README.md).

The source videos were intentionally deleted.
Retained publisher captions, selected frames and saved source evidence support
the recorded chapter reviews; current full-media hashes or new video playback
are not asserted. Human accessibility certification is not asserted. Automated
controls and responsive-layout checks, transcript reading, explicitly bounded
primary-source inspection, and any unverified clipboard behavior are recorded
separately.
