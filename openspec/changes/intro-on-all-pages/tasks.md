## 1. Template changes

- [ ] 1.1 `themes/garden/templates/index.html` — remove the `page_number` gate (lines 15–20): always `{% include "_intro_inference_script.html" %}` followed by the `{%- if not INTRO_ALL %}<h1>Posts</h1>{% endif %}` empty-state fallback; delete the `{%- else -%}<h1>Posts</h1>` branch.
- [ ] 1.2 `themes/garden/templates/lang_index.html` — change the intro condition (line 13) to `{% if INTRO_LANG is defined and INTRO_LANG.get(page_lang) %}` (drop the `page_number` clause); keep the `{% else %}<h1>Posts ({{ page_lang | upper }})</h1>` no-intro-file fallback.

_Commit: "fix(homepage): render intro on every paginated page, not just the first"_

## 2. Verification

- [ ] 2.1 `make devbuild`, then confirm `output/page/2/index.html` contains a `<section class="intro">` (cross-language intro now on page 2).
- [ ] 2.2 Confirm `output/<lang>/page/2/index.html` (for a language with an `intro/lang.<lang>.md` and >12 articles) contains its `<section class="intro">`.
- [ ] 2.3 Confirm page 1 is unchanged: `output/index.html` and `output/<lang>/index.html` still carry the intro exactly as before.
- [ ] 2.4 Confirm the empty-state still works: a language with no `lang.<lang>.md` still renders `<h1>Posts (LANG)</h1>` on every page (no stray empty intro section).
- [ ] 2.5 Run the test suite (`pytest`) — confirm nothing regresses (no template-output tests exist, but the plugin/lint suites should stay green).

## 3. Documentation

- [ ] 3.1 Confirm no `README.md` change is needed (it documents intro authoring, not page scoping). Add a one-line note to `docs/visual-identity.md` under "Intro region" only if the page-coverage change reads as worth recording.

## 4. Deploy validation gate

- [ ] 4.1 Push and watch the `build-and-deploy` GitHub Actions run to green.
- [ ] 4.2 Spot-check the live `/page/2/` (and a `/<lang>/page/2/`) shows the intro.
