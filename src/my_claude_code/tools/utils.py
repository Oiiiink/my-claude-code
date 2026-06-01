from typing import Any

from my_claude_code.tools.contracts import ToolCall

JSONSchema = dict[str, Any]

def check_paras(tool_call: ToolCall, input_schema: dict[str, Any]) -> None:
    properties = input_schema["properties"]

    for required_param in input_schema["required"]:
        if required_param not in tool_call.input:
            raise ValueError(f"{tool_call.name} is missing required parameter: {required_param}")
        
    for param, para in tool_call.input.items():
        if param not in properties:
            raise ValueError(f"{tool_call.name} got unexpected parameter: {param}")
        required_type = properties[param]
        if _type_not_match(para, required_type):
            raise ValueError(f"{tool_call.name} parameter {param} should match schema {required_type}")


def _type_not_match(para: Any, required_type: str | list[str] | JSONSchema) -> bool:
    """Return True when a value does not match the JSON Schema subset used by tools."""
    if isinstance(required_type, dict):
        return not _matches_schema(para, required_type)

    if isinstance(required_type, list):
        return not any(_matches_type(para, schema_type) for schema_type in required_type)

    return not _matches_type(para, required_type)


def _matches_schema(value: Any, schema: JSONSchema) -> bool:
    expected_type = schema.get("type")
    if expected_type is not None and _type_not_match(value, expected_type):
        return False

    if "enum" in schema and value not in schema["enum"]:
        return False

    if expected_type == "array":
        if not isinstance(value, list):
            return False
        item_schema = schema.get("items")
        if item_schema is None:
            return True
        return all(_matches_schema(item, item_schema) for item in value)

    if expected_type == "object":
        if not isinstance(value, dict):
            return False

        properties = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in value:
                return False

        if schema.get("additionalProperties") is False:
            extra_keys = set(value) - set(properties)
            if extra_keys:
                return False

        for key, item_schema in properties.items():
            if key in value and not _matches_schema(value[key], item_schema):
                return False

    return True


def _matches_type(value: Any, required_type: str) -> bool:
    if required_type == "string":
        return isinstance(value, str)
    if required_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if required_type == "boolean":
        return isinstance(value, bool)
    if required_type == "number":
        return isinstance(value, int | float) and not isinstance(value, bool)
    if required_type == "array":
        return isinstance(value, list)
    if required_type == "object":
        return isinstance(value, dict)
    if required_type == "null":
        return value is None
    return False
