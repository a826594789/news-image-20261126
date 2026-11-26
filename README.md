# The World in One Day — 26 November 2026

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/a826594789/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/a826594789/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

A newspaper front page that sums up Thursday 26 November 2026 in a
single image, built for make.fun's `news-image-20261126` bounty.

## What it shows

Four stories, each checked against reporting from 26 November 2026:

1. **North Korea — nuclear arsenal.** Kim Jong Un, touring nuclear
   material plants on Wednesday, said the North must deploy tactical
   (battlefield) nuclear weapons across more domains and expand
   production of nuclear material. KCNA reported it on Thursday; he
   called the North's nuclear status "absolutely inviolable".
   (Reuters, Korea Times, Straits Times, CNN)
2. **New York — Thanksgiving.** The 100th Macy's Thanksgiving Day
   Parade was moved to Saturday 28 November after a nor'easter
   bearing down on the city threatened gusts up to 60 mph, too strong
   for the giant balloons. The first weather postponement in the
   parade's 100-year history. (Reuters, WSJ, Al Jazeera, CNN)
3. **Middle East — oil.** The Houthis claimed a strike on Saudi
   Arabia's Ras Tanura refinery; satellite images showed a huge black
   smoke plume, and oil loadings at the terminal were suspended. The
   Saudi-led coalition said it shot down four drones there. CNN noted
   it could not independently verify the attack. (CNN, Reuters)
4. **Ukraine war — Russia.** Ukraine's General Staff said a
   long-range strike on the Savasleyka airbase damaged five Russian
   aircraft — three MiG-31 jets used to fire hypersonic missiles and
   two Su-34 fighter-bombers — knocking them out of service. Russia
   did not immediately comment. (Al Jazeera, Reuters)

Claims are worded as claims, and every number in the image comes
from the reporting above.

## How it is made

`main.py` is a single self-contained Python 3 program using only the
standard library. It draws the page pixel by pixel from a small
bitmap font built into the file (masthead, kickers, headlines, decks
and four flat pictograms: a missile, a parade balloon, a refinery, a
fighter jet), then encodes the result as a PNG by hand with `zlib`.

There is no network access, no randomness and no clock involved, so
running it twice writes byte-identical files.

## Run it

```sh
python3 main.py
```

The image is written to `$MAKEFUN_OUTPUT_DIR/entry.png`
(` /output/entry.png` by default). It is 1024x1024 pixels and well
under the 1 MiB limit.

## License

MIT — see `LICENSE`.
