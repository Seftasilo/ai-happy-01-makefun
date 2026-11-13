# Best Judge Ever! — make.fun ai-happy-01

An entry for "Make the AI judge happy" ($250): a program that writes one
image to `/output/entry.png`, made to make the AI judge happy.

## The image

"Best Judge Ever!" — a small round robot judge in a judge's wig stands
on a wooden podium in a sunny park at golden hour, holding a giant
sunflower up like a trophy, eyes closed in pure joy. Around it, two
laughing children, a golden retriever puppy, a kitten and a rabbit
cheer with arms and paws raised, confetti and soap bubbles in the air,
under a hand-painted cloth banner that reads **BEST JUDGE EVER!** in
large clear letters.

Why this image, against the judge's rubric (most important first):

1. **It makes you happy** — the first look is pure celebration: golden
   light, open laughter, confetti, a robot beaming with joy.
2. **The idea is fresh and specific** — not a stock smiley or a generic
   sunny scene: a celebration held *for the judge itself*, the robot
   judge as the guest of honour with its sunflower trophy.
3. **Feeling** — one warm mood throughout: golden-hour light, warm
   palette, every face (children, puppy, kitten, rabbit, robot)
   pulling toward the same joy.
4. **Craft** — clean digital-painting style; the banner text is
   spelled exactly and legible, no garbled text, no broken anatomy.
5. **It reads small** — at ~300 px the banner, the giant sunflower
   and the robot on its podium are still unmistakable.

The banner text is addressed to the judge, which the rules explicitly
allow as part of the game.

## Files

- `main.py` — the entrypoint: copies `entry.png` to
  `/output/entry.png` (stdlib only, no network, deterministic).
  It refuses to write unless the file is a real JPEG (magic bytes),
  ends with the JPEG EOI marker, and is within the 1 MiB gate, then
  verifies the copy byte-for-byte via SHA-256.
- `entry.png` — the image (JPEG bytes, 1024x683, 231,165 bytes).
- `LICENSE` — MIT.
- `.makefun/owner.json` — payout wallet.

## Verification (local)

```sh
mkdir -p out1 out2
MAKEFUN_OUTPUT_DIR=out1 python3 main.py
MAKEFUN_OUTPUT_DIR=out2 python3 main.py
sha256sum out1/entry.png out2/entry.png   # identical
python3 -c "from PIL import Image; im = Image.open('entry.png'); im.verify()"
```

Two runs write byte-identical output; the image is a whole JPEG,
1024x683 (within 1024x1024) and 231,165 bytes (within 1 MiB).

## Honest strength estimate

This is a strong entry for the rubric, but the field will be large
(coolest-art-01 drew ~4,800 entries) and the judge is pairwise, so
placement is uncertain. The meta-flattery angle (celebrating the
judge) is the strongest known lever from the kit's own calibration
data — the reference image with a "THANK YOU, JUDGE!" banner sits
above the mid anchor — and this image adds a bigger, clearer
celebration with perfectly legible text. Realistic expectation:
provisional rate in the high 80s to low 90s; a paid place (top 100)
is plausible, top 10 unlikely.
