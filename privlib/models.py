from django.db import models

from django.urls import reverse  # To generate URLS by reversing URL patterns
import uuid  # Required for unique book instances
from datetime import date
from django.contrib.auth.models import User  # Required to assign User as a borrower


class Author(models.Model):
    fio = models.CharField(max_length=200)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('died', null=True, blank=True)

    class Meta:
        ordering = ['fio']
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"

    def get_absolute_url(self):
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        return self.fio
        
class Genre(models.Model):
    name = models.CharField("Жанр", max_length=150)

    def __str__(self):
        return self.name

    class Meta:
            verbose_name = "Жанр"
            verbose_name_plural = "Жанры"

class Category(models.Model):
    name = models.CharField("Категория", max_length=150)
    description = models.TextField("Описание")
    url = models.SlugField(max_length=160, unique=True)

    def str(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def get_absolute_url(self):
            return reverse('category-detail', args=[str(self.id)])

class Book(models.Model):
    """Базовые поля книги"""
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', verbose_name="Автор", on_delete=models.SET_NULL, null=True)
    # Foreign Key used because book can only have one author, but authors can have multiple books
    # Author as a string rather than object because it hasn't been declared yet in file.
    summary = models.TextField(max_length=1000, help_text="Общее описание книги")
    isbn = models.CharField('ISBN', max_length=13,
                            unique=True,
                            help_text='13 символов <a href="https://www.isbn-international.org/content/what-isbn'
                                      '">ISBN номер</a>')
    genre = models.ManyToManyField(Genre, help_text="Выберите жанр книги")
    # ManyToManyField used because a genre can contain many books and a Book can cover many genres.
    # Genre class has already been defined so we can specify the object above.
    language = models.TextField(max_length=2, help_text="Код языка в латинице, 2 знака, наприемр ru,en,fr")
    category = models.ForeignKey('Category', verbose_name="Категория", on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['title', 'author']
        verbose_name = "Книга осн"
        verbose_name_plural = "Книги осн"

    def display_genre(self):
        return ', '.join([genre.name for genre in self.genre.all()[:3]])

    display_genre.short_description = 'Жанр'

    def get_absolute_url(self):
        return reverse('book-detail', args=[str(self.id)])

    def __str__(self):
        return self.title


class BookInstance(models.Model):
    """Личные поля книги"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique ID for this particular book across whole library")
    book = models.ForeignKey('Book', on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def is_overdue(self):
        return bool(self.due_back and date.today() > self.due_back)

    GOAL = (
        ('d', 'Хранение'),
        ('o', 'Прочитать'),
        ('a', 'Отдана'),
        ('r', 'Неизвестно'),
    )

    status = models.CharField(
        max_length=1,
        choices=GOAL,
        blank=True,
        default='d',
        help_text='Цель книги')

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)
        verbose_name = "Книга личн"
        verbose_name_plural = "Книги личн"

    def __str__(self):
        return '{0} ({1})'.format(self.id, self.book.title)


