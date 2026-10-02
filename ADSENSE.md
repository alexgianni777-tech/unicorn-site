# AdSense setup for Unicorn Finds

The site now contains three manual ad positions, but **no Google ad request is made until real AdSense values are added**.

## Prepared positions

- `home_top`: after the four quick picks.
- `home_mid`: after the full product collection.
- `article_mid`: near the end of each editorial guide, before related guides.

The placements deliberately stay away from the main Amazon product CTA so display ads do not compete directly with the affiliate conversion path.

## When the AdSense account is ready

1. Add `unicornsite.online` under AdSense **Sites** and request review.
2. Use the AdSense verification code if Google asks for it.
3. In AdSense, create three responsive display ad units (or reuse one unit if preferred).
4. Put the publisher ID (`ca-pub-...`) and the numeric slot IDs in `assets/ads-config.js`.
5. Add/update `ads.txt` using the exact line shown by AdSense for this publisher account.
6. In **Privacy & messaging**, enable Google's European regulations message or another Google-certified CMP before serving personalised ads to EEA/UK/Swiss users.
7. Re-check the privacy page after ads go live.

## Current safety state

With an empty `publisherId`, the ad containers stay hidden and the AdSense network script is not loaded.
