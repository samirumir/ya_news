from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects

from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    "name", ("news:home",),
)
def test_homepage_availability_for_user(client, name):
    """Главная страница доступна анонимному пользователю"""
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize("name", ("news:detail",),)
def test_detailpage_availability_for_user(news, client, name):
    """Страница отдельной новости доступна анонимному пользователю"""
    url = reverse(name, args=(news.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    "parametrized_client, expected_status",
    (
        (pytest.lazy_fixture("not_author_client"), HTTPStatus.NOT_FOUND,),
        (pytest.lazy_fixture("author_client"), HTTPStatus.OK,),
    ),
)
@pytest.mark.parametrize(
    'name', ('news:edit', 'news:delete'),
)
def test_availability_comment_edit_delete_for_author(name, parametrized_client,
                                                     comment, expected_status):
    """Страница редактирования и удаления комментария доступны только автору"""
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "name", ("users:login", "users:logout", "users:signup"),
)
def test_availability_login_logout_pages(name, client):
    """Страницы регистирации, выхода, входа анонимному пользователю"""
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name', ('news:edit', 'news:delete'),
)
def test_user_redirect_to_registration(name, client, comment):
    """При попытке перейти на страницу редактирования или удаления"""
    """комментария анонимный пользователь"""
    """перенаправляется на страницу авторизации."""
    login_url = reverse("users:login")
    url = reverse(name, args=(comment.id,))
    expected_url = f"{login_url}?next={url}"
    response = client.get(url)
    assertRedirects(response, expected_url)
