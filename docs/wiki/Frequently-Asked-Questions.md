# Frequently Asked Questions

## Why Copier and not a GitHub template repository?

A GitHub template repository is a one-off copy, which is how our earlier projects drifted apart. Copier records the template version, and `copier update` brings later fixes in as a reviewable PR ([Updating from the Template](Updating-from-the-Template)).

## Why release-please and not a bump script?

The version and changelog then come from the commits on `main`, through a PR a human reviews. Nobody runs a script or pushes a tag, so they can't be forgotten, duplicated or done from the wrong branch ([Release Process](Release-Process)).

## Why is the wiki in the repository instead of the GitHub wiki?

So it's reviewed with the code, checked by CI, and visible to AI assistants as context. The GitHub wiki is still where people read it: it's published from `docs/wiki/` ([Project Wiki Standard](Project-Wiki-Standard)).

## Can a project skip a required wiki page?

No. Write a short honest page instead. "No HTTP authentication: bind to a private network only" is a valid Security section. If a page truly doesn't apply to a kind of project, make it conditional in `.standard.toml` upstream.

## Can I use a different AI assistant than the ones listed?

Yes. Most read `AGENTS.md`. For any other, point it at `AGENTS.md`, or paste the chat context prompt from `docs/ai/prompts.md`.

## Does it support languages other than Python?

The core is language-agnostic. Python is the only layer so far, and TypeScript/Node is next ([Contributing to the Template](Contributing-to-the-Template#adding-a-language-layer)).

## Why no Helm chart?

Our clusters use Flux with kustomize overlays, and the kustomize base is consumed directly. A chart would be a second packaging to maintain.
