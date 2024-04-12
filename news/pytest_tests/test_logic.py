from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_user_cant_create_comment(client, form_data, news):
    """Анонимный пользователь не может отправить комментарий"""
    url = reverse("news:detail", args=(news.id,))
    response = client.post(url, data=form_data)
    login_url = reverse("users:login")
    expected_url = f"{login_url}?next={url}"
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, author, form_data, news):
    """Авторизованный пользователь может отправить комментарий"""
    url = reverse("news:detail", args=(news.id,))
    response = author_client.post(url, data=form_data)
    redirect_url = f"{url}#comments"
    assertRedirects(response, redirect_url)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data["text"]
    assert new_comment.news == news
    assert new_comment.author == author


def test_comment_cant_include_bad_words(author_client, news):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse("news:detail", args=(news.id,))
    response = author_client.post(url, data=bad_words_data)
    assertFormError(response, form="form", field="text", errors=WARNING)


def test_author_can_edit_own_comment(author_client, form_data, comment, news):
    url = reverse("news:edit", args=(comment.id,))
    response = author_client.post(url, form_data)
    url_redirect = reverse("news:detail", args=(news.id,))
    assertRedirects(response, f'{url_redirect}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data["text"]


def test_author_can_delete_own_comment(author_client, comment, news):
    url = reverse("news:delete", args=(comment.id,))
    response = author_client.delete(url)
    url_redirect = reverse("news:detail", args=(news.id,))
    assertRedirects(response, f'{url_redirect}#comments')
    assert Comment.objects.count() == 0


def test_user_cant_edit_other_comment(not_author_client, form_data, comment):
    url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


def test_user_cant_delete_other_comment(not_author_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
