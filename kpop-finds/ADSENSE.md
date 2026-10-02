# AdSense launch notes for K-Pop Finds

The prototype has reserved display-ad placements but loads **no AdSense network code** until a real publisher ID and ad-unit slot IDs are supplied.

Before launch on a separate domain:

1. Add the new K-Pop Finds domain to AdSense > Sites and request review.
2. Add the AdSense verification snippet when Google provides it.
3. Create responsive display units for `home_top`, `home_mid`, and `guide_mid`.
4. Add the real `ca-pub-...` and slot IDs to `assets/ads-config.js`.
5. Add the exact `ads.txt` line supplied by AdSense.
6. Configure Google's European regulations message or another Google-certified CMP for EEA/UK/Swiss traffic before personalised ads are served.
7. Update the privacy page when the site moves from prototype to production.
