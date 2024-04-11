from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects

from django.urls import reverse


"""1Главная страница доступна анонимному пользователю.
2Страница отдельной новости доступна анонимному пользователю.
3Страницы удаления и редактирования комментария доступны автору комментария.
4При попытке перейти на страницу редактирования или удаления комментария анонимный пользователь перенаправляется на страницу авторизации.
5Авторизованный пользователь не может зайти на страницы редактирования или удаления чужих комментариев (возвращается ошибка 404).
6Страницы регистрации пользователей, входа в учётную запись и выхода из неё доступны анонимным пользователям."""


@pytest.mark.skip
@pytest.mark.parametrize(
    "name", ("news:home",),
)
def test_homepage_availability_for_anonymous_user(client, name):
    """Главная страница доступна анонимному пользователю"""
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.skip
@pytest.mark.parametrize("name", ("news:detail",),)
def test_detailpage_availability_for_anonymous_user(news, client, name):
    """Страница отдельной новости доступна анонимному пользователю"""
    url = reverse(name, args=(news.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.skip
@pytest.mark.parametrize(
    "parametrized_client, expected_status",
    (
        (pytest.lazy_fixture("not_author_client"), HTTPStatus.NOT_FOUND,),
        (pytest.lazy_fixture("author_client"), HTTPStatus.OK,),
    ),
)
@pytest.mark.parametrize(
    'name',('news:edit', 'news:delete'),
)
def test_availability_comment_edit_delete_for_author(name, author_client, comment):
    """Страница редактирования и удаления комментария доступны только автору"""
    url = reverse(name, args=(comment.id,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.skip
@pytest.mark.parametrize("name", ("users:login", "users:logout", "users:signup"),)
def test_availability_login_logout_pages(name, client):
    """Страницы регистирации, выхода, входа анонимному пользователю"""
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.skip
@pytest.mark.parametrize(
    'name',('news:edit', 'news:delete'),
    )
def test_anonymous_user_redirect_to_registration(name, client):
    """При попытке перейти на страницу редактирования или удаления комментария"""
    """анонимный пользователь перенаправляется на страницу авторизации."""
    login_url = reverse("users:login")
    url = reverse(name)
    expected_url = f"{login_url}?next={url}"
    response = client.get(url)
    assertRedirects(response, expected_url)
