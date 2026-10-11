from app.environment_check import collect_environment


def test_environment_contains_required_fields() -> None:
    environment = collect_environment()

    assert environment["python"]
    assert environment["implementation"] == "CPython"
    assert environment["system"]
    assert environment["architecture"]
    assert environment["executable"]
