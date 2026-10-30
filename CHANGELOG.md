# Changelog

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
