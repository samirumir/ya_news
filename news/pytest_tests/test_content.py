from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects, assertNotContains
from datetime import datetime, timedelta
from django.conf import settings

from django.urls import reverse

from news.forms import CommentForm
from news.models import Comment, News


NUMBER_OF_COMMENT = 5


def test_pages_contains_form_for_auth_client(author_client, news):
    """Авторизованному пользователю доступна форма для отправки комментария"""
    """на странице отдельной новости"""
    url = reverse("news:detail", args=(news.id,))
    response = author_client.get(url)
    assert "form" in response.context
    assert isinstance(response.context["form"], CommentForm)


@pytest.mark.django_db
def test_pages_contains_form_for_not_auth_client(client, news):
    """Анонимному пользователю недоступна форма для отправки комментария"""
    """на странице отдельной новости"""
    url = reverse("news:detail", args=(news.id,))
    response = client.get(url)
    assert "form" not in response.context


@pytest.mark.django_db
def test_news_order_on_homepage(client):
    """Новости отсортированы от самой свежей к самой старой."""
    """Свежие новости в начале списка"""
    today = datetime.today()
    News.objects.bulk_create(
        News(title=f'Новость {index}',
            text='Просто текст.',
            date=today-timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    url = reverse("news:home")
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_news_count(client):
    """Количество новостей на главной странице — не более 10"""
    today = datetime.today()
    News.objects.bulk_create(
        News(title=f'Новость {index}',
            text='Просто текст.',
            date=today-timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    url = reverse("news:home")
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_comment_order_on_detailpage(client, news, author):
    """Комментарии на странице отдельной новости отсортированы"""
    """в хронологическом порядке: старые в начале списка, новые — в конце."""
    today = datetime.today()
    Comment.objects.bulk_create(
        Comment(text=f'Комментарий {index}',
                news=news,
                created=today-timedelta(days=index),
                author=author)
        for index in range(NUMBER_OF_COMMENT)
    )
    response = client.get(reverse("news:detail", args=(news.id,)))
    obj_list = response.context['news']
    all_comments = obj_list.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps