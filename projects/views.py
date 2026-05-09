from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from projects.constants import PROJECT_STATUS_CLOSED, PROJECT_STATUS_OPEN
from projects.forms import ProjectForm
from projects.services import get_projects_queryset
from team_finder.constants import (
    HTTP_BAD_REQUEST,
    HTTP_FORBIDDEN,
    PROJECTS_PAGE_SIZE,
)
from team_finder.services import get_page_obj


def project_list_view(request):
    projects = get_projects_queryset().filter(status=PROJECT_STATUS_OPEN)
    page_obj = get_page_obj(request, projects, PROJECTS_PAGE_SIZE)
    return render(request, "projects/project_list.html", {"projects": page_obj})


def project_detail_view(request, project_id):
    project = get_object_or_404(get_projects_queryset(), id=project_id)
    context = {
        "project": project,
        "is_participant": (
            request.user.is_authenticated
            and project.participants.filter(id=request.user.id).exists()
        ),
        "is_owner": request.user == project.owner,
    }
    return render(request, "projects/project-details.html", context)


@login_required
def create_project_view(request):
    form = ProjectForm(request.POST or None)

    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        messages.success(request, "Проект успешно создан")
        return redirect("projects:detail", project_id=project.id)

    return render(
        request,
        "projects/create-project.html",
        {
            "form": form,
            "is_edit": False,
        },
    )


@login_required
def edit_project_view(request, project_id):
    project = get_object_or_404(get_projects_queryset(), id=project_id)

    if project.owner != request.user:
        messages.error(request, "У вас нет прав для редактирования проекта")
        return redirect("projects:detail", project_id=project.id)

    form = ProjectForm(request.POST or None, instance=project)

    if form.is_valid():
        form.save()
        messages.success(request, "Проект успешно обновлён")
        return redirect("projects:detail", project_id=project.id)

    return render(
        request,
        "projects/create-project.html",
        {
            "form": form,
            "is_edit": True,
            "project": project,
        },
    )


@login_required
def toggle_participate_view(request, project_id):
    project = get_object_or_404(get_projects_queryset(), id=project_id)

    if request.user == project.owner:
        return JsonResponse(
            {
                "status": "error",
                "message": "Автор проекта не может выйти из участников",
            },
            status=HTTP_BAD_REQUEST,
        )

    is_participant = project.participants.filter(id=request.user.id).exists()

    if is_participant:
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)

    return JsonResponse(
        {
            "status": "ok",
            "is_participant": not is_participant,
            "participants_count": project.participants.count(),
        }
    )


@login_required
def complete_project_view(request, project_id):
    project = get_object_or_404(get_projects_queryset(), id=project_id)

    if project.owner != request.user:
        return JsonResponse(
            {
                "status": "error",
                "message": "У вас нет прав для завершения проекта",
            },
            status=HTTP_FORBIDDEN,
        )

    if project.status != PROJECT_STATUS_OPEN:
        return JsonResponse(
            {
                "status": "error",
                "message": "Проект уже закрыт",
            },
            status=HTTP_BAD_REQUEST,
        )

    project.status = PROJECT_STATUS_CLOSED
    project.save(update_fields=("status",))

    return JsonResponse(
        {
            "status": "ok",
            "project_status": PROJECT_STATUS_CLOSED,
        }
    )


@login_required
def toggle_favorite_view(request, project_id):
    project = get_object_or_404(get_projects_queryset(), id=project_id)
    is_favorite = request.user.favorites.filter(id=project.id).exists()

    if is_favorite:
        request.user.favorites.remove(project)
    else:
        request.user.favorites.add(project)

    return JsonResponse(
        {
            "status": "ok",
            "favorited": not is_favorite,
        }
    )


@login_required
def favorites_list_view(request):
    favorites = get_projects_queryset(request.user.favorites.all())
    page_obj = get_page_obj(request, favorites, PROJECTS_PAGE_SIZE)
    return render(request, "projects/favorite_projects.html", {"projects": page_obj})
