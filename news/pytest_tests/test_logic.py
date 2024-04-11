from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


"""1Анонимный пользователь не может отправить комментарий.
2Авторизованный пользователь может отправить комментарий.
3Если комментарий содержит запрещённые слова, он не будет опубликован, а форма вернёт ошибку.
4Авторизованный пользователь может редактировать или удалять свои комментарии.
5Авторизованный пользователь не может редактировать или удалять чужие комментарии"""

@pytest.mark.skip
@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, news):
    """Анонимный пользователь не может отправить комментарий"""
    url = reverse("news:detail", args=(news.id,))
    response = client.post(url, data=form_data)
    login_url = reverse("users:login")
    expected_url = f"{login_url}?next={url}"
    assertRedirects(response, expected_url)
    # В базе данных уже имеется один комментарий, для проверки на редактирование и удаление
    assert Comment.objects.count() == 1


@pytest.mark.skip
def test_user_can_create_comment(author_client, author, form_data, news):
    """Авторизованный пользователь может отправить комментарий"""
    url = reverse("news:detail", args=(news.id,))
    response = author_client.post(url, data=form_data)
    redirect_url = f"{url}#comment"
    assertRedirects(response, redirect_url)
    # В базе данных уже имеется один комментарий, для проверки на редактирование и удаление
    assert Comment.objects.count() == 2
    new_note = Comment.objects.get()
    assert new_note.text == form_data["text"]
    assert new_note.news == news.id
    assert new_note.author == author


@pytest.mark.skip
def test_comment_cant_include_bad_words(auth_client, news):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse("news:detail", args=(news.id,))
    response = auth_client.post(url, data=bad_words_data)
    assertFormError(response, form="form", field="text", errors=WARNING)


@pytest.mark.skip
def test_author_can_edit_own_comment(auhtor_client, form_data, comment, news):
    url = reverse("news:edit", args=(comment.id,))
    response = auhtor_client.post(url, form_data)
    assertRedirects(response, reverse("news:detail", args=(news.id)))
    comment.refresh_from_db()
    assert comment.text == form_data["text"]


@pytest.mark.skip
def test_author_can_delete_own_comment(auhtor_client, comment, news):
    url = reverse("news:delete", args=(comment.id,))
    response = auhtor_client.post(url)
    assertRedirects(response, reverse("news:detail", args=(news.id)))
    assert Comment.objects.count() == 0


@pytest.mark.skip
def test_not_author_cant_edit_own_comment(not_auhtor_client, form_data, comment):
    url = reverse("news:edit", args=(comment.id,))
    response = not_auhtor_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


@pytest.mark.skip
def test_not_author_cant_delete_own_comment(not_auhtor_client, comment):
    url = reverse("news:delete", args=(comment.id,))
    response = not_auhtor_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1