# DOI archive preparation — no DOI assigned

This file prepares a possible future public release; it does not claim that
a GitHub repository, release, Zenodo record or DOI already exists. The
current repository is a local release candidate; no public release or DOI exists yet.

## Required before any public archive

1. Confirm the software authors and their order in `CITATION.cff`.
   The manuscript author list alone does not establish software authorship.
2. Obtain the rights holders' decision on a public code license. The
   current `LICENSE` grants no redistribution rights.
3. Review the public file inclusion list. Keep `.private_review/`,
   `outputs/`, original Java/Python research source, observed workbooks,
   private settings, and local paths out of the public release.
4. The user's current publication instruction covers this repository,
   including its limited Fig. 3(e) aggregate. Check that aggregate in
   the release candidate. Actual pseudo-hindcasts, accepted
   Historical-like/Extreme-dry scenarios, and other figure/table
   numeric files remain outside the authorized public scope.
5. Resolve the source–manuscript version questions in
   [implementation scope](implementation_scope.md). Preserve the precise
   research commit/configuration used for each result if a claim of
   numerical reproduction is intended.
6. Run the documented demos and tests on the candidate release commit,
   record Python version and output checksums, and check the archive
   contents for restricted files.
7. After authorization, create a versioned GitHub release and connect
   the **approved** public repository to a DOI archive service. Copy the
   DOI assigned by that service into `CITATION.cff`, the README and the
   manuscript/reviewer response. Never invent or pre-fill one.

## Current release gate

| Gate | Status |
| --- | --- |
| Public demonstration code and documentation | Prepared locally |
| Tests on current draft | See [audit record](final_audit.md) |
| Rights-approved license and software authorship | Pending |
| Locally included study-derived material | Fig. 3(e) 36-point aggregate only; public release still requires rights review |
| GitHub release and public URL | Not created |
| DOI | Not assigned |
| Exact manuscript result reproduction | Not supported by public materials |

The publication decision belongs to the authors and rights holders. The
demonstration may be archived on its own only if its scope is described
honestly; such an archive would still leave several G8 data/code requests
unmet.
