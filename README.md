# THE WORLD TODAY - news-image-20261118 v4

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/mmr9759/news-image-20261118-v4/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/mmr9759/news-image-20261118-v4/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

One-page newspaper front page summing up Wednesday 18 November 2026:
36 real stories from six continents, three illustrated lead stories
(Kerch Bridge falls, US jets hit Qeshm, Nvidia $115.8bn), a numbered
world map with eight pinned places, and a markets strip.

## Run

```sh
python3 main.py            # writes /output/entry.png
MAKEFUN_OUTPUT_DIR=out python3 main.py   # local run
```

Pure Python 3 standard library, no network, no randomness. The program
draws every pixel itself (embedded 5x7 bitmap font, hand-written PNG
encoder) and writes a deterministic 1024x1024 PNG under 1 MiB.

## License

MIT - see LICENSE.
