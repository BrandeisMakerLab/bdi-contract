# BDI Loan Contracts

Source and development home for the equipment loan contract generator used by
the Brandeis Design and Innovation Design Studio Lab.

The generator is a single self-contained HTML file. BDI staff and student workers
fill out a web form, and the page builds a ready-to-sign loan contract PDF in the
browser, applying the conditional contract language automatically.

## Signed contracts

Signed contracts are **not** stored in this repository, and neither is any
generated PDF. They contain borrower personal information and are kept in a BDI
staff Google Drive folder:

[makerlab.fyi/signed-contracts](https://makerlab.fyi/signed-contracts) — the
short address staff are pointed at, and the one the generator displays after
each download. It resolves to this BDI staff Google Drive folder:

[Signed equipment loan contracts (BDI staff only)](https://drive.google.com/drive/folders/1LFolPr3qnAy-fRi3dKAJMmpNst7dcd5K?usp=drive_link)

Access is managed through Google Drive permissions. If you need access, ask a BDI
staff member rather than requesting it through this repository.

## Repository contents

- `index.html` — the generator. Everything runs from this one file: the form,
  the equipment catalog, the contract language, and the PDF builder. It is named
  `index.html` because GitHub Pages serves that name at the site root.

- `Rules.txt` — the **authoritative spec**. Contract wording, form questions, and
  all six conditional rules. When the spec and the code disagree, this file is
  what the contract is supposed to say; fix the code to match it.

- `DS_Lab_Inventory - Data for contract form.csv` — inventory source data: asset
  ID, contract name, **contract category**, dimensions, weight in grams, and
  replacement value for each of the 38 loanable items. The category column drives
  both the drone rules and the type filter in the form.

The BDI letterhead source document is deliberately **not** in this repository.
It embeds a scanned handwritten signature, which must never be committed to a
repository that is or may become public. It lives outside the repo, alongside the
generated contract PDFs.

- `BDI logo v2 white on blue.png` — the logo used in the page header.

- `tools/sync-inventory.py` — regenerates the generator's equipment catalog from
  the inventory CSV. See **Maintaining the lists** below.

## Where the live copy lives

Staff do not open this repository. The copy they actually use sits in the
Checkout_Contracts folder on the BDI shared Google Drive, alongside the signed
contracts and the policy documents.

That Drive folder is treated as **read-only** from here. Publishing a change is a
deliberate manual step: edit and test the HTML in this repository, then copy the
finished file over the Drive copy yourself.

## Using the generator

**Step 1.** Open the hosted page (see **Hosting** below). Nothing to download
or install. Opening `index.html` from a local copy still works as an offline
fallback.

**Step 2.** The generator opens on a **gate screen** asking *"Does this person
have swipe access to the DS Lab?"* The form is not shown until you answer.
**Yes** reveals it. **No** keeps it hidden and shows a notice pointing the
borrower at [makerlab.fyi/moodle](https://makerlab.fyi/moodle) to complete the
training.

Answering again is harmless: a **Change the DS Lab access answer** link at the
bottom of the form returns to the gate, and a part-filled form comes back
untouched. The answer is not printed on the contract.

**Step 3.** Fill in the **borrower information** and **loan details**. Contract
date and loan start date default to today.

**Step 4.** Pick the **equipment**. With 38 items the list is grouped by type,
and there are two ways to narrow it:

- **Search** by name or asset number. Typing `mavic` finds both Mavic models;
  typing `0083` jumps straight to that asset.

- **Filter by type** using the chips — 3D Scanner, Camera Kit, Charging, Drone,
  GPS, VR — each showing how many items it holds.

Filtering only hides rows, so anything you have already checked stays checked and
still lands on the contract. The recap above the list always shows every selected
item, its quantity, the running replacement value, and a count of any selections
the current filter is hiding. Remove an item with the × on its chip.

**Step 5.** Add any **additional users** who will handle the equipment, then
select your own name under **contract creator**.

**Step 6.** Click **Generate Contract PDF**. The file downloads as
`BDI_EquipmentLoan_<BorrowerName>_<ContractDate>.pdf`.

**Step 7.** Collect signatures, then file the signed PDF at
[makerlab.fyi/signed-contracts](https://makerlab.fyi/signed-contracts) — the
address the page itself shows after a contract downloads.

The download confirmation carries that instruction and stays on screen until the
next contract is generated or the form is reset. It deliberately does not time
out, because it is an action item rather than a status message.

The page loads its PDF library (`pdf-lib`) from a CDN, so an internet connection
is required to generate a contract.

## Hosting

The generator runs entirely in the browser — it loads no data from a server and
sends nothing anywhere — so it can be served as a plain static page. The one
external request is the `pdf-lib` script it pulls from a CDN, which means the
page needs an internet connection to build a PDF.

To publish it on GitHub Pages: in the repository settings open **Pages**, set
**Source** to *Deploy from a branch*, pick branch `main` and folder `/ (root)`,
and save. The site appears at `https://<owner>.github.io/<repo>/` within a
minute or two. `.nojekyll` is committed so Pages serves the files as-is instead
of running them through Jekyll.

Note that **a GitHub Pages site is public**. Pages on a private repository
requires a paid plan, and even then the published site is world-readable —
access-controlled Pages is a GitHub Enterprise Cloud feature. So anything in
this repository, including the inventory and its replacement values, is readable
by anyone who finds the URL. That is why no signature image is stored here any
more; see rule 7 in `Rules.txt`.

Once the page is hosted, the copy on the shared Drive is redundant. Either
retire it or keep it as a deliberate offline fallback, but do not leave a stale
copy in circulation — staff following an old bookmark would generate contracts
from an out-of-date equipment list.

## Conditional rules

Six rules change what appears in the finished contract. `Rules.txt` is the full
statement of each; in brief:

- **Drone dimensions and weight.** Drone items print dimensions in inches and
  weight in grams, because borrowers need the weight to apply for insurance.
  Custom builds — CineKing 4K Micro, Cinewhoop, DIY Racing/Freestyle — have no
  authoritative weight, so they print dimensions only. Any inventory item with a
  blank weight field must omit the weight line.

- **Out-of-Massachusetts travel.** A primary location of "Other" whose text does
  not mention MA, Massachusetts, or Waltham adds transport permission and
  carry-on luggage language.

- **Drone clauses.** A drone in the loan appends the licenses and permits
  acknowledgement, the liability disclaimer, and — only when additional users are
  named — an acknowledgement listing them.

- **Department chair approval.** A chair certification paragraph and second
  signature block appear when the loan includes the Artec scanner, or when the
  borrower is an undergraduate or graduate student and the total replacement
  value reaches **$1,000** or more.

- **Signature block appearance.** Both signature blocks render as thin
  horizontal lines with small captions beneath, never as filled boxes, and stay
  empty so the borrower fills them in.

- **Creator name order.** The dropdown lists names as "Last, First" for
  alphabetical scanning, but the contract footer must print "First Last", with
  middle initials preserved in the middle.

## Maintaining the lists

The equipment catalog exists in **two places**: the CSV in this repository, and
the `const INVENTORY` array near the top of the `<script>` block in the HTML. The
running page only reads the array, so editing the sheet alone changes nothing.

Rather than hand-editing the array, export the sheet over the CSV and run:

    python tools/sync-inventory.py

That rebuilds the array from the sheet, prints a per-category count, and warns
about duplicate asset IDs or two items sharing a printed contract name. Use
`--check` to report drift without writing (it exits non-zero when the HTML is
stale). Chair-approval flags live in `CHAIR_IDS` at the top of that script,
because the sheet has no column for them. Both are currently in sync at 38 items across six
categories: 3D Scanner (6), Camera Kit (3), Charging (1), Drone (14), GPS (1),
VR (13).

Each catalog entry carries an `assetId` (the sheet's zero-padded ID, shown in the
form and searchable) and a `category` taken verbatim from the sheet's Contract
Category column. Category strings feed the type filter and the drone rules, so
spelling matters: drone detection matches the word "drone" case-insensitively.
Adding a new category to the sheet automatically adds a filter chip — no code
change needed.

Also in that script block:

- **Staff list** (`STAFF`) — the names offered in the contract creator dropdown.
  Add and remove people as the lab's staff and student workers change. Entries
  are "Last, First".

- **Approval threshold** (`STUDENT_LOAN_THRESHOLD`) — currently `1000`. The
  dollar amount that triggers department chair approval for student loans.
  Because the threshold is measured against replacement values, keep those values
  current in both the CSV and the HTML catalog.

- **Chair approval flag** (`requiresChairApproval`) — set on the Artec scanner.
  Add it to any future item that should always require a chair signature.

## Known data issues in the inventory sheet

Two things in the current sheet are worth fixing at the source. Neither blocks
the generator, and neither is patched in code — the sheet stays the single source
of truth.

- **Asset 0067 appears twice**, once as "Bad Elf Handheld GPS" and once as
  "Bad Elf". The import keeps the first name it sees and skips the duplicate, so
  the item currently prints as "Bad Elf Handheld GPS". Delete whichever row is
  wrong.

- **Assets 0001 and 0008 both print as "Oculus Rift".** The BDI Name for 0008 is
  `BDI_OculusRiftS_008`, so it is almost certainly an Oculus Rift **S** with a
  truncated contract name. Because that name prints on a signed contract it has
  not been changed here. The form shows the asset number next to each name so
  staff can still tell them apart, but two identical entries invite mistakes.

Also note that IDs `85` and `86` lost their leading zeros in the sheet; the
import re-pads them to `0085` and `0086` to match the rest of the catalog.

## Related documents

The policy and instruction documents that accompany this generator live in the
Drive folder with the signed contracts:

- BDI Equipment Loan Policies and Procedures

- Loan Contract Generator Instructions
