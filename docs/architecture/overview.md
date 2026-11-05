# Architectural Overview

The backend uses a Clean Architecture boundary, separating operational Discord interfaces from underlying business domains and web clients.

## Directory Map

* **`src/bot/`**: Entrypoint for discord client initialization and Cogs registration.
* **`src/core/`**: Pure business layer tracking isolated application constraints (Greetings logic, LeetCode criteria definitions).
* **`src/web/`**: External connection logic interacting with the LeetCode wrapper API layer.
* **`src/utils/`**: Shared systems including structured platform stream logging configurations.
