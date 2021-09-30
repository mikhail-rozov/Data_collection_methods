import scrapy


class InstaparserItem(scrapy.Item):
    username = scrapy.Field()  # Имя целевого пользователя
    type = scrapy.Field()  # Тип (подписан на, подписчик) (following, followers)
    name = scrapy.Field()  # Полное имя пользователя из группы type, при отсутствии равняется имени профиля
    profile_name = scrapy.Field()  # Имя профиля пользователя из группы type
    user_id = scrapy.Field()  # id пользователя из группы type
    photo_link = scrapy.Field()  # ссылка на фотографию пользователя из группы type
    photo = scrapy.Field()  # подробные данные о фотографии, формируемые после её загрузки на диск
