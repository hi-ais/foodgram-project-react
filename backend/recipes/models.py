from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Модель для реализации тегов."""
    RED = '#EE6363'
    ORANGE = '#FFA500'
    YELLOW = '#FFFF00'
    GREEN = '#90EE90'
    BLUE = '#6495ED'
    DARK_BLUE = '#000080'
    PURPLE = '#9370DB'

    COLOR_CHOICE = (
        (RED, 'Красный'),
        (ORANGE, 'Оранжевый'),
        (YELLOW, 'Жёлтый'),
        (GREEN, 'Зелёный'),
        (BLUE, 'Голубой'),
        (DARK_BLUE, 'Синий'),
        (PURPLE, 'Фиолетовый'),
    )

    name = models.CharField(
        max_length=50,
        verbose_name='Название тега',
        unique=True,
        blank=False
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цветовой HEX-код',
        choices=COLOR_CHOICE,
        unique=True,
        blank=False
    )
    slug = models.SlugField(
        max_length=50,
        verbose_name='Слаг',
        unique=True,
        blank=False
    )

    class Meta:
        verbose_name = ' Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель реализации ингредиетов."""
    name = models.CharField(
        max_length=70,
        verbose_name='Название ингредиента',
        blank=False
    )
    measurement_unit = models.CharField(
        max_length=70,
        verbose_name='Единица измерения',
        blank=False
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='uniq_name-measurement_unit_pair'
            ),
        )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель реализации рецептов."""
    author = models.ForeignKey(
        User,
        related_name='recipies',
        on_delete=models.CASCADE,
        verbose_name='автор рецепта')
    name = models.CharField(
        blank=False,
        verbose_name='Название блюда',
        max_length=50
    )
    image = models.ImageField(
        upload_to='recipes',
        verbose_name='Изображение',
        blank=False
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        blank=False
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        blank=False,
        validators=[MinValueValidator(settings.COOKING_TIME,
                    'Значение не может быть меньше 1')]
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги рецепта',
        blank=False
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientVolume',
        verbose_name='Ингредиенты рецепта',
        related_name='recipies',
        blank=False
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-id',)

    def __str__(self):
        return self.name


class IngredientVolume(models.Model):
    """Модель описывает количество ингредиента в рецепте."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        blank=False,
        validators=(MinValueValidator(
            settings.AMOUNT,
            message='Минимальное количество ингридиентов 1'),)
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='uniq_ingredient-recipe_pair'
            ),
        )

    def __str__(self):
        return f'В рецепте {self.recipe} {self.ingredient} {self.amount}'


class FavoriteRecipe(models.Model):
    """Модель для реализации избранных рецептов."""
    user = models.ForeignKey(
        User,
        verbose_name='Добавивший',
        related_name='user_added',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Избранный рецепт',
        related_name='favorite_recipe',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='uniq_user-recipe_pair'
            ),
        )

    def __str__(self):
        return f'{self.user} добавил в избранное {self.recipe}'


class ShoppingCard(models.Model):
    """Модель для реализаци корзины покупок."""
    user = models.ForeignKey(
        User,
        verbose_name='Владелец корзины',
        related_name='cart_owner',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='cart',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='uniq_cart-user_pair'
            ),
        )

    def __str__(self):
        return f'{self.user} добавил в корзину {self.recipe}'
