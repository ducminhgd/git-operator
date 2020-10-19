from functools import singledispatch


class MasterHandler:
    ...


class MasterExistHandler:
    ...


@singledispatch
def split_task(task):
    print('\tSplit task: ' + task.__class__.__name__)


@singledispatch
def publish_task(task):
    print('\tPublish task: ' + task.__class__.__name__)


def handle(task):
    print('Handle task: ' + task.__class__.__name__)
    split_task(task)
    publish_task(task)


@split_task.register
def _(task: MasterHandler):
    print('\tNo need to split: ' + task.__class__.__name__)


if __name__ == "__main__":
    master = MasterHandler()
    master_exist = MasterExistHandler()

    handle(master)
    handle(master_exist)