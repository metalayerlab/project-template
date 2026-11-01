# Changelog

## [0.1.22](https://github.com/metalayerlab/project-template/compare/v0.1.21...v0.1.22) (2026-11-01)


### ✨ Features

* brain_pull follows a Subscriptions note, and only main runs move the date ([#106](https://github.com/metalayerlab/project-template/issues/106)) ([6568081](https://github.com/metalayerlab/project-template/commit/65680818ef10bce1774b074ab620a84d12085401)), closes [#105](https://github.com/metalayerlab/project-template/issues/105)
* list settings (is_list) in the generated config engine, and design 0019 for a thin config.py ([#107](https://github.com/metalayerlab/project-template/issues/107)) ([7e9142f](https://github.com/metalayerlab/project-template/commit/7e9142f8716d361e63a4fc28f33062a1dd7126af))

## [0.1.21](https://github.com/metalayerlab/project-template/compare/v0.1.20...v0.1.21) (2026-11-01)


### ✨ Features

* agents list what a session left behind and remove only what the user approves ([#96](https://github.com/metalayerlab/project-template/issues/96)) ([9f48a54](https://github.com/metalayerlab/project-template/commit/9f48a54f25d977e7d1603ac1c94ba1cb31ddd18a))
* an opt-in CI job for integration tests that need system packages or extras ([#97](https://github.com/metalayerlab/project-template/issues/97)) ([1e52ca7](https://github.com/metalayerlab/project-template/commit/1e52ca787ad42c729f9249039b67808f892fdeaf))
* brain_pull, a scheduled Brain pull workflow for obsidian brains ([#99](https://github.com/metalayerlab/project-template/issues/99)) ([e1b5992](https://github.com/metalayerlab/project-template/commit/e1b59928203a00271384628ea46b4eacc1570331))


### 🐛 Bug Fixes

* keep inline code's text in wiki heading anchors ([#95](https://github.com/metalayerlab/project-template/issues/95)) ([dc6254d](https://github.com/metalayerlab/project-template/commit/dc6254d362671bfeeea84dbbf9d9d6acf85376bc))
* run bootstrap after copier update, not during it, so a failing task can't drop project edits ([#101](https://github.com/metalayerlab/project-template/issues/101)) ([07cf1f2](https://github.com/metalayerlab/project-template/commit/07cf1f2477451e7940e345a1063f5eb562453776))
* run Python integration tests and test subsets without the coverage floor ([#103](https://github.com/metalayerlab/project-template/issues/103)) ([a5984a3](https://github.com/metalayerlab/project-template/commit/a5984a3844f7fdc72ab7662b2315bd57e646ce6f))

## [0.1.20](https://github.com/metalayerlab/project-template/compare/v0.1.19...v0.1.20) (2026-11-01)


### ✨ Features

* kind knowledge, a notes repository with the agent guard rails ([#89](https://github.com/metalayerlab/project-template/issues/89)) ([4c0c225](https://github.com/metalayerlab/project-template/commit/4c0c225e2bb67dec9d15d5912b7c40ec1077f435))
* language obsidian, a vault layer whose kind is brain, replacing kind knowledge ([#92](https://github.com/metalayerlab/project-template/issues/92)) ([89ae367](https://github.com/metalayerlab/project-template/commit/89ae3674857d5efc42ee0e9aaae99cec18cfe5d9))


### 🐛 Bug Fixes

* separate Home wiki contents lines and list every choice in the template problem form ([#87](https://github.com/metalayerlab/project-template/issues/87)) ([0ec97df](https://github.com/metalayerlab/project-template/commit/0ec97df3a4902e9864a32edcd3d7d70f7937eda8))


### 📚 Documentation

* design record 0015, a knowledge kind ([#88](https://github.com/metalayerlab/project-template/issues/88)) ([2fef77a](https://github.com/metalayerlab/project-template/commit/2fef77ad8b113cdfb5b668ecff270f268236036a))
* design record 0016, an obsidian language layer ([#91](https://github.com/metalayerlab/project-template/issues/91)) ([c5fbe07](https://github.com/metalayerlab/project-template/commit/c5fbe07f3c8eabd00955183616da87f5fd36e9d1))
* run the docs-touched wiki check in the Definition of done ([#93](https://github.com/metalayerlab/project-template/issues/93)) ([60ccad1](https://github.com/metalayerlab/project-template/commit/60ccad1d45dbd7341c897c73dbace299e8fea466))

## [0.1.19](https://github.com/metalayerlab/project-template/compare/v0.1.18...v0.1.19) (2026-11-01)


### 🐛 Bug Fixes

* config rejects a YAML float or bool for an int setting, and a list or mapping for a string ([#85](https://github.com/metalayerlab/project-template/issues/85)) ([4d11ed9](https://github.com/metalayerlab/project-template/commit/4d11ed9b03dbf06aa7c1dfc15a5d526dbea37d23))

## [0.1.18](https://github.com/metalayerlab/project-template/compare/v0.1.17...v0.1.18) (2026-10-31)


### ✨ Features

* kind web, a Vite + React single-page app served by nginx ([#77](https://github.com/metalayerlab/project-template/issues/77)) ([64cedf8](https://github.com/metalayerlab/project-template/commit/64cedf81b6211f7e0310003fb5402a60f438a612))


### 📚 Documentation

* design record 0014, a web kind ([#75](https://github.com/metalayerlab/project-template/issues/75)) ([b1f5b87](https://github.com/metalayerlab/project-template/commit/b1f5b870b25bb8513379f7c0b616e8d43bc62397))

## [0.1.17](https://github.com/metalayerlab/project-template/compare/v0.1.16...v0.1.17) (2026-10-31)


### ✨ Features

* prompt to work through the open issues with one sub-agent each ([#73](https://github.com/metalayerlab/project-template/issues/73)) ([5b5923f](https://github.com/metalayerlab/project-template/commit/5b5923f621e938a2311cd39a15c79cc494a2d94b))

## [0.1.16](https://github.com/metalayerlab/project-template/compare/v0.1.15...v0.1.16) (2026-10-31)


### ✨ Features

* keep AI assistants' edits inside the repository; ask other codebases for changes by issue ([#71](https://github.com/metalayerlab/project-template/issues/71)) ([97178d5](https://github.com/metalayerlab/project-template/commit/97178d59093049c6d4880e4d156274c1300ce526))
* review checklist items for replaced results, shared two-sided checks, typed config, path and secret leaks ([#69](https://github.com/metalayerlab/project-template/issues/69)) ([8ea3073](https://github.com/metalayerlab/project-template/commit/8ea3073a1de7c39cf611b3218d01ac2dbf3c973f))

## [0.1.15](https://github.com/metalayerlab/project-template/compare/v0.1.14...v0.1.15) (2026-10-31)


### ✨ Features

* name the optional extras the image installs (image_extras) ([#64](https://github.com/metalayerlab/project-template/issues/64)) ([3632a75](https://github.com/metalayerlab/project-template/commit/3632a75205db93629f7d3715388bcbe1cd1624ed))


### 📚 Documentation

* prompts for working on the template (docs/ai/prompts.md) ([#66](https://github.com/metalayerlab/project-template/issues/66)) ([5c37e26](https://github.com/metalayerlab/project-template/commit/5c37e266e6d8d7ccecfce2bf2a938568d24be8e9))

## [0.1.14](https://github.com/metalayerlab/project-template/compare/v0.1.13...v0.1.14) (2026-10-31)


### ✨ Features

* let AI assistants push feature branches; keep main, force, tag and release pushes denied ([#61](https://github.com/metalayerlab/project-template/issues/61)) ([4da050c](https://github.com/metalayerlab/project-template/commit/4da050ca97a54a7a9526a0d9c4ab57dec71a0247))

## [0.1.13](https://github.com/metalayerlab/project-template/compare/v0.1.12...v0.1.13) (2026-10-30)


### ✨ Features

* install system packages from contrib/system-packages.txt in CI and the image ([#59](https://github.com/metalayerlab/project-template/issues/59)) ([d52258e](https://github.com/metalayerlab/project-template/commit/d52258e691ab4a037df926a0731d22c8981327d4))
* keep GitHub's About box (description, wiki link, topics) in .github/repository.toml ([#54](https://github.com/metalayerlab/project-template/issues/54)) ([c6d93fb](https://github.com/metalayerlab/project-template/commit/c6d93fb35dff5f573000b93e84fae3c8baf1286c))


### 🐛 Bug Fixes

* a long or quoted description no longer breaks the generated project ([#58](https://github.com/metalayerlab/project-template/issues/58)) ([e5088a4](https://github.com/metalayerlab/project-template/commit/e5088a4b00acb758c3dce29a95470ed17740f15f))
* workflows create the labels they rely on (no-docs-needed, template-update) ([#57](https://github.com/metalayerlab/project-template/issues/57)) ([0aa772f](https://github.com/metalayerlab/project-template/commit/0aa772f4db8cc38d58eb31d5209f65becd0aefe4))

## [0.1.12](https://github.com/metalayerlab/project-template/compare/v0.1.11...v0.1.12) (2026-10-30)


### ✨ Features

* a TypeScript language layer ([#50](https://github.com/metalayerlab/project-template/issues/50)) ([f1bf1e4](https://github.com/metalayerlab/project-template/commit/f1bf1e41fd217a94690931f4ca980f4e9456c329))

## [0.1.11](https://github.com/metalayerlab/project-template/compare/v0.1.10...v0.1.11) (2026-10-30)


### ✨ Features

* a "None" language choice ([#44](https://github.com/metalayerlab/project-template/issues/44)) ([d6f2104](https://github.com/metalayerlab/project-template/commit/d6f2104f86d9762c030878fa6e9d36c5e5c131cf))


### 🐛 Bug Fixes

* a library's README links API Reference, not a page it doesn't have ([#45](https://github.com/metalayerlab/project-template/issues/45)) ([4c5e52b](https://github.com/metalayerlab/project-template/commit/4c5e52bc311b5eb1ffcfb864b2dda6313542fa97))

## [0.1.10](https://github.com/metalayerlab/project-template/compare/v0.1.9...v0.1.10) (2026-10-30)


### 🐛 Bug Fixes

* a warning fails a project's tests ([#41](https://github.com/metalayerlab/project-template/issues/41)) ([3ec9127](https://github.com/metalayerlab/project-template/commit/3ec912771aa961f699a2b7c70b1ba4c74be8b1e7))
* service projects test with httpx2, so pytest no longer warns ([#40](https://github.com/metalayerlab/project-template/issues/40)) ([a6160e6](https://github.com/metalayerlab/project-template/commit/a6160e6ad06954edbf1d6a7082c00baa370c9923))

## [0.1.9](https://github.com/metalayerlab/project-template/compare/v0.1.8...v0.1.9) (2026-10-30)


### ✨ Features

* checks print one line when they pass, and assistants keep sessions terse ([#38](https://github.com/metalayerlab/project-template/issues/38)) ([bd6ba32](https://github.com/metalayerlab/project-template/commit/bd6ba3241bbe22afc8f72f97edfddae58c1ba25a))

## [0.1.8](https://github.com/metalayerlab/project-template/compare/v0.1.7...v0.1.8) (2026-10-30)


### ✨ Features

* assistants give their recommendation with every question they ask ([#35](https://github.com/metalayerlab/project-template/issues/35)) ([4fa07aa](https://github.com/metalayerlab/project-template/commit/4fa07aad34b25ac697b7487c6ba29e0ea6bbda2f))
* assistants report what let a bug happen and what should change ([#36](https://github.com/metalayerlab/project-template/issues/36)) ([4c89cee](https://github.com/metalayerlab/project-template/commit/4c89ceeda5b50e19c0367f65d1a67f065e1aac44))
* raise the AGENTS.md budget to 9,000 characters and document what a cut costs ([#37](https://github.com/metalayerlab/project-template/issues/37)) ([f06ffbb](https://github.com/metalayerlab/project-template/commit/f06ffbb0125611292ac3f10eaf49933792f0ed27))


### 🐛 Bug Fixes

* tell a sole code owner how to merge their own PR ([#33](https://github.com/metalayerlab/project-template/issues/33)) ([4192a27](https://github.com/metalayerlab/project-template/commit/4192a27e6f15263fe0dccb9bbb24b639247808b1))

## [0.1.7](https://github.com/metalayerlab/project-template/compare/v0.1.6...v0.1.7) (2026-10-29)


### ✨ Features

* extra_ports question, so a service can declare listeners besides port ([#30](https://github.com/metalayerlab/project-template/issues/30)) ([fbdc334](https://github.com/metalayerlab/project-template/commit/fbdc3349e5736543f7f0456fe33c12131b1231b5))
* run CI's markdownlint and gitleaks locally with scripts/check-docs-secrets.sh ([#29](https://github.com/metalayerlab/project-template/issues/29)) ([f2f7957](https://github.com/metalayerlab/project-template/commit/f2f7957e941959a33d38ef88524eac834b89ec25))


### 🐛 Bug Fixes

* library projects' Troubleshooting page fails markdownlint on the first PR ([#28](https://github.com/metalayerlab/project-template/issues/28)) ([8c86358](https://github.com/metalayerlab/project-template/commit/8c863589242fd92522472bbdc267829d965cdebf))

## [0.1.6](https://github.com/metalayerlab/project-template/compare/v0.1.5...v0.1.6) (2026-10-29)


### ✨ Features

* tell projects how to report a template bug instead of only working around it ([#26](https://github.com/metalayerlab/project-template/issues/26)) ([f7dcc1e](https://github.com/metalayerlab/project-template/commit/f7dcc1e9bab576a6680e362611906e9656ffad5f))

## [0.1.5](https://github.com/metalayerlab/project-template/compare/v0.1.4...v0.1.5) (2026-10-29)


### 🐛 Bug Fixes

* document Typer sub-commands and positional arguments in CLI-Reference ([#18](https://github.com/metalayerlab/project-template/issues/18)) ([495f2cf](https://github.com/metalayerlab/project-template/commit/495f2cf40ce0290146fefa4b0b19196c13764de3))
* service images bind 0.0.0.0 whatever the app's default listen host ([#19](https://github.com/metalayerlab/project-template/issues/19)) ([90fe2bd](https://github.com/metalayerlab/project-template/commit/90fe2bdfeac1f2867cffe7718c635f5711931a09))

## [0.1.4](https://github.com/metalayerlab/project-template/compare/v0.1.3...v0.1.4) (2026-10-28)


### 🐛 Bug Fixes

* stop AI assistants crediting themselves in commits and PRs ([#15](https://github.com/metalayerlab/project-template/issues/15)) ([caed0b8](https://github.com/metalayerlab/project-template/commit/caed0b8605a3748964abe522c3ab60ff8c8b8ec8))

## [0.1.3](https://github.com/metalayerlab/project-template/compare/v0.1.2...v0.1.3) (2026-10-28)


### ✨ Features

* optional Dependabot auto-merge, still gated on a code owner's approval ([#13](https://github.com/metalayerlab/project-template/issues/13)) ([5a56087](https://github.com/metalayerlab/project-template/commit/5a560876f85187b2d30f033326462cfc2a4b3c8d))


### 🐛 Bug Fixes

* render tests from the checkout, not the latest release tag ([#11](https://github.com/metalayerlab/project-template/issues/11)) ([84f3d9a](https://github.com/metalayerlab/project-template/commit/84f3d9a205b9ae0c08054a8c91e5546b6289c951))

## [0.1.2](https://github.com/metalayerlab/project-template/compare/v0.1.1...v0.1.2) (2026-10-28)


### 🐛 Bug Fixes

* don't publish a :0 image tag for 0.x releases ([#9](https://github.com/metalayerlab/project-template/issues/9)) ([981aa27](https://github.com/metalayerlab/project-template/commit/981aa273e63428880bf4e27e1319fbac7d1d907e))


### 📚 Documentation

* bot PR runs need approval on every push, not just the first ([#7](https://github.com/metalayerlab/project-template/issues/7)) ([251e9d2](https://github.com/metalayerlab/project-template/commit/251e9d2076d1528e0af15f9ee71a1561c80cc338))
* new GHCR packages are private until made public ([#10](https://github.com/metalayerlab/project-template/issues/10)) ([e3d156c](https://github.com/metalayerlab/project-template/commit/e3d156cc3fda54061d2bcef9a6abd82d03fb112e))

## [0.1.1](https://github.com/metalayerlab/project-template/compare/v0.1.0...v0.1.1) (2026-10-28)


### 🐛 Bug Fixes

* open an issue when a template update needs workflow changes the token can't push ([#5](https://github.com/metalayerlab/project-template/issues/5)) ([51248cc](https://github.com/metalayerlab/project-template/commit/51248ccc9cf9d3fa027e86a82f8367e551812517))
* tag template releases vX.Y.Z so copier update can find them ([#4](https://github.com/metalayerlab/project-template/issues/4)) ([abade04](https://github.com/metalayerlab/project-template/commit/abade0478b7ec1e94d69e4dd5398fcd3b5a96d78))

## 0.1.0 (2026-10-28)


### ✨ Features

* initial project template ([be647a9](https://github.com/metalayerlab/project-template/commit/be647a926768087600e31d30d2d47b09adf94d3b))


### 🐛 Bug Fixes

* run CI once per change, not once per push and again per PR ([#1](https://github.com/metalayerlab/project-template/issues/1)) ([55c9cb8](https://github.com/metalayerlab/project-template/commit/55c9cb89e9702d563403e3a326c17c91e72d3bce))
* start the first release at 0.1.0, not 1.0.0 ([#3](https://github.com/metalayerlab/project-template/issues/3)) ([159e194](https://github.com/metalayerlab/project-template/commit/159e1941496170a46d500a7db977406b3fb8f2f7))

## Changelog

Generated by [release-please](https://github.com/googleapis/release-please) from
Conventional Commit messages on `main`. Do not edit by hand: change the commit
or PR title instead. See the wiki's Release-Process page.
