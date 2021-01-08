import json

from flask import request, jsonify, views, g
from flask import current_app as app

from . import register
from arch.auth.token import authorization, generate_uid
from arch.storage.table import WorkspaceFate, AccountWorkspace, DatasetFateWorkspace, DatasetFate
from arch.storage.sql_result_to_dict import model_to_dict


class Workspace(views.MethodView):
    methods = ["get", "post", "put", "patch", "delete"]
    decorators = (authorization,)

    def get(self):
        resp = dict()
        uid = request.args.get("uid")
        user_id = g.token["user_id"]
        if uid:
            execute_res = app.db.query(WorkspaceFate).filter_by(
                uid=uid,
                creator=user_id
                ).first()
        else:
            execute_res = app.db.query(WorkspaceFate).filter_by(
                creator=user_id
                ).all()
        if execute_res:
            result = model_to_dict(execute_res)
            resp["code"] = 200
            resp["data"] = result
        else:
            resp["code"] = 400
        return jsonify(resp)
    
    def post(self):
        """
            Content-Type: application/json

            data = {
                "name": String,
                "description": String,
                "party": List
            }
        """
        resp = {"code": 200}

        json_obj = json.loads(request.get_data())
        user_id = g.token["user_id"]
        execute_res = app.db.query(WorkspaceFate).filter_by(
            creator=user_id,
            name=json_obj.get("name")
            
        ).first()
        if not execute_res:
            ws_uid = generate_uid()
            for i in json_obj.get("party"):
                app.db.add(AccountWorkspace(user_id=i, workspace_uid=ws_uid))
            app.db.add(AccountWorkspace(user_id=user_id, workspace_uid=ws_uid))
            app.db.add(WorkspaceFate(
                uid=ws_uid,
                name=json_obj.get("name"),
                creator=user_id,
                description=json_obj.get("description")
            ))
            app.db.commit()
        else:
            resp["code"] = 400
        return jsonify(resp)
    
    def put(self):
        return ""
    
    def patch(self, uid):
        return ""
    
    def delete(self, uid):
        resp = {"code": 200}

        execute_res = app.db.query(WorkspaceFate).filter_by(
            creator=g.token["user_id"],
            uid=uid
        ).first()
        if execute_res:

            # delete
            app.db.query(AccountWorkspace).filter_by(workspace_uid=uid).delete()
            app.db.delete(execute_res)
            app.db.commit()
        else:
            resp["code"] = 400
        return jsonify(resp)


workspace_view = Workspace.as_view(name='workspace')
register.add_url_rule("/workspace/", view_func=workspace_view, methods=["GET", "POST"])
register.add_url_rule(
    "/workspace/<string:uid>", view_func=workspace_view, methods=["DELETE", "PATCH"]
)


class WorkspaceDataset(views.MethodView):
    methods = ["get", "post", "put", "patch", "delete"]
    decorators = (authorization,)

    def get(self, uid):
        resp = {"code": 400}
        
        user_id = g.token["user_id"]
        workspace_ = app.db.query(AccountWorkspace).filter_by(
            user_id=user_id,
            workspace_uid=uid
        ).first()
        if workspace_:
            execute_res = app.db.query(
                DatasetFateWorkspace, DatasetFate
                ).filter(
                    DatasetFateWorkspace.dataset_uid == DatasetFate.uid,
                    DatasetFateWorkspace.workspace_uid==uid
                     ).with_entities(
                        DatasetFateWorkspace.workspace_uid,
                        DatasetFateWorkspace.dataset_uid,
                        DatasetFate.name
                    ).all()
            print(execute_res)
            if execute_res:
                data_list = list()
                for i in execute_res:
                    data_list.append({
                        "workspace_uid": i[0],
                        "dataset_uid": i[1],
                        "name": i[2],
                    })
                resp["code"] = 200
                resp["data"] = data_list
        return jsonify(resp)
    
    def post(self):
        """
            data = {
                "workspace_uid": String,
                "dataset_uid": String,
            }
        """
        resp = {"code": 200}

        workspace_uid = request.form.get("workspace_uid")
        dataset_uid = request.form.get("dataset_uid")

        user_id = g.token["user_id"]
        execute_res = app.db.query(WorkspaceFate).filter_by(
            creator=user_id,
            uid=workspace_uid
            
        ).first()
        if execute_res:
            result = app.db.query(DatasetFateWorkspace).filter_by(
                dataset_uid=dataset_uid,
                workspace_uid=workspace_uid
                
            ).first()
            if not result:
                app.db.add(DatasetFateWorkspace(dataset_uid=dataset_uid, workspace_uid=workspace_uid))
                app.db.commit()
                resp["msg"] =  "succeed."
            else:
                resp["code"] = 400
                resp["msg"] =  "The dataset is associated with the workspace."
        else:
            resp["code"] = 400
            resp["msg"] = "The workspace is not find."
        return jsonify(resp)
    
    def put(self):
        return ""
    
    def patch(self, uid):
        return ""
    
    def delete(self):
        resp = {"code": 200}

        workspace_uid = request.form.get("workspace_uid")
        dataset_uid = request.form.get("workspace_uid")
        print(workspace_uid)
        print(dataset_uid)

        execute_res = app.db.query(WorkspaceFate).filter_by(
            creator=g.token["user_id"],
            uid=workspace_uid
        ).first()
        print(execute_res)
        if execute_res:
            app.db.query(AccountWorkspace).filter_by(workspace_uid=workspace_uid).delete()
            app.db.query(DatasetFateWorkspace).filter_by(workspace_uid=workspace_uid).delete()
            app.db.delete(execute_res)
            app.db.commit()
        else:
            resp["code"] = 400
        return jsonify(resp)


workspace_dataset_view = WorkspaceDataset.as_view(name='workspace_dataset')
register.add_url_rule("/workspace/dataset/", view_func=workspace_dataset_view, methods=["POST", "DELETE"])
register.add_url_rule(
    "/workspace/dataset/<string:uid>", view_func=workspace_dataset_view, methods=["GET", "PATCH"]
)