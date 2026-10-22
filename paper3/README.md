# Stand-alone Paper 3 review draft

Run `python3 paper3/build_paper3.py` from the repository root. The builder reads
`thesis/ch4_paper3.tex` as the only authority for the shared theory, compiles the
companion papers in a disposable directory to resolve their actual reference
numbers, and moves the shared proof blocks to an appendix. Edit front matter
only in `frontmatter.tex`; never hand-edit the generated `paper3.tex`.

`build_receipt.json` records the authoritative source, front matter, bibliography,
generated TeX and PDF hashes, abstract word count and resolved cross-references.
The builder rejects a source change during generation. The numerical macros
remain generated from the registered recovery result in the thesis checks folder.

This is a working draft. A1 needs a repaired lower-bound statement, matrix
formalization remains scoped, prospective evidence is pending, and bibliography
verification is incomplete. Journal selection and submission remain human tasks.
