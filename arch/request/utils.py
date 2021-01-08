import os
import sys
from uuid import uuid1
import json
import click
import requests
import traceback

from flask import Response

from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
from flow_client.flow_cli.utils.cli_utils import check_abs_path


def prettify(response, verbose=True):
    if verbose:
        if isinstance(response, requests.models.Response):
            try:
                response_dict = response.json()
            except TypeError:
                response_dict = response.json
        else:
            response_dict = response
        try:
            click.echo(json.dumps(response_dict, indent=4, ensure_ascii=False))
        except TypeError:
            click.echo(json.dumps(response_dict.json, indent=4, ensure_ascii=False))
        click.echo('')
    return response


# def dataset_upload(url, config_data):
#     file = config_data['file']
#     config_temp_path = f"/tmp/{uuid1()}"
#     with open(config_temp_path, "w", encoding="utf-8") as fp:
#         json.dump(config_data, fp)
#     with open(file, 'rb') as fp:
#         data = MultipartEncoder(
#             fields={'file': (file, fp, 'application/octet-stream')}
#         )
#         tag = [0]

#         def read_callback(monitor):
#             if config_data.get('verbose') == 1:
#                 sys.stdout.write("\r UPLOADING:{0}{1}".format("|" * (monitor.bytes_read * 100 // monitor.len), '%.2f%%' % (monitor.bytes_read * 100 // monitor.len)))
#                 sys.stdout.flush()
#                 if monitor.bytes_read / monitor.len == 1:
#                     tag[0] += 1
#                     if tag[0] == 2:
#                         sys.stdout.write('\n')

#         data = MultipartEncoderMonitor(data, read_callback)
#         return access_server('post', url, 'data/upload', json_data=None, data=data,
#                         params=config_data, headers={'Content-Type': data.content_type})
def dataset_upload(file_name, params, url):
    with open(f"/tmp/{file_name}", 'rb') as fp:
        data = MultipartEncoder(
            fields={'file': (file_name, fp, 'application/octet-stream')}
        )
        tag = [0]
        def read_callback(monitor):
            if params.get('verbose') == 1:
                sys.stdout.write("\r UPLOADING:{0}{1}".format("|" * (monitor.bytes_read * 100 // monitor.len), '%.2f%%' % (monitor.bytes_read * 100 // monitor.len)))
                sys.stdout.flush()
                if monitor.bytes_read / monitor.len == 1:
                    tag[0] += 1
                    if tag[0] == 2:
                        sys.stdout.write('\n')
        data = MultipartEncoderMonitor(data, read_callback)
        resp = access_server(
            'post', 
            url, 
            'data/upload', 
            data=data,
            params=params, 
            headers={"Content-Type": data.content_type}
        )
        return resp

def access_server(method, url, postfix, json_data=None, echo=True, **kwargs):
    try:
        url = "/".join([url, postfix])
        response = {}
        if method == 'get':
            response = requests.get(url=url, json=json_data, **kwargs)
        elif method == 'post':
            response = requests.post(url=url, json=json_data, **kwargs)
        if echo:
            prettify(response)
            return response
        else:
            return response
    except Exception as e:
        exc_type, exc_value, exc_traceback_obj = sys.exc_info()
        response = {'retcode': 100, 'retmsg': str(e),
                    'traceback': traceback.format_exception(exc_type, exc_value, exc_traceback_obj)}
        if 'Connection refused' in str(e):
            response['retmsg'] = 'Connection refused. Please check if the fate flow service is started'
            del response['traceback']
        if 'Connection aborted' in str(e):
            response['retmsg'] = 'Connection aborted. Please make sure that the address of fate flow server ' \
                                    'is configured correctly. The configuration file path is: ' \
                                    '{}.'.format(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                os.pardir, os.pardir, 'settings.yaml')))
            del response['traceback']
        if echo:
            prettify(response)
            return ""
        else:
            return Response(json.dumps(response), status=500, mimetype='application/json')
