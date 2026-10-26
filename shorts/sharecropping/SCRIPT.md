# The Sharecropping Trap (Short, test build)

**What this is:** a test of this repo's method on a real Chunk History Short. The narration is your voice clone, spliced from
*Bottom Rail on Top* (Reconstruction, Part 2) ch08 *No Land* and ch09 *The Debt*, so it used no new voice credits. The
visuals are GSAP scenes in the channel's look. **59.6 s, 1080×1920.** Final: `renders/Sharecropping_Trap_Short.mp4`.

**Promise (the method's Phase 0).** Hook: *the family finds out it owes more than it made* (a question: how?). Peak: the
settling-up ledger, where the owed bar lands on the wrong side of zero, the same red bar the cover shows. The ending loops
back to the cover. Call to action: the full episode.

**Palette.** This is a heavy subject, so it uses the quiet palette: bone tape for titles, teal marks, no coral tint, notes
on cream slips, the ledger in bars with no dollar figures (as in Ep 2). Orange comes back only on the end card.

## Shot script

| # | Time | Visual | On screen | Voice (spliced) |
|---|---|---|---|---|
| 0 | 0.0 | **Cover, fully drawn on frame 0:** *Weighing cotton, Texas, 1904*. A red "= owes" slip lands on *owes*. | A YEAR OF WORK. / STILL IN DEBT. | "the family finds out it owes more than it made." (ch09) |
| 1 | 3.7 | Cotton field, 1896. The title stamps onto the picture. | SHARECROPPING | "It's called sharecropping." (ch08) |
| 2 | 5.5 | A cabin, c. 1906, drops in. Teal loop around the woman at the door. | *20 or 30 acres* · *+ a cabin* | "A family moves onto one, maybe 20 or 30 acres, with a cabin." |
| 3 | 9.8 | **The deal** card. Each item appears as it's named: land, a mule, tools, then the work. | PLANTER · FAMILY | "The planter provides the land, and maybe a mule and tools. The family provides the work." |
| 4 | 15.1 | A cotton bale drops and splits on *half and half*. | *the crop* · *planter ½* · *family ½* | "At harvest, they split the crop. Often half and half." |
| 5 | 18.8 | **The year:** months J–D, the crop curve grows to harvest, a bracket under the months before it. | *harvest* · *has to eat* | "until harvest, a family has to eat." (ch09) |
| 6 | 21.5 | Plantation commissary, 1937. Teal loop around the store. | *on credit* · *the planter's store* | "So they bought what they needed on credit. Usually from a local store, and the store was often owned by the planter." |
| 7 | 27.6 | The De Soto County sharecropping contract, 1867. Definition bar. | **crop lien** · a promise that the store gets paid first… · *paid first: 1. the store, 2. the family* | "they signed a crop lien. That's a promise that the store gets paid first, out of the crop, before the family sees a cent." |
| 8 | 34.6 | The title stamps, then the ledger page drops in. | SETTLING UP | "And at the end of the year came settling up." |
| 9 | 37.1 | **Peak:** the ledger, line by line: crop sold, the family's half, minus the store, plus interest, **= owes**. Music drops out on *owes*; the owed bar glows; the camera pushes in. | the ledger rows | "The crop is sold. The family's half comes in. Then the store subtracts everything they bought, plus interest. And the family finds out it owes more than it made." |
| 10 | 47.1 | The ledger dims. | *can't leave* | "That means they can't leave." |
| 11 | 48.9 | Year pages stack, each opening with a debt carried over. | *next year* · *and the next* · *already behind* | "So they sign on for another year, already behind. Then another." |
| 12 | 53.2 | **Loop:** back to the cover; the title stamps again on *trap*. | A YEAR OF WORK. / STILL IN DEBT. | "But for a lot of families, it was a trap with no way out." |
| 13 | 56.5 | End card (3 s). | THE FULL STORY · **BOTTOM RAIL ON TOP** · Reconstruction, Part 2 · on the channel | — |

## Accuracy

The narration is word for word from the published episode, which was fact-checked (Ep 2 `script/SCRIPT.md`, rows 22–23:
sharecropping terms "safe as worded", with *maybe* and *often*). The new on-screen text only repeats the narration. The one
added line, "paid first: 1. the store, 2. the family", restates the crop lien definition. No dollar figures, no dates
beyond the photo credits. Credits are in the source tags (LOC, FSA, Nabb Center / Internet Archive).

## YouTube text

- **Title:** Why Sharecroppers Owed Money After a Whole Year of Work
- **Description:** They grew the crop, split it, and still ended the year in debt. Here's how sharecropping's math worked.
  Full story on the channel: Bottom Rail on Top (Reconstruction, Part 2). #history #reconstruction #sharecropping
- **Pinned comment:** What would you have done at settling-up time: sign on for another year, or leave and risk arrest?
- **On upload:** "Altered or synthetic content": Yes (voice clone). "Not made for kids." Related video: *Bottom Rail on Top*.

## Rebuild

```bash
python3 tools/build_audio.py ../../../15minhistorystyle   # splice the voice, mix, write timeline.json/.js
node tools/render.mjs --check                             # dead-zone + overlap/safe-zone audit at 0.5 s
node tools/render.mjs --stills 0,12.5,45                  # QA frames -> out/stills/sheet.jpg
node tools/render.mjs                                     # -> out/sharecropping_short.mp4 (about 4-5 min)
python3 tools/master.py out/sharecropping_short.mp4 renders/Sharecropping_Trap_Short.mp4
```

The page loads GSAP 3.13.0 from jsDelivr (not committed, per the repo's rule). For an offline render: `npm i gsap@3.13.0`
anywhere, then `GSAP_DIR=/path/to/node_modules/gsap/dist node tools/render.mjs`. To watch in a browser, serve the folder
(`python3 -m http.server`) and open `sharecropping.html`. Click to play with sound, use ←/→ to skip and the bar at the
bottom to seek.
