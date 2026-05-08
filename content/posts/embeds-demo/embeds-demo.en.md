Title: Content embeds demo
Slug: embeds-demo
Date: 2026-05-08
Lang: en
Translation_key: embeds-demo
Status: hidden
Tags: Demo

This post exercises the content-tags extension set. It is permanently hidden from the published index — its only purpose is to verify that each construct renders correctly.

## Admonition (callout)

!!! note "A note admonition"
    This is a `note` callout using the Python-Markdown admonition extension. The border and title colour track the `--accent` token.

!!! warning "A warning admonition"
    This is a `warning` callout. The colour is a fixed warm red, chosen to remain legible in both light and dark themes without requiring a new token.

!!! tip "A tip admonition"
    Tips use the `--accent-display` token, which is slightly more saturated in light mode.

!!! danger "A danger admonition"
    Danger uses a deep red. Use sparingly.

## Figure with caption

The image below is promoted to a `<figure>` element because the Markdown image includes a title attribute:

![A small white square — placeholder](assets/sample.png "Placeholder image: 16 × 16 white square")

An image without a title renders as a plain `<img>`:

![A small white square](assets/sample.png)

## YouTube embed

Big Buck Bunny by the Blender Foundation (used as a stable video for testing):

[!youtube id="YE7VzlLtp-4"]

The same embed with a start offset:

[!youtube id="YE7VzlLtp-4" start="10"]

## Generic iframe embed

The Digital garden Wikipedia page, embedded at default height:

[!iframe src="https://en.wikipedia.org/wiki/Digital_garden" title="Digital garden — Wikipedia"]

Same, with a custom height:

[!iframe src="https://en.wikipedia.org/wiki/Digital_garden" title="Digital garden — Wikipedia" height="600"]

## Code block — embeds are NOT expanded here

The following fenced block should render as literal text, not as a YouTube iframe:

```
[!youtube id="YE7VzlLtp-4"]
```

And this indented block too:

    [!youtube id="YE7VzlLtp-4"]
