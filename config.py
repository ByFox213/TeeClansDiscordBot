from byfoxlib.model import Post, BotMessage

host = "royal-tee.ru"

application = {
    "channel": 0,  # Канал для отравки сообщение с кнопками
    "mod_channel": 0  # Канал в который будут идти заявки
}

member_role = 0  # Роль учатсника клана(Не сервера)

channel_id = 0  # Канал для отправки всех участников
channel_warning_id = 0  # Канал для отправки варнов(Клан тег и т.д)
err_channel = 0  # Канал для отправки ошибкок

clan_name = ""  # clan tag

TOKEN = ""  # рекомендую ставить токен через переменную DISCORD_TOKEN в окружении

sql = Post(
    host="127.0.0.1",
    port=5435,
    user="royal",
    passwd="",
    db="royal"
)

message = BotMessage(**{
    "clan_app": "Заявка на участие в клане",
    "clan_desk": "Чтобы подать заявку, вам нужно нажать на кнопку и указать ник игрока, возраст и рассказать о себе",
    "remove_user": "Удалён участник",
    "remove": "убран",
    "leave_user": "Вышел",
    "error": "Error",
    "member": "участник",
    "moder": "модератор",
    "deputy": "заместитель",
    "chapter": "глава",
    "programmer": "Программист",
    "forgot2": "Ты забыл ввести значение любое из 2",
    "memberisbot": "Данный пользователь является ботом",
    "something": "Что-то пошло не так😅",
    "player_remove": "Игрок успешно удалён из данного режима",
    "notreg": "Игрок не зарегистрирован",
    "clan_members": "Участники клана"
})
