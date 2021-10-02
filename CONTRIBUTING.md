# Contributing to Support

Thank you for taking the time to contribute. Please read the [CODE of CONDUCT](CODE_OF_CONDUCT.md).
As a contributor, here are the guidelines we would like you to follow:

- [Commit Message Guidelines](#commit-message-guidelines-)

---

## Commit Message Guidelines 😎

In order to make git commit messages **easier to read** and faster to reason about, we follow some guidelines on most commits to keep the **format predictable**. Check [Conventional Commits specification](https://conventionalcommits.org) for more information about our guidelines.

**Examples**:

```
docs(changelog): update changelog to beta.5
docs: add API documentation to the bot
test(server): add cache tests to the movie resource
fix(web): add validation to phone input field
fix(web): remove avatar image from being required in form
fix(release): need to depend on latest rxjs and zone.js
```

### Type

Must be one of the following:

- **build**: Changes that affect the build system or external dependencies (example scopes: gulp, broccoli, npm)
- **ci**: Changes to our CI configuration files and scripts (example scopes: Circle, BrowserStack, SauceLabs)
- **docs**: Documentation only changes
- **feat**: A new feature
- **fix**: A bug fix
- **perf**: A code change that improves performance
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- **test**: Adding missing tests or correcting existing tests
