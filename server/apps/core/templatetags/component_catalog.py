"""Read component usage headers for the development catalog."""

import re

from django import template
from django.template.loader import get_template

register = template.Library()


@register.inclusion_tag("patterns/component_reference.html")
def component_reference(name: str) -> dict[str, str]:
    if not re.fullmatch(r"[a-z_]+", name):
        raise ValueError("Expected a component name")
    path = f"components/{name}.html"
    source = get_template(path).template.source
    contract = "\n".join(re.findall(r"^\{# (.*?) #\}$", source, flags=re.MULTILINE))
    return {"source_path": f"server/templates/{path}", "contract": contract}
