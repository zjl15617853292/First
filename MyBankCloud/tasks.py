from celery import Celery

#Celery异步任务队列，一个基于分布式消息传递的作业队列

def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['mysql+pymysql://root:123456@localhost'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

celery = make_celery(app)