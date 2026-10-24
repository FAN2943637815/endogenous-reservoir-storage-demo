# DOI archive status and future release checks

The reviewed repository is public at
<https://github.com/FAN2943637815/endogenous-reservoir-storage-demo>.
The [v0.1.0 release](https://github.com/FAN2943637815/endogenous-reservoir-storage-demo/releases/tag/v0.1.0)
at commit `6c8e202` was archived by Zenodo with version DOI
[10.5281/zenodo.23614749](https://doi.org/10.5281/zenodo.23614749).
The archive contains the reviewed 55-file demonstration tree. Its DOI does not
imply that restricted research inputs or all G8 materials were deposited.

## Checks for a future version or broader data release

1. Keep the nine software authors and their confirmed order in `CITATION.cff`
   and Zenodo metadata aligned. The repository owner confirmed them after
   the first Zenodo archive was created.
2. Obtain the rights holders' decision on a reuse license if one is intended.
   The current `LICENSE` and corrected Zenodo rights field grant none.
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
7. For each future release, verify the GitHub tag, Zenodo archive file list,
   version DOI, license metadata and citation against the exact public tree.

## Current release gate

| Gate | Status |
| --- | --- |
| Public demonstration code and documentation | 55 files published to GitHub |
| Tests on public demonstration | Four suites, 12 tests passed; see [audit record](final_audit.md) |
| Software authorship | Nine names and order confirmed by repository owner |
| Reuse license | None granted; all rights reserved in GitHub and Zenodo |
| Publicly included study-derived material | Fig. 3(e) 36-point aggregate only; exact submitted-image version unverified |
| GitHub repository and public URL | Created; link above |
| Versioned GitHub release | `v0.1.0`, commit `6c8e202` |
| Zenodo version DOI | [10.5281/zenodo.23614749](https://doi.org/10.5281/zenodo.23614749) |
| Exact manuscript result reproduction | Not supported by public materials |

The DOI identifies the public demonstration only. Actual pseudo-hindcasts,
study scenarios, remaining figure/table numbers, and original optimization
code are still outside its scope. The release ZIP's `CITATION.cff` predates
the DOI assignment and author confirmation; Zenodo metadata and the current
GitHub `main` citation file carry the verified details.
