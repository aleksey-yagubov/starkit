# Импорт пакета setuptools.
import setuptools

from setuptools import setup, Extension

setup(name='starkit', version='0.0.3',  \
      ext_modules=[Extension('starkit', ['src/starkit.c'])])

# Открытие README.rst и присвоение его long_description.
with open("README.rst", "r") as fh:
	long_description = fh.read()

# Определение requests как requirements для того, чтобы этот пакет работал. Зависимости проекта.
# requirements = ["requests<=2.21.0"]

# Функция, которая принимает несколько аргументов. Она присваивает эти значения пакету.
setuptools.setup(
	# Имя дистрибутива пакета. Оно должно быть уникальным, поэтому добавление вашего имени пользователя в конце является обычным делом.
	name="starkit",
	# Номер версии вашего пакета. Обычно используется семантическое управление версиями.
	version="0.0.3",
	# Имя автора.
	author="Babaev Azer Kahraman Ogly",
	# Его почта.
	author_email="7684067@mail.ru",
	# Краткое описание, которое будет показано на странице PyPi.
	description="Python module for soccer humanoid robot",
	license = 'MIT',
	# Длинное описание, которое будет отображаться на странице PyPi. Использует README.rst репозитория для заполнения.
	long_description=long_description,
	# Определяет тип контента, используемый в long_description.
	long_description_content_type="text/markdown",
	# URL-адрес, представляющий домашнюю страницу проекта. Большинство проектов ссылаются на репозиторий.
	url="https://elsiros.org/",
	# Находит все пакеты внутри проекта и объединяет их в дистрибутив.
	packages=setuptools.find_packages(),
	# requirements или dependencies, которые будут установлены вместе с пакетом, когда пользователь установит его через pip.
	# install_requires=requirements,
	# Предоставляет pip некоторые метаданные о пакете. Также отображается на странице PyPi.
	classifiers=[
		"Programming Language :: Python :: 3.9",
		'Programming Language :: C',
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	# Требуемая версия Python.
	python_requires='>=3.6',
)