import os, sys
import json
import requests

from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

from flask import request, jsonify, views, g
from flask import current_app as app
from flask import Response

from . import register
from arch.auth.token import authorization, generate_uid
from arch.storage.table import WorkspaceFate, AccountWorkspace, DatasetFate
from arch.storage.sql_result_to_dict import model_to_dict
from arch.storage.sql_utils import dataset_is_exists, workspace_is_exists, dataset_save, dataset_list
from arch.request.utils import access_server, dataset_upload


class Dataset(views.MethodView):
    methods = ["get", "post", "put", "patch", "delete"]
    decorators = (authorization,)

    def get(self):
        """
            {
                "uid": String,
                "role": String,
                "party_id": String,
            }
        """
        uid = request.args.get("uid")
        role = request.args.get("role")
        party_id = request.args.get("party_id")

        cfg = g.token["cfg"]["fate"]
        server_url = f"http://{cfg['ip']}:{cfg['port']}/{cfg['version']}"
        if uid:
            resp = dataset_is_exists(app=app, user_id=g.token["user_id"], uid=uid)
            if resp:
                resp = model_to_dict(resp)
                data = {
                    "job_id": resp.get("job_id"),
                    "role": role,
                    "party_id": party_id,
                    "component_name":"upload_0"
                }
                resp = requests.post(f"{server_url}/tracking/component/output/data", json=data).json()
        else:
            resp = dataset_is_exists(app=app, user_id=g.token["user_id"], one=False)
            resp = model_to_dict(resp)
        return jsonify(resp)
    
    def post(self):
        """
            data = {
                "namespace": String,
                "table_name": String,
                "work_mode": Integer(1),
                "head": Integer(1),
                "partition": Integer(1),
                "backend": Integer(0),
                "file": Text
            }
        """
        resp = dict()

        table_name = request.form.get("table_name")
        namespace = request.form.get("namespace")
        user_id = g.token["user_id"]

        if dataset_is_exists(app, user_id, table_name):
            resp["retcode"] = 100
            resp["retmsg"] = "The data table already exists"
            return jsonify(resp)

        file = request.files.get("file")
        file_name = file.filename
        file.save(f"/tmp/{file_name}")

        cfg = g.token["cfg"]["fate"]
        server_url = f"http://{cfg['ip']}:{cfg['port']}/{cfg['version']}"
        print(server_url)
        params = {
                "namespace": namespace,
                "table_name": table_name,
                "work_mode": 1,
                "head": 1,
                "partition": 1,
                "backend": 0,
            }

        resp = dataset_upload(file_name, params, server_url).json()

        if resp.get("retcode") == 0:
            dataset_save(app, user_id, table_name, job_id=resp["jobId"])

        return jsonify(resp)
    
    def put(self):
        """
            data = {
                "table_name": String,
                "file": Text
            }
        """
        resp = {"code": 200}

        name = request.form.get("name")
        file = request.files.get("file")
        user_id = g.token["user_id"]
        cfg = g.token["cfg"]["fate"]
        server_url = f"http://{cfg['ip']}:{cfg['port']}/{cfg['version']}"

        config_data = {
                "file": f"/tmp/{file.filename}",
                "table_name": name,
                "backend": 0,
                "work_mode": 1,
                "partition": 4,
                "head": 1,
                "id_delimiter": ",",
                "drop": 1,
                "namespace": "server_default"
        }
        file.save(config_data["file"])

        # dataset search
        res = access_server(
            "post", 
            server_url,
            "table/table_info", 
            config_data
            )
        if res:
            schema = json.loads(res._content.decode("utf-8")).get("data")["schema"]
            if not schema:
                execute_res = dataset_is_exists(app, user_id, name)
                assert not execute_res

                # dataset upload
                res = dataset_upload(server_url, config_data)
                job_id = json.loads(res._content.decode("utf-8")).get("jobId")
                if not job_id:
                    resp["code"] = 400
                # save info
                dataset_save(app, user_id, name)
                return jsonify(resp)
                 
        resp["code"] = 400
        return jsonify(resp)
    
    def patch(self, uid):
        return ""
    
    def delete(self, uid):
        resp = dict()

        cfg = g.token["cfg"]["fate"]
        server_url = f"http://{cfg['ip']}:{cfg['port']}/{cfg['version']}"

        sql_resp = dataset_is_exists(app=app, user_id=g.token["user_id"], uid=uid)
        if sql_resp:
            resp_dict = model_to_dict(sql_resp)

            data = {
                "table_name": resp_dict["name"],
                "namespace": "test_namespace"
            }

            # fate delete
            resp = requests.post(f"{server_url}/table/delete", json=data).json()
            if resp.get("retcode") == 0:
                #local delete
                app.db.delete(sql_resp)
                app.db.commit()
        else:
            resp["retcode"] = 400
            resp["retmsg"] = "The data table not find"
        return jsonify(resp)


dataset_view = Dataset.as_view(name='dataset')
register.add_url_rule("/dataset/", view_func=dataset_view, methods=["GET", "POST"])
register.add_url_rule(
    "/dataset/<string:uid>", view_func=dataset_view, methods=["DELETE", "PATCH"]
)