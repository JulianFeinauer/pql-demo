import uuid
from datetime import datetime, timedelta
from random import uniform
from typing import Iterable, Tuple, Callable, Any, Union, List, Dict

from pql import Query, Projection, Aggregation, SubQuery, RootContext, agg_functions


def create_cycles(n):
    cycles = []
    timestamp = datetime.now()
    for i in range(0, n):
        cycle_duration = timedelta(seconds=uniform(20.0, 30.0))
        pause = timedelta(seconds=uniform(1.0, 60.0))
        cycles.append({"id": i, "start": timestamp, "end": timestamp + cycle_duration, "machine": "LHL 01"})

        timestamp = timestamp + cycle_duration + pause

    return cycles


def create_tools(n):
    tools = []
    timestamp = datetime.now()
    for i in range(0, n):
        duration = timedelta(minutes=uniform(20.0, 40.0))
        pause = timedelta(minutes=uniform(5.0, 15.0))
        tools.append({"id": uuid.uuid4(), "name": f"Tool {i}", "start": timestamp, "end": timestamp + duration,
                      "machine": "LHL 01"})

        timestamp = timestamp + duration + pause

    return tools


def create_materials(n):
    materials = []
    timestamp = datetime.now()
    for i in range(0, n):
        duration = timedelta(minutes=uniform(10.0, 20.0))
        pause = timedelta(minutes=uniform(0.0, 5.0))
        materials.append(
            {"id": uuid.uuid4(), "material": f"Material {i % 2}", "start": timestamp, "end": timestamp + duration,
             "machine": "LHL 01"})

        timestamp = timestamp + duration + pause

    return materials


generated_tools = create_tools(5)
generated_cycles = create_cycles(100)
generated_materials = create_materials(10)


def get_all_assets(name: str) -> Iterable[dict]:
    if name == "Tools":
        return generated_tools
    elif name == "Cycles":
        return generated_cycles
    elif name == "Materials":
        return generated_materials
    else:
        raise Exception("")


if __name__ == '__main__':
    # SELECT t.name, COUNT(SELECT c FROM Cycles [WHERE t.start <= c.start AND c.start < t.end]),
    # LIST(SELECT m.material FROM Materials [WHERE t.start <= m.start AND m.start < t.end])
    # FROM Tools

    # Concrete Example:
    # SELECT t.name, COUNT(SELECT c FROM Cycles) AS "cycles", FLATTEN(SELECT m.material FROM Materials) AS "products",
    # (SELECT m.material, COUNT(SELECT c FROM Cycles) FROM Materials) AS "material_and_count"
    # FROM Tools
    query = Query([
        Projection("name"),
        Aggregation("count", Query([Projection("*")], "Cycles"), name="cycles"),
        Aggregation("flatten", Query([Projection("material")], "Materials"), name="products"),
        SubQuery(
            Query([
                Projection("material"), Aggregation("count", Query([Projection("*")], "Cycles"), name="cycles")
            ], "Materials"), name="material_and_count")
    ], "Tools")

    # Root Context is what defines the boundaries and where to read the entities from
    context = RootContext(get_all_assets, lambda s: agg_functions.get(s))
    results = query.execute(context)

    # The result is a list of dicts representing a (probably nested) table
    print(results)