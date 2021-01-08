
from arch.auth.token import generate_uid
from arch.storage.table import WorkspaceFate, AccountWorkspace, DatasetFate


def workspace_is_exists(app, user_id, name, **kwargs):
    execute_res = app.db.query(WorkspaceFate).filter_by(
            creator=user_id,
            name=name,
            **kwargs
    ).first()
    return execute_res


def dataset_list(app, user_id, **kwargs):
    execute_res = app.db.query(DatasetFate).filter_by(
        user_id=user_id,
        **kwargs
    ).all()
    return execute_res


def dataset_is_exists(app, user_id, one=True, **kwargs):
    execute_res = app.db.query(DatasetFate).filter_by(
        user_id=user_id,
        **kwargs
    )
    if one:
        return execute_res.first()
    else:
        return execute_res.all()


def dataset_save(app, user_id, name, **kwargs):
    app.db.add(DatasetFate(uid=generate_uid(), user_id=user_id, name=name, **kwargs))
    app.db.commit()
