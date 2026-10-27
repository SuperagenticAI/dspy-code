"""Field names must be usable in generated Python signatures."""

import keyword

import pytest

from dspy_code.validation.input_validator import InputValidator, ValidationError


@pytest.mark.parametrize("name", keyword.kwlist)
def test_field_name_rejects_python_keywords(name):
    with pytest.raises(ValidationError, match="not a valid Python identifier"):
        InputValidator().validate_field_name(name)


@pytest.mark.parametrize("name", ["question", "class_", "_answer", "café", "match", "case"])
def test_field_name_accepts_usable_identifiers(name):
    validated = InputValidator().validate_field_name("  " + name + "  ")
    assert validated == name
    compile(f"class Signature:\n    {validated}: str\n", "<signature>", "exec")
