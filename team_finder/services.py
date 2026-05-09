from django.core.exceptions import ValidationError
from django.core.paginator import Paginator

from .constants import GITHUB_DOMAIN


def validate_github_url(url):
    if url and GITHUB_DOMAIN not in url:
        raise ValidationError("Ссылка должна вести на GitHub")
    return url


def get_page_obj(request, queryset, per_page):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)
