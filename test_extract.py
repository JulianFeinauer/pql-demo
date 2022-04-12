from extract import Parameter, AutoGeneratedManyToOne, AutoGeneratedField, StateProcessor

config: dict = {
    "Cycle": {
        "id": Parameter("cycle_id"),
        "material_equipped": AutoGeneratedManyToOne("MaterialEquipped", "id")
    },
    "MaterialEquipped": {
        "id": AutoGeneratedField(),
        "material_name": Parameter("material_name"),
    }
}


def run_processor(states):
    """
    Helper Function
    :param states:
    :return:
    """
    processor = StateProcessor(config, states[0])
    processor.reset_fk_constraints_and_autogen_fields()
    for state in states:
        processor.process_state(state)
    results = processor.get_result()
    return results


def test_one():
    states = [
        {"timestamp": 1, "cycle_id": 21, "material_name": "Material 1"},
        {"timestamp": 2, "cycle_id": 21, "material_name": "Material 1"},
        {"timestamp": 3, "cycle_id": 22, "material_name": "Material 1"},
        {"timestamp": 4, "cycle_id": 22, "material_name": "Material 1"},
    ]

    results = run_processor(states)

    assert len(results.get("Cycle")) == 2
    assert len(results.get("MaterialEquipped")) == 1
    assert results.get("Cycle")[0].get("start") == 1
    assert results.get("Cycle")[0].get("end") == 2
    assert results.get("Cycle")[0].get("material_equipped") == 1
    assert results.get("Cycle")[1].get("material_equipped") == 1


def test_two():
    states = [
        {"timestamp": 1, "cycle_id": 21, "material_name": "Material 1"},
        {"timestamp": 2, "cycle_id": 21, "material_name": "Material 1"},
        {"timestamp": 3, "cycle_id": 22, "material_name": "Material 1"},
        {"timestamp": 4, "cycle_id": 22, "material_name": "Material 1"},
    ]

    processor = StateProcessor(config,states[0])
    processor.reset_fk_constraints_and_autogen_fields()
    for state in states:
        processor.process_state(state)

    results = processor.get_result()

    assert len(results.get("Cycle")) == 2
    assert len(results.get("MaterialEquipped")) == 1
    assert results.get("Cycle")[0].get("start") == 1
    assert results.get("Cycle")[0].get("end") == 2
    assert results.get("Cycle")[0].get("material_equipped") == 1
    assert results.get("Cycle")[1].get("material_equipped") == 1


def test_cycle_material_switch():
    states = [
        {"timestamp": 1, "cycle_id": 21, "material_name": "Material 1"},
        {"timestamp": 2, "cycle_id": 21, "material_name": "Material 1"},
        {"timestamp": 3, "cycle_id": 22, "material_name": "Material 2"},
        {"timestamp": 4, "cycle_id": 22, "material_name": "Material 2"},
    ]

    processor = StateProcessor(config,states[0])
    processor.reset_fk_constraints_and_autogen_fields()
    for state in states:
        processor.process_state(state)

    results = processor.get_result()

    assert len(results.get("Cycle")) == 2
    assert len(results.get("MaterialEquipped")) == 2

    assert results.get("MaterialEquipped")[0] == {'end': 2, 'id': 1, 'material_name': 'Material 1', 'start': 1}
    assert results.get("MaterialEquipped")[1] == {'end': 4, 'id': 1, 'material_name': 'Material 2', 'start': 3}

    assert results.get("Cycle")[0] == {'start': 1, 'end': 2, 'id': 21, 'material_equipped': 1}
    # TODO Why does this test fail?
    assert results.get("Cycle")[1] == {'start': 3, 'end': 4, 'id': 22, 'material_equipped': 2}
