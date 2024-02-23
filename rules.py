import re
from hashlib import md5
from pathlib import Path, PurePath

import commonmark

from simprov import *


def normalize_file_path(file_path) -> Path:
    return Path(file_path.replace("\\", "/"))


def parse_mlrules_comments(text: str, base_path: Path):
    entities = []
    lines = text.split("\n")
    comments = filter(lambda line: line.strip().startswith("//") and "SIMPROV:" in line, lines)

    for comment in comments:
        cleaned_comment = re.sub("^//.*SIMPROV:", "", comment)
        [type, values] = [component.strip() for component in cleaned_comment.split("=")]
        values = [value.strip() for value in values.split(",")]
        if type == "Assumptions":
            for value in values:
                if value == "":
                    continue
                assumption = Entity("Assumption")
                assumption.attributes["File Path"] = (base_path / value).as_posix().lower()
                entities.append(assumption)
        elif type == "Requirements":
            for value in values:
                if value == "":
                    continue
                requirement = Entity("Requirement")
                requirement.attributes["File Path"] = (base_path / value).as_posix().lower()
                entities.append(requirement)
        elif type == "Research Question":
            research_question = Entity("Research Question")
            research_question.attributes["File Path"] = (base_path / values[0]).as_posix().lower()
            entities.append(research_question)
    return entities


def parse_python_comments(text: str, base_path):
    entities = []
    lines = text.split("\n")
    comments = filter(lambda line: line.strip().startswith("#") and "SIMPROV:" in line, lines)
    for comment in comments:
        cleaned_comment = re.sub("^#.*SIMPROV:", "", comment)
        [type, values] = [component.strip() for component in cleaned_comment.split("=")]
        values = [value.strip() for value in values.split(",")]
        if type == "Assumptions":
            for value in values:
                if value == "":
                    continue
                assumption = Entity("Assumption")
                assumption.attributes["File Path"] = (base_path / value).as_posix().lower()
                entities.append(assumption)
        elif type == "Requirements":
            for value in values:
                if value == "":
                    continue
                requirement = Entity("Requirement")
                requirement.attributes["File Path"] = (base_path / value).as_posix().lower()
                entities.append(requirement)
        elif type == "Simulation Model":
            model = Entity("Simulation Model")
            model.attributes["File Path"] = (base_path / values[0]).as_posix().lower()
            entities.append(model)
    return entities


def find_list_under_markdown_heading(text, heading):
    parser = commonmark.Parser()
    ast = parser.parse(text)

    heading_found = False
    items = []
    for node in ast.walker():
        if node[0].t == "heading" and node[0].first_child is not None and node[0].first_child.literal == heading:
            next_child = node[0].first_child
            heading_found = True
            continue
        if heading_found and node[0].t == "item":
            if node[0].first_child is not None and node[0].first_child.first_child is not None:
                possible_item_text = node[0].first_child.first_child.literal
                items.append(possible_item_text)
    return set(items)


@rule("ResearchQuestion Created")
def process_new_research_question(event):
    activity = Activity("Specifying Research Question")
    used_entities = []
    generated_entities = []

    research_question_file_path = normalize_file_path(event["filePath"])

    research_question = Entity("Research Question")
    research_question.attributes["File Path"] = research_question_file_path.as_posix().lower()
    research_question.attributes["Content"] = event["content"]
    generated_entities.append(research_question)

    reference_items = find_list_under_markdown_heading(event["content"], "References")
    for item in reference_items:
        reference = Entity("Reference")
        reference.attributes["File Path"] = (research_question_file_path.parent / item).as_posix().lower()
        used_entities.append(reference)
    activity.generated_entities = generated_entities
    activity.used_entities = used_entities
    return activity


@rule("ResearchQuestion Specified")
def process_specification_research_question(event):
    activity = Activity("Specifying Research Question")
    used_entities = []
    generated_entities = []

    research_question_file_path = normalize_file_path(event["filePath"])

    old_research_question = Entity("Research Question")
    old_research_question.attributes["File Path"] = research_question_file_path.as_posix().lower()
    used_entities.append(old_research_question)

    research_question = Entity("Research Question")
    research_question.attributes["File Path"] = research_question_file_path.as_posix().lower()
    research_question.attributes["Content"] = event["content"]
    generated_entities.append(research_question)

    reference_items = find_list_under_markdown_heading(event["content"], "References")
    for item in reference_items:
        reference = Entity("Reference")
        reference.attributes["File Path"] = (research_question_file_path.parent / item).as_posix().lower()
        used_entities.append(reference)

    activity.generated_entities = generated_entities
    activity.used_entities = used_entities
    return activity


@rule("Reference Created")
def process_new_reference(event):
    activity = Activity("Specifying Reference")
    used_entities = []
    generated_entities = []

    reference_file_path = normalize_file_path(event["filePath"])

    reference = Entity("Reference")
    reference.attributes["File Path"] = reference_file_path.as_posix().lower()
    reference.attributes["Content"] = event["content"]
    generated_entities.append(reference)

    activity.generated_entities = generated_entities
    activity.used_entities = used_entities
    return activity


@rule("Reference Specified")
def process_specification_reference(event):
    activity = Activity("Specifying Reference")
    used_entities = []
    generated_entities = []

    reference_file_path = normalize_file_path(event["filePath"])

    old_reference = Entity("Reference")
    old_reference.attributes["File Path"] = reference_file_path.as_posix().lower()
    used_entities.append(old_reference)

    reference = Entity("Reference")
    reference.attributes["File Path"] = reference_file_path.as_posix().lower()
    reference.attributes["Content"] = event.get("content", "")
    generated_entities.append(reference)

    activity.generated_entities = generated_entities
    activity.used_entities = used_entities
    return activity


@rule("Requirement Created")
def process_new_requirement(event):
    activity = Activity("Specifying Requirement")
    used_entities = []
    generated_entities = []

    requirement_file_path = normalize_file_path(event["filePath"])

    requirement = Entity("Requirement")
    requirement.attributes["File Path"] = requirement_file_path.as_posix().lower()
    requirement.attributes["Content"] = event["content"]
    generated_entities.append(requirement)

    reference_items = find_list_under_markdown_heading(event["content"], "References")
    for item in reference_items:
        reference = Entity("Reference")
        reference.attributes["File Path"] = (requirement_file_path.parent / item).as_posix().lower()
        used_entities.append(reference)

    activity.generated_entities = generated_entities
    activity.used_entities = used_entities
    return activity


@rule("Requirement Specified")
def process_specification_requirement(event):
    activity = Activity("Specifying Requirement")
    used_entities = []
    generated_entities = []

    requirement_file_path = normalize_file_path(event["filePath"])

    old_requirement = Entity("Requirement")
    old_requirement.attributes["File Path"] = requirement_file_path.as_posix().lower()
    used_entities.append(old_requirement)

    requirement = Entity("Requirement")
    requirement.attributes["File Path"] = requirement_file_path.as_posix().lower()
    requirement.attributes["Content"] = event["content"]
    generated_entities.append(requirement)

    reference_items = find_list_under_markdown_heading(event["content"], "References")
    for item in reference_items:
        reference = Entity("Reference")
        reference.attributes["File Path"] = (requirement_file_path.parent / item).as_posix().lower()
        used_entities.append(reference)

    activity.generated_entities = generated_entities
    activity.used_entities = used_entities
    return activity


@rule("Assumption Created")
def process_new_assumption(event):
    activity = Activity("Specifying Assumption")
    used_entities = []
    generated_entities = []

    assumption_file_path = normalize_file_path(event["filePath"])

    assumption = Entity("Assumption")
    assumption.attributes["File Path"] = assumption_file_path.as_posix().lower()
    assumption.attributes["Content"] = event["content"]
    generated_entities.append(assumption)

    reference_items = find_list_under_markdown_heading(event["content"], "References")
    for item in reference_items:
        reference = Entity("Reference")
        reference.attributes["File Path"] = (assumption_file_path.parent / item).as_posix().lower()
        used_entities.append(reference)

    activity.generated_entities = generated_entities
    activity.used_entities = used_entities
    return activity


@rule("Assumption Specified")
def process_specification_assumption(event):
    activity = Activity("Specifying Assumption")
    used_entities = []
    generated_entities = []

    assumption_file_path = normalize_file_path(event["filePath"])

    old_assumption = Entity("Assumption")
    old_assumption.attributes["File Path"] = assumption_file_path.as_posix().lower()
    used_entities.append(old_assumption)

    assumption = Entity("Assumption")
    assumption.attributes["File Path"] = assumption_file_path.as_posix().lower()
    assumption.attributes["Content"] = event["content"]
    generated_entities.append(assumption)

    reference_items = find_list_under_markdown_heading(event["content"], "References")
    for item in reference_items:
        reference = Entity("Reference")
        reference.attributes["File Path"] = (assumption_file_path.parent / item).as_posix().lower()
        used_entities.append(reference)

    activity.generated_entities = generated_entities
    activity.used_entities = used_entities
    return activity


@rule("SimulationModel Created")
def process_new_model(event):
    activity = Activity("Specifying Simulation Model")
    generated_entities = []

    model_path = normalize_file_path(event["filePath"])

    model = Entity("Simulation Model")
    model.attributes["File Path"] = model_path.as_posix().lower()
    model.attributes["Content"] = event["content"]
    generated_entities.append(model)

    used_entities = parse_mlrules_comments(event["content"], model_path.parent)

    activity.generated_entities = generated_entities
    activity.used_entities = used_entities
    return activity


@rule("SimulationModel Specified")
def process_specification_model(event):
    activity = Activity("Specifying Simulation Model")
    generated_entities = []
    used_entities = []

    model_path = normalize_file_path(event["filePath"])

    old_model = Entity("Simulation Model")
    old_model.attributes["File Path"] = model_path.as_posix().lower()
    used_entities.append(old_model)

    model = Entity("Simulation Model")
    model.attributes["File Path"] = model_path.as_posix().lower()
    model.attributes["Content"] = event["content"]
    generated_entities.append(model)

    used_entities += parse_mlrules_comments(event["content"], model_path.parent)

    activity.generated_entities = generated_entities
    activity.used_entities = used_entities
    return activity


@rule("SimulationExperiment Created")
def process_new_experiment(event):
    activity = Activity("Specifying Simulation Experiment")
    generated_entities = []
    used_entities = []

    experiment_path = normalize_file_path(event["filePath"])

    experiment = Entity("Simulation Experiment")
    experiment.attributes["File Path"] = experiment_path.as_posix().lower()
    experiment.attributes["Content"] = event["content"]
    generated_entities.append(experiment)

    used_entities += parse_python_comments(event["content"], experiment_path.parent)

    activity.generated_entities = generated_entities
    activity.used_entities = used_entities
    return activity


@rule("SimulationExperiment Specified")
def process_specification_experiment(event):
    activity = Activity("Specifying Simulation Experiment")
    generated_entities = []
    used_entities = []

    experiment_path = normalize_file_path(event["filePath"])

    old_experiment = Entity("Simulation Experiment")
    old_experiment.attributes["File Path"] = experiment_path.as_posix().lower()
    used_entities.append(old_experiment)

    experiment = Entity("Simulation Experiment")
    experiment.attributes["File Path"] = experiment_path.as_posix().lower()
    experiment.attributes["Content"] = event["content"]
    generated_entities.append(experiment)

    used_entities += parse_python_comments(event["content"], experiment_path.parent)

    activity.generated_entities = generated_entities
    activity.used_entities = used_entities
    return activity


@rule("Executing Simulation Experiment")
def process_executing_simulation_experiment(event):
    activity = Activity("Executing Simulation Experiment")
    generated_entities = []
    used_entities = []

    experiment_path = normalize_file_path(event["experiment_path"])

    experiment = Entity("Simulation Experiment")
    experiment.attributes["File Path"] = experiment_path.as_posix().lower()
    used_entities.append(experiment)

    # TODO: CHECK
    for path in event["data_paths"]:
        data_path = normalize_file_path(path).as_posix().lower()
        data_entity = Entity("Simulation Data")
        data_entity.attributes["File Path"] = data_path
        if path in event["path_contents"]:
            data_entity.attributes["Contents"] = event["path_contents"][path]
        generated_entities.append(data_entity)

    activity.generated_entities = generated_entities
    activity.used_entities = used_entities
    return activity


@rule("Analyzing Simulation Data")
def process_analyzing_simulation_data(event):
    activity = Activity("Analyzing Simulation Data")
    generated_entities = []
    used_entities = []

    script_path = normalize_file_path(event["script_path"])

    script = Entity("Script")
    hash_text = (script_path.as_posix().lower() + event["script_content"]).encode("utf-8")
    script.attributes["Hash"] = md5(hash_text).hexdigest()
    script.attributes["File Path"] = script_path.as_posix().lower()
    script.attributes["Content"] = event["script_content"]
    used_entities.append(script)

    # TODO: CHECK
    for path in event["simulation_data_paths"]:
        data_entity = Entity("Simulation Data")
        data_entity.attributes["File Path"] = normalize_file_path(path).as_posix().lower()
        used_entities.append(data_entity)

    for path in event.get("used_analysis_result_paths", []):
        analysis_result_entity = Entity("Analysis Result")
        analysis_result_entity.attributes["File Path"] = normalize_file_path(path).as_posix().lower()
        used_entities.append(analysis_result_entity)

    if "analysis_result_path" in event:
        path = event["analysis_result_path"]
        analysis_result_entity = Entity("Analysis Result")
        analysis_result_entity.attributes["File Path"] = normalize_file_path(path).as_posix().lower()
        analysis_result_entity.attributes["Content"] = event["analysis_result_content"]
        generated_entities.append(analysis_result_entity)

    if "visualization_path" in event:
        path = event["visualization_path"]
        visualization_entity = Entity("Visualization")
        visualization_entity.attributes["File Path"] = normalize_file_path(path).as_posix().lower()
        visualization_entity.attributes["Content"] = event["visualization_content"]
        generated_entities.append(visualization_entity)

    used_entities += parse_python_comments(event["script_content"], script_path.parent)
    activity.generated_entities = generated_entities
    activity.used_entities = used_entities
    return activity

