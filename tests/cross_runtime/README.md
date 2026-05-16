## Cross-Runtime Integration Tests

The `tests/cross_runtime/` test suite verifies that `.soul` files can be successfully exported to and imported from third-party agent frameworks without losing Core Memory, Semantic Memory, or Episodic Memory.

Currently supported frameworks and CLIs:
* **LangChain** (`langchain_core`)
* **CrewAI** (`crewai`)
* **PocketPaw** (via the `soul-protocol` Python Runtime API)

### Running the Tests

To run these integration tests locally, execute:

```bash
uv run pytest tests/cross_runtime/ -v
```

Optional Dependencies:
To keep the core soul-protocol lightweight, third-party frameworks like LangChain and CrewAI are not strictly required in the default development environment. If LangChain or CrewAI is not installed then the tests will skip instead of failing.

Python Version Constraints: The crewai ecosystem is currently unstable on newer Python runtimes.

These tests will automatically run and pass in the official CI pipeline under supported environments (Python <= 3.12). To run the full suite locally without skips, ensure those specific packages are installed and you are using a compatible Python version.
