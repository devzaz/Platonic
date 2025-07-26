# legal/services.py
import datetime
from .models import Contract, ContractTemplate
from projects.models import Project
from django.core.exceptions import ObjectDoesNotExist

def generate_contract(template_id: int, project_id: int) -> Contract:
    """
    Generates a new Contract instance from a template and project data.

    Args:
        template_id: The primary key of the ContractTemplate to use.
        project_id: The primary key of the Project to source data from.

    Returns:
        The newly created Contract instance.

    Raises:
        ObjectDoesNotExist: If the template or project cannot be found.
    """
    try:
        template = ContractTemplate.objects.get(id=template_id)
        project = Project.objects.get(id=project_id)
    except ObjectDoesNotExist as e:
        # Re-raise the exception to be handled by the calling view.
        raise e

    # --- Build the context dictionary with all possible placeholders ---
    context = {
        "client_name": project.client.name,
        "client_company": project.client.company_name or "N/A",
        "client_address": project.client.address or "N/A",
        "project_name": project.name,
        "project_budget": f"{project.budget:,.2f}", # Formats the number with commas
        "project_start_date": project.start_date.strftime("%B %d, %Y") if project.start_date else "TBD",
        "current_date": datetime.date.today().strftime("%B %d, %Y"),
    }

    # --- Perform the replacement ---
    generated_text = template.content
    for placeholder, value in context.items():
        generated_text = generated_text.replace(f"{{{{{placeholder}}}}}", str(value))

    # --- Create the new contract instance in the database ---
    new_contract = Contract.objects.create(
        project=project,
        template_used=template,
        generated_content=generated_text,
        status='draft' # Start as a draft
    )

    return new_contract