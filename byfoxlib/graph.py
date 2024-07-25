from byfoxlib.emoji import task1_emoji, task2_emoji, task3_emoji, task4_emoji, task5_emoji, task6_emoji


def create_graph_emoji(x: float, count: int = 10):
    task_count, x = round(x / (100 / count)), round(x)
    if task_count >= count:
        return str(task4_emoji) + str(task5_emoji) * (count - 2) + str(task6_emoji) + f' {x}%'
    task = str(task1_emoji) + str(task2_emoji) * (count - 2) + str(task3_emoji)
    if task_count < 1:
        return task + f' {x}%'
    task = task.replace(str(task1_emoji), str(task4_emoji), 1)
    if task_count > 1:
        task = task.replace(str(task2_emoji), str(task5_emoji), task_count - 1)
    return task + f' {x}%'




