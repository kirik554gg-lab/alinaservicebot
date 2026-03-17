import logging
import random
import asyncio
import sys
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# =============================================
# 🔑 ТОКЕН
# =============================================
TOKEN = "8478240025:AAE5SpfCzjJcmlMCEIHdHJnGhFykP4Cuwg8"

# =============================================
# 💬 ПРИВЕТСТВЕННЫЙ ТЕКСТ (замени на свой!)
# =============================================
WELCOME_TEXT = """
Добро пожаловать в службу поддержки Алины ✨

Это комфортное и тихое место создано для того, чтобы каждый твой день был хорошим. Я очень рада, что ты здесь!!

Нажимай минюшечку и выбирай🌷

Разработчики: Алина&Кирилл
"""

# =============================================
# 📋 МЕНЮ
# =============================================
MENU_BUTTONS = [
    ["🌼 Хороший день чтобы..."],
    ["⭐️ Мотивашка"],
    ["🐒 Смешнявки"],
    ["💋 Комплимент"],
    ["💗 Вдохновение"],
    ["💌 Письмо"]
]

# =============================================
# 🌞 ФРАЗЫ — "Хороший день чтобы..."
# =============================================
GOOD_DAY_PHRASES = [
    # ☕ Для себя любимой
    "☕ ...выпить кофе медленно, без спешки, просто наслаждаясь каждым глотком.",
    "🛁 ...принять долгую ванну с пеной и любимой музыкой.",
    "🧖 ...сделать маску для лица и притвориться, что ты в спа.",
    "🌙 ...лечь спать на час раньше и не чувствовать за это вины.",
    "🍳 ...приготовить что-то вкусное — не по необходимости, а с удовольствием.",
    # 🌿 На улице
    "🚶 ...выйти на прогулку без маршрута и идти туда, куда захочется.",
    "🌤 ...найти скамейку в парке и просто посидеть, глядя на небо.",
    "💐 ...собрать букет из того, что растёт вдоль дороги.",
    "🌅 ...встретить закат — не в телефоне, а глазами.",
    "🗺 ...поехать в незнакомый район города и открыть его заново.",
    # 🎨 Творчество
    "🎨 ...достать краски, которые давно ждут своего часа.",
    "🧶 ...начать вязать что-то маленькое — просто чтобы руки были заняты уютным делом.",
    "📓 ...написать несколько страниц в дневник — без плана, просто мысли вслух.",
    "📸 ...сфотографировать всё, что кажется красивым сегодня.",
    "👩‍🍳 ...попробовать новый рецепт, который давно лежит в закладках.",
    # 📚 Для ума и вдохновения
    "📖 ...начать ту книгу, до которой никак не доходили руки.",
    "🎧 ...послушать подкаст о чём-то совершенно новом для себя.",
    "🌍 ...посмотреть документальный фильм о месте, куда мечтаешь поехать.",
    "🗣 ...выучить 10 слов на языке, который давно хочется знать.",
    "✨ ...перечитать любимую книгу детства — как будто впервые.",
    # 💛 Уют и тепло
    "🌸 ...купить себе цветы — просто так, без повода.",
    "🕯 ...зажечь свечу и посидеть в тишине с чашкой чая.",
    "🎬 ...пересмотреть любимый фильм, который всегда поднимает настроение.",
    "💌 ...написать письмо человеку, о котором давно думаешь.",
    "💃 ...устроить дома танцы под любимый плейлист — никто не смотрит!",
    # 🌟 Маленькие авантюры
    "🎓 ...записаться на тот мастер-класс, который откладывался месяцами.",
    "🌄 ...попробовать новый маршрут для утренней прогулки.",
    "☕ ...зайти в кафе, где ты никогда не была, и заказать что-то незнакомое.",
    "🍓 ...сходить на рынок и выбрать фрукты и цветы просто по настроению.",
    "🌈 ...ничего не планировать и позволить дню сложиться самому — иногда это лучшее, что можно сделать.",
]

# =============================================
# 💪 МОТИВАШКИ
# =============================================
MOTIVATION_PHRASES = [
    # 🌸 Тёплые слова
    "💫 Ты заслуживаешь всего самого лучшего — просто потому что ты есть.",
    "🌟 Даже в самый серый день ты несёшь с собой свет.",
    "💛 Твоя доброта меняет мир вокруг тебя — даже когда ты этого не замечаешь.",
    "💪 Ты сильнее, чем думаешь, храбрее, чем кажется, и любимее, чем можешь представить.",
    "🌸 Разрешай себе отдыхать. Даже цветы закрываются на ночь.",
    # 📜 Цитаты великих
    "✨ Всё будет хорошо в конце. Если не хорошо — значит, это ещё не конец. — Оскар Уайльд",
    "🎯 Верь, что ты можешь, — и ты уже на полпути к цели. — Теодор Рузвельт",
    "🎵 Жизнь — это то, что происходит, пока ты строишь другие планы. — Джон Леннон",
    "🌈 Счастье — это не станция назначения, а способ путешествовать. — Маргарет Ли Рунбек",
    "🌠 Ты никогда не стара, чтобы поставить новую цель или мечтать о новой мечте. — К.С. Льюис",
    # 🎬 Из кино и мультфильмов
    "🐟 Просто продолжай плыть. — Дори, В поисках Немо",
    "🌺 Я не буду сдаваться — я докажу им всем, на что способна. — Мулан",
    "🍯 Какой чудесный день! Самое время сделать что-нибудь приятное. — Винни Пух",
    "🕯 Счастье можно найти даже в тёмные времена, если не забывать обращаться к свету. — Дамблдор",
    "🐦 Главное — не бояться мечтать. А ещё — хорошо кушать! — Кар Карыч, Смешарики",
    # 🦋 Маленькие напоминалки
    "☀️ Каждое утро — это шанс начать именно то, что ты откладывала.",
    "🪜 Не обязательно видеть всю лестницу — просто сделай первый шаг.",
    "🔥 Ошибки не делают тебя неудачницей. Они делают тебя опытной.",
    "🦋 Позволь себе быть в процессе. Бабочка тоже была гусеницей.",
    "💫 Иногда самое смелое, что можно сделать — это просто продолжать.",
    # 💕 О себе с любовью
    "🛁 Ты не должна быть продуктивной каждый день. Иногда просто быть — уже достаточно.",
    "😊 Твоя улыбка — это подарок всем, кто рядом.",
    "🍀 Люди, которым повезло тебя знать, — очень счастливые люди.",
    "💆 Позаботься о себе так же хорошо, как ты заботишься о других.",
    "📖 Ты — главный герой своей истории. И история эта прекрасна.",
    # 🌻 На каждый день
    "🌞 Сегодня — хороший день, чтобы сделать что-то, что сделает тебя счастливой.",
    "🍓 Маленькие радости и есть настоящая жизнь.",
    "🗺 Доверяй своему пути, даже если сейчас ты не видишь карты.",
    "💎 Всё, что тебе нужно — уже внутри тебя.",
    "🌟 Ты справлялась со всем, что было до этого. Справишься и с этим.",
]

# =============================================
# 😂 СМЕШНЯВКИ — картинки (file_id)
# =============================================
FUNNY_IMAGES = [
    "AgACAgIAAxkBAAFFEARpubbzxIhN4G7prEJgJjWmPyymQgACVhlrG6se0Eks-3kot8V9vQEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEAVpubbz4XXW7v7CFuIPTwbh2Q-NwwACVxlrG6se0EnHMle3PXiugQEAAwIAA3gAAzoE",
    "AgACAgIAAxkBAAFFEAZpubbzLbeRcZmvei9SMxJNCWXAHwACWBlrG6se0EnHy9UZcHhT0QEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEAdpubbzi6W9j5K16vjx-BlP-mxzBAACWRlrG6se0EkM828JalwnuAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEAhpubbz-YIX96tVgdvvmDqc3BSEUQACWhlrG6se0EkVyG9qWvUogAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEAlpubbz2O8ZzmypEtmzexFpjQwqggACXxlrG6se0EnJQ2E3H3u1IwEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEAppubbzlj-CDgm-5Wgh3M76YevmjAACWxlrG6se0EnlyzxUSAK-mAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEAtpubbzeLB28DogjkVl23oxFKtsBAACXBlrG6se0En4I3qcFGAhugEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEAxpubbzIDLzURR5rwpRUU2FajSchwACYRlrG6se0EmJG12lvt_RAwEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEA1pubbzuJ7FeRzDSL0cZ6ET2d9fJwACXRlrG6se0EnejxmgWmdPsAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEA5pubbz8vouiaC8KubEEZwFyAsGJAACXhlrG6se0Eka7hEf036VjAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEA9pubbz2yaEJ4IAAf-M2zGZdQQsirsAAmAZaxurHtBJNxfehvl65QABAQADAgADcwADOgQ",
    "AgACAgIAAxkBAAFFEBBpubbz2ZO5CqRHOp_c36AZdnF-xwACYhlrG6se0EkTI1PWkarsOgEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEBFpubbzCuQTBTM-G6ju28Lw6FWwPgACYxlrG6se0Eli7R_8q9W9pAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEBJpubbzCvyEh1V-DuRYZuX_xzRl3gACZBlrG6se0Eme6vn3LH_VEwEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEBNpubbzX0z2IaJlgDLs1p6qZihJ0AACZRlrG6se0ElcwOpBY00bfgEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEBRpubbzWEQbUJU5RyMTEkfxE9nYngACZhlrG6se0Em9ZGe5GBxDogEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEBVpubbzfPgHCuXw5oPkg2992yemKgACZxlrG6se0ElozmMZHLDujAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEBZpubbz2si6xMtqXGzJLSx2nG5W_AACaBlrG6se0EkO3gzmf_3qGgEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEBdpubbziEj-iMgO1ZC4Brr1TEo4CwACaRlrG6se0En6n7NORghv4wEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEBhpubbzDlf6LglSswgMXDfWdLHLqAACahlrG6se0El7jEBdPu3xDgEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEBlpubbzipQpVoztUwJCtDXyCNB49AACaxlrG6se0EmgI2lJJgAB_u0BAAMCAANzAAM6BA",
    "AgACAgIAAxkBAAFFEBtpubbzjOLo1JwqU3LEXrBnV5wL7QACbRlrG6se0EkhTN9lTg7UBwEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEBppubbzeqCnGdgUA4xINF9OPwR61AACbBlrG6se0EnRPxr3oDzWkAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEBxpubbzJVunr5gJXvX1KO07pi-X2gACbhlrG6se0En1tCfl7k-7mQEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEB1pubbzlzSD1Cn53CiMPboNS8eHHQACbxlrG6se0EmPXZtVKfIqYgEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEB5pubbzzakCWJUfAZYOZbKjLZCqBQACcBlrG6se0ElWpZjgjkLFKAEAAwIAA20AAzoE",
    "AgACAgIAAxkBAAFFEB9pubbzS9_XTT83quyugB5WtlxWvAACcRlrG6se0EnfOu6TbVX3EQEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFECBpubbzhtzD-1toYX1RWF_3nwK1UgACchlrG6se0EnMQsq5AknKhwEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFECFpubbzK0Wmc2nSgyPMa_Jj-GSBzQACcxlrG6se0ElQAdIJGmev1QEAAwIAA3MAAzoE",
]


# =============================================
# 💋 КОМПЛИМЕНТЫ
# =============================================
COMPLIMENT_PHRASES = [
    # 💄 Внешность
    "💋 У тебя такая улыбка, что рядом с ней хочется улыбаться самой.",
    "✨ Ты умеешь выглядеть красиво даже тогда, когда совсем не стараешься.",
    "👁 В твоих глазах столько жизни — в них можно читать целые истории.",
    "🩰 Ты носишь себя с такой лёгкостью и грацией, что это само по себе искусство.",
    "🎶 Твой смех — один из самых красивых звуков на свете.",
    # 💛 Характер и душа
    "🕊 Ты один из тех редких людей, рядом с которыми сразу становится спокойно.",
    "💎 В тебе есть что-то настоящее — и это чувствуется с первых минут общения.",
    "🫶 Ты умеешь слушать так, что человек чувствует себя по-настоящему услышанным.",
    "🦋 Твоя доброта — не слабость, это твоя суперсила.",
    "🌿 Ты никогда не теряешь себя, даже когда вокруг всё меняется.",
    # 🧠 Ум и таланты
    "🌊 Ты думаешь глубже, чем большинство людей — и это восхищает.",
    "🌸 У тебя удивительная способность находить красоту там, где другие её не замечают.",
    "💡 Твои идеи всегда свежие, неожиданные и такие... твои.",
    "⚡ Ты схватываешь всё на лету — это редкий дар.",
    "🎤 Когда ты говоришь — хочется слушать. Серьёзно.",
    # 🤝 В отношениях с людьми
    "🌺 Рядом с тобой люди расцветают — ты это умеешь.",
    "💞 Ты из тех друзей, которых хочется беречь и не отпускать.",
    "🔮 Ты умеешь поддержать так точно и вовремя, будто читаешь мысли.",
    "🤍 С тобой можно молчать — и это тоже будет хорошо.",
    "🙌 Твоя забота — это не слова, это действия. И это очень много значит.",
    # 💪 Сила и внутренний стержень
    "🏔 Ты прошла через многое — и осталась собой. Это настоящая сила.",
    "🌱 Ты умеешь падать и вставать — тихо, без драмы, с достоинством.",
    "🔥 В тебе есть стойкость, которую невозможно сломить.",
    "🦁 Ты не боишься быть собой — и это один из самых смелых поступков.",
    "⭐ Даже в моменты сомнений ты продолжаешь идти. Это восхищает.",
    # 🌟 Просто — о ней
    "🌍 Мир немного лучше, потому что в нём есть ты.",
    "🕯 Ты — то самое человеческое тепло, которого так не хватает в жизни.",
    "🎁 Знать тебя — это уже подарок.",
    "💗 Ты заслуживаешь той же любви и заботы, которую сама даришь другим.",
    "👑 Ты прекрасна. Не иногда, не в хорошие дни — всегда.",
]

# =============================================
# 💗 ВДОХНОВЕНИЕ — картинки (file_id)
# =============================================
INSPIRATION_IMAGES = [
    "AgACAgIAAxkBAAFFEIZpub_RMT7Z-K32qnuRkWM6Q1S_5gAC3BlrG6se0EkqYIOahWuglwEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEIdpub_R9ii0XwytWAbXd6Rsw51TAQAC3RlrG6se0EkYD4qT-e0swgEAAwIAA3gAAzoE",
    "AgACAgIAAxkBAAFFEIhpub_REC4FrQNnayY_GOhwP2FBZgAC3hlrG6se0En7J6lGLt9zXgEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEIlpub_R7U8RuZCjLnzdBmwNvatUdQAC3xlrG6se0Elph1soQ27IJAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEIppub_ReRn4XYhE_whY9WyKwIuKJwAC4BlrG6se0ElhlIrcpAucPAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEItpub_RDyEkWJ2gc2i-Pz9jnqHloAAC4RlrG6se0En8d92BDQo8ZQEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEIxpub_RkUq2j2vH-V5Jd58uxgFbWAAC4hlrG6se0EnJ0A9Oh17q4QEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEI1pub_RodSo_sSbRWMytS9sZWyXGwAC4xlrG6se0Em_WpylSoQTqAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEI5pub_RXUTn3kXKapCx4kin0WdlmAAC5BlrG6se0EkFdxnnRE2hygEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEI9pub_S8Rht3ATN0gcy4I5vyWA0-gAC5RlrG6se0EnYtbwqw24jlwEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJBpub_SjGf9Wm8JoPDzv4340XG1AwAC5hlrG6se0Ek44L9GbhbLkgEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJFpub_SQMl2XPsH41w_oOJiNc3XGwAC5xlrG6se0En9BIX30LDIQQEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJJpub_SjvVuAwABB6gbf6mZuzk_3jIAAugZaxurHtBJvr757kYISo8BAAMCAANzAAM6BA",
    "AgACAgIAAxkBAAFFEJNpub_STxQPseR4kp0M1AABydx52HwAAukZaxurHtBJyRqOnvDFYwIBAAMCAANzAAM6BA",
    "AgACAgIAAxkBAAFFEJRpub_SrY7HJ9GeohuOsFhL2E2xKQAC6hlrG6se0EknNQTSGmHO4wEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJVpub_SJ3O7D2NioBIQvWqWT2D3-wAC6xlrG6se0Ek7CyEOCKajywEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJZpub_ShPDAGvZz5NyDImnqJm2_ZwAC7BlrG6se0Eml0HYOeG6m5QEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJdpub_Sq8nXWZWXBO6P7qXhB95hHwAC7RlrG6se0EmUv7kAAa3nOO0BAAMCAANzAAM6BA",
    "AgACAgIAAxkBAAFFEJhpub_SLNDdOpGW9Ve6W-7RERrMFAAC7hlrG6se0EmqGihNxsD-LwEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJlpub_Sy51DVLhjirqpmz3qfbNVsgAC7xlrG6se0EmMnWN_wbyxmwEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJppub_Ss4IuBvHdyKqLSYqY30KoOQAC8BlrG6se0EnR-366KRlHIwEAAwIAA20AAzoE",
    "AgACAgIAAxkBAAFFEJtpub_SOHY_r5MqpDLBTaBIS-Pg6wAC8RlrG6se0EkdWapVAc0JlgEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJxpub_SC5aSwVxHYSV210vOHyGkLAAC8hlrG6se0Em_fnYCK1g_2gEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJ1pub_SjF33qdckjrWs88-fdcqsKAAC-hlrG6se0EnSHnxED9RZeQEAAwIAA20AAzoE",
    "AgACAgIAAxkBAAFFEJ5pub_S-9k7C9lEqS2EUhmM3YaZ2QAC8xlrG6se0EliVLs5XRcWdQEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJ9pub_SjCRn3ZNwrrDePL15bUD38AAC9BlrG6se0ElKPyhgJjzTlAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEKBpub_S6OwwtttI1IjKN7gjA3SP4wAC9RlrG6se0EmqglqaPWiwEAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEKJpub_S75VLVzo3bfXdSeyw9g_rqQAC9xlrG6se0Emeuw3oeqEs5gEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEKFpub_S5B5ZihW0TzI8-Q-UDufrxgAC9hlrG6se0EkOiLN_kf1dIgEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEKNpub_SjySj3MsB6hUNjxXpQkMmDgAC-BlrG6se0Ekro-z3LbSBzwEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEKRpub_S_mxcCH--1TbExj5A8DLsKAAC-RlrG6se0EkNk4npVhMfPgEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEKVpub_SDZe6f-LAeO9ksfVB6Yua9QAC-xlrG6se0EmKNqRhKJziwQEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEKZpub_SuMYEZcMX3J4-d_nnn_Qe3AAC_BlrG6se0Elt_WNNC7LMIAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEKdpub_SPTDj_1DneTSf7caej3K7PQAC_RlrG6se0EnVeC3of1F1cgEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEKhpub_Sm4wRfNLwYNc7D39Nl_GNhgAC_hlrG6se0EnRAYnETWm_oQEAAwIAA3MAAzoE",
]

# =============================================
# 💌 ПИСЬМО
# =============================================
LETTER_TEXT = """💌 *Письмо для тебя...*

Текст письма будет здесь совсем скоро 🌸
"""

# =============================================
# ⚙️ ЛОГИКА БОТА
# =============================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def get_menu_keyboard():
    keyboard = [[KeyboardButton(btn[0])] for btn in MENU_BUTTONS]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        WELCOME_TEXT,
        reply_markup=get_menu_keyboard()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🌼 Хороший день чтобы...":
        phrase = random.choice(GOOD_DAY_PHRASES)
        await update.message.reply_text(
            f"🌼 *Хороший день чтобы...*\n\n{phrase}",
            parse_mode="Markdown",
            reply_markup=get_menu_keyboard()
        )
    elif text == "⭐️ Мотивашка":
        phrase = random.choice(MOTIVATION_PHRASES)
        await update.message.reply_text(
            f"⭐️ *Мотивашка дня:*\n\n{phrase}",
            parse_mode="Markdown",
            reply_markup=get_menu_keyboard()
        )
    elif text == "🐒 Смешнявки":
        image = random.choice(FUNNY_IMAGES)
        await update.message.reply_photo(
            photo=image,
            reply_markup=get_menu_keyboard()
        )
    elif text == "💋 Комплимент":
        phrase = random.choice(COMPLIMENT_PHRASES)
        await update.message.reply_text(
            "💋 *Комплимент для тебя:*\n\n" + phrase,
            parse_mode="Markdown",
            reply_markup=get_menu_keyboard()
        )

    elif text == "💗 Вдохновение":
        image = random.choice(INSPIRATION_IMAGES)
        await update.message.reply_photo(
            photo=image,
            reply_markup=get_menu_keyboard()
        )

    elif text == "💌 Письмо":
        await update.message.reply_text(
            LETTER_TEXT,
            parse_mode="Markdown",
            reply_markup=get_menu_keyboard()
        )

    else:
        await update.message.reply_text(
            "Выбери что-нибудь из меню 👇",
            reply_markup=get_menu_keyboard()
        )


# =============================================
# 🚀 ЗАПУСК — совместимо с Python 3.14 + Windows
# =============================================

async def run_bot():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)

    print("✅ Бот запущен! Нажми Ctrl+C чтобы остановить.")

    stop_event = asyncio.Event()
    try:
        await stop_event.wait()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        print("\n⏳ Останавливаю бота...")
        await app.updater.stop()
        await app.stop()
        await app.shutdown()
        print("👋 Бот остановлен.")


if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен.")# =============================================
# 💗 ВДОХНОВЕНИЕ — картинки (file_id)
# =============================================
INSPIRATION_IMAGES = [
    "AgACAgIAAxkBAAFFEIZpub_RMT7Z-K32qnuRkWM6Q1S_5gAC3BlrG6se0EkqYIOahWuglwEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEIdpub_R9ii0XwytWAbXd6Rsw51TAQAC3RlrG6se0EkYD4qT-e0swgEAAwIAA3gAAzoE",
    "AgACAgIAAxkBAAFFEIhpub_REC4FrQNnayY_GOhwP2FBZgAC3hlrG6se0En7J6lGLt9zXgEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEIlpub_R7U8RuZCjLnzdBmwNvatUdQAC3xlrG6se0Elph1soQ27IJAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEIppub_ReRn4XYhE_whY9WyKwIuKJwAC4BlrG6se0ElhlIrcpAucPAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEItpub_RDyEkWJ2gc2i-Pz9jnqHloAAC4RlrG6se0En8d92BDQo8ZQEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEIxpub_RkUq2j2vH-V5Jd58uxgFbWAAC4hlrG6se0EnJ0A9Oh17q4QEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEI1pub_RodSo_sSbRWMytS9sZWyXGwAC4xlrG6se0Em_WpylSoQTqAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEI5pub_RXUTn3kXKapCx4kin0WdlmAAC5BlrG6se0EkFdxnnRE2hygEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEI9pub_S8Rht3ATN0gcy4I5vyWA0-gAC5RlrG6se0EnYtbwqw24jlwEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJBpub_SjGf9Wm8JoPDzv4340XG1AwAC5hlrG6se0Ek44L9GbhbLkgEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJFpub_SQMl2XPsH41w_oOJiNc3XGwAC5xlrG6se0En9BIX30LDIQQEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJJpub_SjvVuAwABB6gbf6mZuzk_3jIAAugZaxurHtBJvr757kYISo8BAAMCAANzAAM6BA",
    "AgACAgIAAxkBAAFFEJNpub_STxQPseR4kp0M1AABydx52HwAAukZaxurHtBJyRqOnvDFYwIBAAMCAANzAAM6BA",
    "AgACAgIAAxkBAAFFEJRpub_SrY7HJ9GeohuOsFhL2E2xKQAC6hlrG6se0EknNQTSGmHO4wEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJVpub_SJ3O7D2NioBIQvWqWT2D3-wAC6xlrG6se0Ek7CyEOCKajywEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJZpub_ShPDAGvZz5NyDImnqJm2_ZwAC7BlrG6se0Eml0HYOeG6m5QEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJdpub_Sq8nXWZWXBO6P7qXhB95hHwAC7RlrG6se0EmUv7kAAa3nOO0BAAMCAANzAAM6BA",
    "AgACAgIAAxkBAAFFEJhpub_SLNDdOpGW9Ve6W-7RERrMFAAC7hlrG6se0EmqGihNxsD-LwEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJlpub_Sy51DVLhjirqpmz3qfbNVsgAC7xlrG6se0EmMnWN_wbyxmwEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJppub_Ss4IuBvHdyKqLSYqY30KoOQAC8BlrG6se0EnR-366KRlHIwEAAwIAA20AAzoE",
    "AgACAgIAAxkBAAFFEJtpub_SOHY_r5MqpDLBTaBIS-Pg6wAC8RlrG6se0EkdWapVAc0JlgEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJxpub_SC5aSwVxHYSV210vOHyGkLAAC8hlrG6se0Em_fnYCK1g_2gEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJ1pub_SjF33qdckjrWs88-fdcqsKAAC-hlrG6se0EnSHnxED9RZeQEAAwIAA20AAzoE",
    "AgACAgIAAxkBAAFFEJ5pub_S-9k7C9lEqS2EUhmM3YaZ2QAC8xlrG6se0EliVLs5XRcWdQEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJ9pub_SjCRn3ZNwrrDePL15bUD38AAC9BlrG6se0ElKPyhgJjzTlAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEKBpub_S6OwwtttI1IjKN7gjA3SP4wAC9RlrG6se0EmqglqaPWiwEAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEKJpub_S75VLVzo3bfXdSeyw9g_rqQAC9xlrG6se0Emeuw3oeqEs5gEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEKFpub_S5B5ZihW0TzI8-Q-UDufrxgAC9hlrG6se0EkOiLN_kf1dIgEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEKNpub_SjySj3MsB6hUNjxXpQkMmDgAC-BlrG6se0Ekro-z3LbSBzwEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEKRpub_S_mxcCH--1TbExj5A8DLsKAAC-RlrG6se0EkNk4npVhMfPgEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEKVpub_SDZe6f-LAeO9ksfVB6Yua9QAC-xlrG6se0EmKNqRhKJziwQEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEKZpub_SuMYEZcMX3J4-d_nnn_Qe3AAC_BlrG6se0Elt_WNNC7LMIAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEKdpub_SPTDj_1DneTSf7caej3K7PQAC_RlrG6se0EnVeC3of1F1cgEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEKhpub_Sm4wRfNLwYNc7D39Nl_GNhgAC_hlrG6se0EnRAYnETWm_oQEAAwIAA3MAAzoE",
]
PLACEHOLDER_CLOSE
import asyncio
import sys
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# =============================================
# 🔑 ТОКЕН
# =============================================
TOKEN = "8478240025:AAE5SpfCzjJcmlMCEIHdHJnGhFykP4Cuwg8"

# =============================================
# 💬 ПРИВЕТСТВЕННЫЙ ТЕКСТ (замени на свой!)
# =============================================
WELCOME_TEXT = """
Привет, моя дорогая подруга! 🌸

Я так рада, что ты здесь! 
Этот бот создан специально для тебя с любовью 💕

Выбирай что-нибудь из меню ниже 👇
"""

# =============================================
# 📋 МЕНЮ
# =============================================
MENU_BUTTONS = [
    ["🌼 Хороший день чтобы..."],
    ["⭐️ Мотивашка"],
    ["🐒 Смешнявки"],
    ["💋 Комплимент"],
    ["💗 Вдохновение"],
    ["💌 Письмо"]
]

# =============================================
# 🌞 ФРАЗЫ — "Хороший день чтобы..."
# =============================================
GOOD_DAY_PHRASES = [
    # ☕ Для себя любимой
    "☕ ...выпить кофе медленно, без спешки, просто наслаждаясь каждым глотком.",
    "🛁 ...принять долгую ванну с пеной и любимой музыкой.",
    "🧖 ...сделать маску для лица и притвориться, что ты в спа.",
    "🌙 ...лечь спать на час раньше и не чувствовать за это вины.",
    "🍳 ...приготовить что-то вкусное — не по необходимости, а с удовольствием.",
    # 🌿 На улице
    "🚶 ...выйти на прогулку без маршрута и идти туда, куда захочется.",
    "🌤 ...найти скамейку в парке и просто посидеть, глядя на небо.",
    "💐 ...собрать букет из того, что растёт вдоль дороги.",
    "🌅 ...встретить закат — не в телефоне, а глазами.",
    "🗺 ...поехать в незнакомый район города и открыть его заново.",
    # 🎨 Творчество
    "🎨 ...достать краски, которые давно ждут своего часа.",
    "🧶 ...начать вязать что-то маленькое — просто чтобы руки были заняты уютным делом.",
    "📓 ...написать несколько страниц в дневник — без плана, просто мысли вслух.",
    "📸 ...сфотографировать всё, что кажется красивым сегодня.",
    "👩‍🍳 ...попробовать новый рецепт, который давно лежит в закладках.",
    # 📚 Для ума и вдохновения
    "📖 ...начать ту книгу, до которой никак не доходили руки.",
    "🎧 ...послушать подкаст о чём-то совершенно новом для себя.",
    "🌍 ...посмотреть документальный фильм о месте, куда мечтаешь поехать.",
    "🗣 ...выучить 10 слов на языке, который давно хочется знать.",
    "✨ ...перечитать любимую книгу детства — как будто впервые.",
    # 💛 Уют и тепло
    "🌸 ...купить себе цветы — просто так, без повода.",
    "🕯 ...зажечь свечу и посидеть в тишине с чашкой чая.",
    "🎬 ...пересмотреть любимый фильм, который всегда поднимает настроение.",
    "💌 ...написать письмо человеку, о котором давно думаешь.",
    "💃 ...устроить дома танцы под любимый плейлист — никто не смотрит!",
    # 🌟 Маленькие авантюры
    "🎓 ...записаться на тот мастер-класс, который откладывался месяцами.",
    "🌄 ...попробовать новый маршрут для утренней прогулки.",
    "☕ ...зайти в кафе, где ты никогда не была, и заказать что-то незнакомое.",
    "🍓 ...сходить на рынок и выбрать фрукты и цветы просто по настроению.",
    "🌈 ...ничего не планировать и позволить дню сложиться самому — иногда это лучшее, что можно сделать.",
]

# =============================================
# 💪 МОТИВАШКИ
# =============================================
MOTIVATION_PHRASES = [
    # 🌸 Тёплые слова
    "💫 Ты заслуживаешь всего самого лучшего — просто потому что ты есть.",
    "🌟 Даже в самый серый день ты несёшь с собой свет.",
    "💛 Твоя доброта меняет мир вокруг тебя — даже когда ты этого не замечаешь.",
    "💪 Ты сильнее, чем думаешь, храбрее, чем кажется, и любимее, чем можешь представить.",
    "🌸 Разрешай себе отдыхать. Даже цветы закрываются на ночь.",
    # 📜 Цитаты великих
    "✨ Всё будет хорошо в конце. Если не хорошо — значит, это ещё не конец. — Оскар Уайльд",
    "🎯 Верь, что ты можешь, — и ты уже на полпути к цели. — Теодор Рузвельт",
    "🎵 Жизнь — это то, что происходит, пока ты строишь другие планы. — Джон Леннон",
    "🌈 Счастье — это не станция назначения, а способ путешествовать. — Маргарет Ли Рунбек",
    "🌠 Ты никогда не стара, чтобы поставить новую цель или мечтать о новой мечте. — К.С. Льюис",
    # 🎬 Из кино и мультфильмов
    "🐟 Просто продолжай плыть. — Дори, В поисках Немо",
    "🌺 Я не буду сдаваться — я докажу им всем, на что способна. — Мулан",
    "🍯 Какой чудесный день! Самое время сделать что-нибудь приятное. — Винни Пух",
    "🕯 Счастье можно найти даже в тёмные времена, если не забывать обращаться к свету. — Дамблдор",
    "🐦 Главное — не бояться мечтать. А ещё — хорошо кушать! — Кар Карыч, Смешарики",
    # 🦋 Маленькие напоминалки
    "☀️ Каждое утро — это шанс начать именно то, что ты откладывала.",
    "🪜 Не обязательно видеть всю лестницу — просто сделай первый шаг.",
    "🔥 Ошибки не делают тебя неудачницей. Они делают тебя опытной.",
    "🦋 Позволь себе быть в процессе. Бабочка тоже была гусеницей.",
    "💫 Иногда самое смелое, что можно сделать — это просто продолжать.",
    # 💕 О себе с любовью
    "🛁 Ты не должна быть продуктивной каждый день. Иногда просто быть — уже достаточно.",
    "😊 Твоя улыбка — это подарок всем, кто рядом.",
    "🍀 Люди, которым повезло тебя знать, — очень счастливые люди.",
    "💆 Позаботься о себе так же хорошо, как ты заботишься о других.",
    "📖 Ты — главный герой своей истории. И история эта прекрасна.",
    # 🌻 На каждый день
    "🌞 Сегодня — хороший день, чтобы сделать что-то, что сделает тебя счастливой.",
    "🍓 Маленькие радости и есть настоящая жизнь.",
    "🗺 Доверяй своему пути, даже если сейчас ты не видишь карты.",
    "💎 Всё, что тебе нужно — уже внутри тебя.",
    "🌟 Ты справлялась со всем, что было до этого. Справишься и с этим.",
]

# =============================================
# 😂 СМЕШНЯВКИ — картинки (file_id)
# =============================================
FUNNY_IMAGES = [
    "AgACAgIAAxkBAAFFEARpubbzxIhN4G7prEJgJjWmPyymQgACVhlrG6se0Eks-3kot8V9vQEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEAVpubbz4XXW7v7CFuIPTwbh2Q-NwwACVxlrG6se0EnHMle3PXiugQEAAwIAA3gAAzoE",
    "AgACAgIAAxkBAAFFEAZpubbzLbeRcZmvei9SMxJNCWXAHwACWBlrG6se0EnHy9UZcHhT0QEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEAdpubbzi6W9j5K16vjx-BlP-mxzBAACWRlrG6se0EkM828JalwnuAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEAhpubbz-YIX96tVgdvvmDqc3BSEUQACWhlrG6se0EkVyG9qWvUogAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEAlpubbz2O8ZzmypEtmzexFpjQwqggACXxlrG6se0EnJQ2E3H3u1IwEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEAppubbzlj-CDgm-5Wgh3M76YevmjAACWxlrG6se0EnlyzxUSAK-mAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEAtpubbzeLB28DogjkVl23oxFKtsBAACXBlrG6se0En4I3qcFGAhugEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEAxpubbzIDLzURR5rwpRUU2FajSchwACYRlrG6se0EmJG12lvt_RAwEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEA1pubbzuJ7FeRzDSL0cZ6ET2d9fJwACXRlrG6se0EnejxmgWmdPsAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEA5pubbz8vouiaC8KubEEZwFyAsGJAACXhlrG6se0Eka7hEf036VjAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEA9pubbz2yaEJ4IAAf-M2zGZdQQsirsAAmAZaxurHtBJNxfehvl65QABAQADAgADcwADOgQ",
    "AgACAgIAAxkBAAFFEBBpubbz2ZO5CqRHOp_c36AZdnF-xwACYhlrG6se0EkTI1PWkarsOgEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEBFpubbzCuQTBTM-G6ju28Lw6FWwPgACYxlrG6se0Eli7R_8q9W9pAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEBJpubbzCvyEh1V-DuRYZuX_xzRl3gACZBlrG6se0Eme6vn3LH_VEwEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEBNpubbzX0z2IaJlgDLs1p6qZihJ0AACZRlrG6se0ElcwOpBY00bfgEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEBRpubbzWEQbUJU5RyMTEkfxE9nYngACZhlrG6se0Em9ZGe5GBxDogEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEBVpubbzfPgHCuXw5oPkg2992yemKgACZxlrG6se0ElozmMZHLDujAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEBZpubbz2si6xMtqXGzJLSx2nG5W_AACaBlrG6se0EkO3gzmf_3qGgEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEBdpubbziEj-iMgO1ZC4Brr1TEo4CwACaRlrG6se0En6n7NORghv4wEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEBhpubbzDlf6LglSswgMXDfWdLHLqAACahlrG6se0El7jEBdPu3xDgEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEBlpubbzipQpVoztUwJCtDXyCNB49AACaxlrG6se0EmgI2lJJgAB_u0BAAMCAANzAAM6BA",
    "AgACAgIAAxkBAAFFEBtpubbzjOLo1JwqU3LEXrBnV5wL7QACbRlrG6se0EkhTN9lTg7UBwEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEBppubbzeqCnGdgUA4xINF9OPwR61AACbBlrG6se0EnRPxr3oDzWkAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEBxpubbzJVunr5gJXvX1KO07pi-X2gACbhlrG6se0En1tCfl7k-7mQEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEB1pubbzlzSD1Cn53CiMPboNS8eHHQACbxlrG6se0EmPXZtVKfIqYgEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEB5pubbzzakCWJUfAZYOZbKjLZCqBQACcBlrG6se0ElWpZjgjkLFKAEAAwIAA20AAzoE",
    "AgACAgIAAxkBAAFFEB9pubbzS9_XTT83quyugB5WtlxWvAACcRlrG6se0EnfOu6TbVX3EQEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFECBpubbzhtzD-1toYX1RWF_3nwK1UgACchlrG6se0EnMQsq5AknKhwEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFECFpubbzK0Wmc2nSgyPMa_Jj-GSBzQACcxlrG6se0ElQAdIJGmev1QEAAwIAA3MAAzoE",
]


# =============================================
# 💋 КОМПЛИМЕНТЫ
# =============================================
COMPLIMENT_PHRASES = [
    # 💄 Внешность
    "💋 У тебя такая улыбка, что рядом с ней хочется улыбаться самой.",
    "✨ Ты умеешь выглядеть красиво даже тогда, когда совсем не стараешься.",
    "👁 В твоих глазах столько жизни — в них можно читать целые истории.",
    "🩰 Ты носишь себя с такой лёгкостью и грацией, что это само по себе искусство.",
    "🎶 Твой смех — один из самых красивых звуков на свете.",
    # 💛 Характер и душа
    "🕊 Ты один из тех редких людей, рядом с которыми сразу становится спокойно.",
    "💎 В тебе есть что-то настоящее — и это чувствуется с первых минут общения.",
    "🫶 Ты умеешь слушать так, что человек чувствует себя по-настоящему услышанным.",
    "🦋 Твоя доброта — не слабость, это твоя суперсила.",
    "🌿 Ты никогда не теряешь себя, даже когда вокруг всё меняется.",
    # 🧠 Ум и таланты
    "🌊 Ты думаешь глубже, чем большинство людей — и это восхищает.",
    "🌸 У тебя удивительная способность находить красоту там, где другие её не замечают.",
    "💡 Твои идеи всегда свежие, неожиданные и такие... твои.",
    "⚡ Ты схватываешь всё на лету — это редкий дар.",
    "🎤 Когда ты говоришь — хочется слушать. Серьёзно.",
    # 🤝 В отношениях с людьми
    "🌺 Рядом с тобой люди расцветают — ты это умеешь.",
    "💞 Ты из тех друзей, которых хочется беречь и не отпускать.",
    "🔮 Ты умеешь поддержать так точно и вовремя, будто читаешь мысли.",
    "🤍 С тобой можно молчать — и это тоже будет хорошо.",
    "🙌 Твоя забота — это не слова, это действия. И это очень много значит.",
    # 💪 Сила и внутренний стержень
    "🏔 Ты прошла через многое — и осталась собой. Это настоящая сила.",
    "🌱 Ты умеешь падать и вставать — тихо, без драмы, с достоинством.",
    "🔥 В тебе есть стойкость, которую невозможно сломить.",
    "🦁 Ты не боишься быть собой — и это один из самых смелых поступков.",
    "⭐ Даже в моменты сомнений ты продолжаешь идти. Это восхищает.",
    # 🌟 Просто — о ней
    "🌍 Мир немного лучше, потому что в нём есть ты.",
    "🕯 Ты — то самое человеческое тепло, которого так не хватает в жизни.",
    "🎁 Знать тебя — это уже подарок.",
    "💗 Ты заслуживаешь той же любви и заботы, которую сама даришь другим.",
    "👑 Ты прекрасна. Не иногда, не в хорошие дни — всегда.",
]

# =============================================
# 💗 ВДОХНОВЕНИЕ — картинки (file_id)
# =============================================
INSPIRATION_IMAGES = [
    "AgACAgIAAxkBAAFFEIZpub_RMT7Z-K32qnuRkWM6Q1S_5gAC3BlrG6se0EkqYIOahWuglwEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEIdpub_R9ii0XwytWAbXd6Rsw51TAQAC3RlrG6se0EkYD4qT-e0swgEAAwIAA3gAAzoE",
    "AgACAgIAAxkBAAFFEIhpub_REC4FrQNnayY_GOhwP2FBZgAC3hlrG6se0En7J6lGLt9zXgEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEIlpub_R7U8RuZCjLnzdBmwNvatUdQAC3xlrG6se0Elph1soQ27IJAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEIppub_ReRn4XYhE_whY9WyKwIuKJwAC4BlrG6se0ElhlIrcpAucPAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEItpub_RDyEkWJ2gc2i-Pz9jnqHloAAC4RlrG6se0En8d92BDQo8ZQEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEIxpub_RkUq2j2vH-V5Jd58uxgFbWAAC4hlrG6se0EnJ0A9Oh17q4QEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEI1pub_RodSo_sSbRWMytS9sZWyXGwAC4xlrG6se0Em_WpylSoQTqAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEI5pub_RXUTn3kXKapCx4kin0WdlmAAC5BlrG6se0EkFdxnnRE2hygEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEI9pub_S8Rht3ATN0gcy4I5vyWA0-gAC5RlrG6se0EnYtbwqw24jlwEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJBpub_SjGf9Wm8JoPDzv4340XG1AwAC5hlrG6se0Ek44L9GbhbLkgEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJFpub_SQMl2XPsH41w_oOJiNc3XGwAC5xlrG6se0En9BIX30LDIQQEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJJpub_SjvVuAwABB6gbf6mZuzk_3jIAAugZaxurHtBJvr757kYISo8BAAMCAANzAAM6BA",
    "AgACAgIAAxkBAAFFEJNpub_STxQPseR4kp0M1AABydx52HwAAukZaxurHtBJyRqOnvDFYwIBAAMCAANzAAM6BA",
    "AgACAgIAAxkBAAFFEJRpub_SrY7HJ9GeohuOsFhL2E2xKQAC6hlrG6se0EknNQTSGmHO4wEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJVpub_SJ3O7D2NioBIQvWqWT2D3-wAC6xlrG6se0Ek7CyEOCKajywEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJZpub_ShPDAGvZz5NyDImnqJm2_ZwAC7BlrG6se0Eml0HYOeG6m5QEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJdpub_Sq8nXWZWXBO6P7qXhB95hHwAC7RlrG6se0EmUv7kAAa3nOO0BAAMCAANzAAM6BA",
    "AgACAgIAAxkBAAFFEJhpub_SLNDdOpGW9Ve6W-7RERrMFAAC7hlrG6se0EmqGihNxsD-LwEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJlpub_Sy51DVLhjirqpmz3qfbNVsgAC7xlrG6se0EmMnWN_wbyxmwEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJppub_Ss4IuBvHdyKqLSYqY30KoOQAC8BlrG6se0EnR-366KRlHIwEAAwIAA20AAzoE",
    "AgACAgIAAxkBAAFFEJtpub_SOHY_r5MqpDLBTaBIS-Pg6wAC8RlrG6se0EkdWapVAc0JlgEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJxpub_SC5aSwVxHYSV210vOHyGkLAAC8hlrG6se0Em_fnYCK1g_2gEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJ1pub_SjF33qdckjrWs88-fdcqsKAAC-hlrG6se0EnSHnxED9RZeQEAAwIAA20AAzoE",
    "AgACAgIAAxkBAAFFEJ5pub_S-9k7C9lEqS2EUhmM3YaZ2QAC8xlrG6se0EliVLs5XRcWdQEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEJ9pub_SjCRn3ZNwrrDePL15bUD38AAC9BlrG6se0ElKPyhgJjzTlAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEKBpub_S6OwwtttI1IjKN7gjA3SP4wAC9RlrG6se0EmqglqaPWiwEAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEKJpub_S75VLVzo3bfXdSeyw9g_rqQAC9xlrG6se0Emeuw3oeqEs5gEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEKFpub_S5B5ZihW0TzI8-Q-UDufrxgAC9hlrG6se0EkOiLN_kf1dIgEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEKNpub_SjySj3MsB6hUNjxXpQkMmDgAC-BlrG6se0Ekro-z3LbSBzwEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEKRpub_S_mxcCH--1TbExj5A8DLsKAAC-RlrG6se0EkNk4npVhMfPgEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEKVpub_SDZe6f-LAeO9ksfVB6Yua9QAC-xlrG6se0EmKNqRhKJziwQEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEKZpub_SuMYEZcMX3J4-d_nnn_Qe3AAC_BlrG6se0Elt_WNNC7LMIAEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEKdpub_SPTDj_1DneTSf7caej3K7PQAC_RlrG6se0EnVeC3of1F1cgEAAwIAA3MAAzoE",
    "AgACAgIAAxkBAAFFEKhpub_Sm4wRfNLwYNc7D39Nl_GNhgAC_hlrG6se0EnRAYnETWm_oQEAAwIAA3MAAzoE",
]

# =============================================
# 💌 ПИСЬМО
# =============================================
LETTER_TEXT = """💌 *Письмо для тебя...*

Текст письма будет здесь совсем скоро 🌸
"""

# =============================================
# ⚙️ ЛОГИКА БОТА
# =============================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def get_menu_keyboard():
    keyboard = [[KeyboardButton(btn[0])] for btn in MENU_BUTTONS]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        WELCOME_TEXT,
        reply_markup=get_menu_keyboard()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🌼 Хороший день чтобы...":
        phrase = random.choice(GOOD_DAY_PHRASES)
        await update.message.reply_text(
            f"🌼 *Хороший день чтобы...*\n\n{phrase}",
            parse_mode="Markdown",
            reply_markup=get_menu_keyboard()
        )
    elif text == "⭐️ Мотивашка":
        phrase = random.choice(MOTIVATION_PHRASES)
        await update.message.reply_text(
            f"⭐️ *Мотивашка дня:*\n\n{phrase}",
            parse_mode="Markdown",
            reply_markup=get_menu_keyboard()
        )
    elif text == "🐒 Смешнявки":
        image = random.choice(FUNNY_IMAGES)
        await update.message.reply_photo(
            photo=image,
            reply_markup=get_menu_keyboard()
        )
    elif text == "💋 Комплимент":
        phrase = random.choice(COMPLIMENT_PHRASES)
        await update.message.reply_text(
            "💋 *Комплимент для тебя:*\n\n" + phrase,
            parse_mode="Markdown",
            reply_markup=get_menu_keyboard()
        )

    elif text == "💗 Вдохновение":
        image = random.choice(INSPIRATION_IMAGES)
        await update.message.reply_photo(
            photo=image,
            reply_markup=get_menu_keyboard()
        )

    elif text == "💌 Письмо":
        await update.message.reply_text(
            LETTER_TEXT,
            parse_mode="Markdown",
            reply_markup=get_menu_keyboard()
        )

    else:
        await update.message.reply_text(
            "Выбери что-нибудь из меню 👇",
            reply_markup=get_menu_keyboard()
        )


# =============================================
# 🚀 ЗАПУСК — совместимо с Python 3.14 + Windows
# =============================================

async def run_bot():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)

    print("✅ Бот запущен! Нажми Ctrl+C чтобы остановить.")

    stop_event = asyncio.Event()
    try:
        await stop_event.wait()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        print("\n⏳ Останавливаю бота...")
        await app.updater.stop()
        await app.stop()
        await app.shutdown()
        print("👋 Бот остановлен.")


if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен.")
