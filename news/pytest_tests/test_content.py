from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects, assertNotContains
from datetime import datetime, timedelta
from django.conf import settings

from django.urls import reverse

from news.forms import CommentForm
from news.models import Comment, News


""""1Количество новостей на главной странице — не более 10.
2Новости отсортированы от самой свежей к самой старой. Свежие новости в начале списка.
3Комментарии на странице отдельной новости отсортированы в хронологическом порядке: старые в начале списка, новые — в конце.
4Анонимному пользователю недоступна форма для отправки комментария на странице отдельной новости, а авторизованному доступна."""


NUMBER_OF_COMMENT = 5

# @pytest.mark.skip
def test_pages_contains_form_for_auth_client(author_client, news):
    """Авторизованному пользователю доступна форма для отправки комментария"""
    """на странице отдельной новости"""
    url = reverse("news:detail", args=(news.id,))
    response = author_client.get(url)
    assert "form" in response.context
    assert isinstance(response.context["form"], CommentForm)


# @pytest.mark.skip
@pytest.mark.django_db
def test_pages_contains_form_for_not_auth_client(client, news):
    """Анонимному пользователю недоступна форма для отправки комментария"""
    """на странице отдельной новости"""
    url = reverse("news:detail", args=(news.id,))
    response = client.get(url)
    assert "form" not in response.context


# @pytest.mark.skip
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
    response = client.get("news:home")
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates)
    assert all_dates == sorted_dates


@pytest.mark.skip
def test_news_count(client):
    """Количество новостей на главной странице — не более 10"""
    today = datetime.today()
    News.objects.bulk_create(
        News(title=f'Новость {index}',
            text='Просто текст.',
            date=today-timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    response = client.get("news:home")
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.skip
def test_comment_order_on_detailpage(client, news):
    """Комментарии на странице отдельной новости отсортированы"""
    """в хронологическом порядке: старые в начале списка, новые — в конце."""
    today = datetime.today()
    Comment.objects.bulk_create(
        Comment(text=f'Новость {index}',
                news=news.id,
                created=today-timedelta(days=index))
        for index in range(NUMBER_OF_COMMENT)
    )
    response = client.get("news:detail", args=(news.id,))
    object_list = response.context['object_list']
    # all_dates = [news.date for news in object_list]
    # sorted_dates = sorted(all_dates, reverse=True)
    all_created = [comments.created for comments in object_list]
    sorted_created = sorted(all_created, reverse=True)
    assert all_created == sorted_created
