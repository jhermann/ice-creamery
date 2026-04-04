---
applyTo: "**/*.py"
---
# Pytest Testing Standards

Whenever generating or refactoring Python code,
adhere to the following unit testing rules.

## Framework & Structure
- **Framework**: Always use `pytest`. Do not use `unittest` or `nose`.
- **File Naming**: Tests must be located in the `tests/` directory and named `test_*.py`.
- **Class vs Function**: Prefer functional tests. Only use classes if grouping tests with shared expensive setup.

## Pytest Best Practices
- **Fixtures**: Use `pytest.fixture` for setup/teardown. Place shared fixtures in `tests/conftest.py`.
- **Parameterization**: Use `@pytest.mark.parametrize` for testing multiple inputs instead of multiple test functions.
- **Assertions**: Use plain `assert` statements (e.g., `assert result == expected`). Avoid `self.assertEqual`.
- **Mocking**: Use `pytest-mock` (the `mocker` fixture) instead of the standard `unittest.mock` library.

## Test Content
- **Coverage**: Every new function must include a "happy path" test and at least one edge case (e.g., empty input, None, or Exception handling).
- **Style**: Use Arrange-Act-Assert (AAA) comments to structure the test body.
- **Docstrings**: Each test function should have a brief docstring explaining the scenario being tested.

## Example Pattern
```python
def test_function_behavior(mocker, sample_fixture):
    # Arrange
    mocker.patch('module.path.dependency', return_value=True)
    
    # Act
    result = function_under_test(sample_fixture)
    
    # Assert
    assert result is True
```
