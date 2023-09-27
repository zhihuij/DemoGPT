import re

from demogpt.chains.prompts.task_definitions import TASK_TYPE2_TASK


def refineKeyTypeCompatiblity(task):
    if task["input_data_type"] == "none":
        if task["input_key"] != "none":
            task["input_key"] = "none"
    if task["output_data_type"] == "none":
        if task["output_key"] != "none":
            task["output_key"] = "none"
    return task           

def checkDTypes(tasks):

    feedback = ""
    for task in tasks:
        name = task["task_type"]

        input_data_type = task["input_data_type"]
        output_data_type = task["output_data_type"]
        input_key = task["input_key"]

        if name not in TASK_TYPE2_TASK:
            feedback += (
                f"There is no task with a name {name}.Please find another way.\n"
            )
            continue

        reference = TASK_TYPE2_TASK[name]
        reference_input = reference["input_data_type"]
        reference_output = reference["output_data_type"]

        if task["step"] == 1:
            if input_key != "none":
                feedback += f"Since {name} is the first task, its input data type is supposed to be none but it is {input_key}.Please find another way.\n"

        elif reference_input == "*":
            continue
        
        elif reference_input.startswith("*") and input_data_type == "list":
            continue
        # Check input data types
        elif reference_input.startswith("*"):
            reference_input = reference_input.replace("*", "")
            if isinstance(input_key, str):
                if input_data_type != reference_input and input_data_type != "none":
                    feedback += f"""
                    {name} expects all inputs as {reference_input} or none but the data type of {input_key} is {input_data_type} not {reference_input}. Please find another way.\n
                    """
            else:
                for res, data_type in zip(input_key, input_data_type):
                    if data_type != reference_input:
                        feedback += f"""
                        {name} expects all inputs as {reference_input} but data type of {res} is {data_type} not {reference_input}. Please find another way.\n
                        """
        elif input_data_type != reference_input:
            feedback += f"""
            {name} expects all inputs as {reference_input} but the data type of {input_key} is {input_data_type} not {reference_input}. Please find another way.\n
            """

        if reference_output == "*":
            continue
        # Check output data types
        elif output_data_type != reference_output:
            if not (reference_output.startswith("*") and output_data_type != "list"):
                feedback += f"""
                {name} should output in {reference_output} data type but it is {output_data_type} not {reference_output}. Please find another way.\n
                """

    valid = len(feedback) == 0

    return {"feedback": feedback, "valid": valid}


def checkPromptTemplates(templates, task, additional_inputs=[]):
    templates = " ".join(list(templates.values()))
    inputs = task["input_key"]
    if inputs == "none":
        inputs = []
    else:
        if isinstance(inputs, str):
            if inputs.startswith("["):
                inputs = inputs[1:-1]
            inputs = [var.strip() for var in inputs.split(",")]
    template_inputs =  inputs + additional_inputs
    feedback = ""
    for input_key in template_inputs:
        if f"{{{input_key}}}" not in templates:
            feedback += f"'{{{input_key}}}' is not included in any of the templates. You must add '{{{input_key}}}' inside of at least one of the templates.\n"

    # now detect extras

    matches = set(re.findall(r"\{([^}]+)\}", templates))

    for match in matches:
        if match not in template_inputs:
            feedback += f"'{{{match}}}' cannot be included nowhere in the templates. You must remove '{{{match}}}'.\n"

    valid = len(feedback) == 0

    return {"feedback": feedback, "valid": valid}