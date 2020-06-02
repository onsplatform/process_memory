from util import convert_to_utc
from datetime import datetime

from flask_api import status
from flask import Blueprint, request, jsonify, make_response, current_app as app

from pymongo import ASCENDING
from bson.json_util import loads
from process_memory.db import get_database

bp = Blueprint('instances', __name__)


@bp.route("/<uuid:instance_id>/head")
def find_head(instance_id):
    entities, event, fork, maps, instance_filter = _get_memory_body(instance_id)
    if event:
        result = dict()
        result['event'] = event if event else None
        result['map'] = {'content': maps if maps else {}, 'name': event['header']['app_name']}
        result['dataset'] = {'entities': entities if entities else {}}
        result['fork'] = fork if fork else None
        result['processId'] = result['event']['header']['processId']
        result['systemId'] = result['event']['header']['systemId']
        result['instanceId'] = result['event']['header']['instanceId']
        result['eventOut'] = result['event']['header']['eventOut']
        commit = result['event']['header']['commit']
        result['commit'] = commit if commit else False
        result['instance_filter'] = instance_filter if instance_filter else []
        # result['inputs'] = inputs if inputs else []
        return jsonify(result)
    return make_response('', status.HTTP_404_NOT_FOUND)


def _get_memory_body(instance_id):
    event = _get_event_body(instance_id)
    maps = _get_maps(instance_id)
    entities = _get_entities(instance_id)
    fork = get_memory_part(instance_id, 'fork')
    instance_filter = _get_instance_filter(instance_id)
    # inputs = _get_inputs(instance_id)
    return entities, event, fork, maps, instance_filter


def _get_event_body(instance_id):
    event = get_memory_part(instance_id, 'event')
    _format_date(event, 'referenceDate')
    _format_date(event, 'timestamp')
    return event


def _format_date(event, field):
    if event[field]:
        event[field] = event[field].strftime('%Y-%m-%dT%H:%M:%S.%fZ')


@bp.route('/instances/reprocessable/byentities', methods=['POST'])
def instances_reprocessable_by_entities():
    if request.data:
        data = set()
        db = get_database()
        app.logger.debug('getting entities with ids:')
        entities = loads(request.data).pop('entities', None)
        reprocessable_tables_grouped_by_tags = loads(
            request.data).pop('tables_grouped_by_tags', None)

        if entities and reprocessable_tables_grouped_by_tags:
            query_items = {
                "data.id": {"$in": entities},
                "header.image": {"$in": [*reprocessable_tables_grouped_by_tags.keys()]},
                "data._metadata.changeTrack": {"$eq": 'query'}
            }

            for item in db['entities'].find(query_items):
                if item['data']['_metadata']['table'] in reprocessable_tables_grouped_by_tags[item['header']['image']]:
                    data.add(item['header']['instanceId'])

            if data:
                return jsonify(
                    [item['instanceId'] for item in
                     db['event'].find({
                         "instanceId": {"$in": list(data)},
                         'scope': {'$eq': 'execution'}
                     }).sort('timestamp', ASCENDING)])

    return make_response('', status.HTTP_404_NOT_FOUND)


@bp.route("/instances/bytags", methods=['POST'])
def get_instances_by_tags():
    if request.data:
        db = get_database()
        app.logger.debug('getting entities with ids:')
        reprocessable_tables_grouped_by_tags = loads(
            request.data).pop('tables_grouped_by_tags', None)

        if reprocessable_tables_grouped_by_tags:
            query_items = {
                "header.image": {"$in": list({*reprocessable_tables_grouped_by_tags.keys()})},
                "data._metadata.changeTrack": {"$eq": 'query'},
            }

            data = set()

            for item in db['entities'].find(query_items):
                if item['data']['_metadata']['table'] in reprocessable_tables_grouped_by_tags[item['header']['image']]:
                    data.add(item['header']['instanceId'])

            if data:
                return jsonify(
                    [{'id': item['header']['instanceId'], 'tag': item['header']['image']} for item in
                     db['event'].find({
                         "instanceId": {"$in": list(data)},
                         'scope': {'$eq': 'execution'}
                     }).sort('timestamp', ASCENDING)])

    return make_response('', status.HTTP_404_NOT_FOUND)


@bp.route("/events/between/dates", methods=['POST'])
def get_events_between_dates():
    if request.data:
        db = get_database()
        json = loads(request.data)
        date_format = '%Y-%m-%dT%H:%M:%S.%f'
        date_begin_validity = convert_to_utc(json['date_begin_validity'], date_format)
        date_end_validity = convert_to_utc(datetime.now().strftime(date_format), date_format)
        process_id = json['process_id']
        if json['date_end_validity']:
            date_end_validity = convert_to_utc(json['date_end_validity'], date_format)

        app.logger.debug(f'getting events between dates {date_begin_validity} and {date_end_validity}')
        return jsonify(
            [item['instanceId'] for item in
             db['event'].find({
                 'referenceDate': {
                     '$gte': date_begin_validity,
                     '$lte': date_end_validity,
                 },
                 'header.processId': {"$eq": process_id},
                 'scope': {'$eq': 'execution'}
             }).sort('referenceDate', ASCENDING)])

    return make_response('', status.HTTP_404_NOT_FOUND)


def _format_timestamp(date):
    return datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f')


@bp.route("/payload/<uuid:instance_id>", methods=['GET'])
def get_payload(instance_id):
    event = get_memory_part(instance_id, 'event')
    if event:
        return jsonify(event['payload'])

    return make_response('', status.HTTP_404_NOT_FOUND)


@bp.route("/fork/<uuid:instance_id>", methods=['GET'])
def get_fork(instance_id):
    return jsonify(get_memory_part(instance_id, 'fork'))


@bp.route("/event/<uuid:instance_id>", methods=['GET'])
def get_event(instance_id):
    return jsonify(_get_event_body(instance_id))


@bp.route("/event/bynameanddate/<name>/<date_from>", defaults={'date_until': None}, methods=['GET'])
@bp.route("/event/bynameanddate/<name>/<date_from>/<date_until>", methods=['GET'])
def get_event_by_name_and_dates(name, date_from, date_until):
    return jsonify(_get_event_by_name_and_dates(name, date_from, date_until))


@bp.route("/entities/<uuid:instance_id>", methods=['GET'])
def get_entities(instance_id):
    return jsonify(_get_entities(instance_id))


@bp.route("/maps/<uuid:instance_id>", methods=['GET'])
def get_maps(instance_id):
    return jsonify(_get_maps(instance_id))


@bp.route("/instance_filter/<uuid:instance_id>", methods=['GET'])
def get_instance_filter(instance_id):
    return jsonify(_get_instance_filter([str(instance_id)]))


@bp.route("/instance_filters/byinstanceids", methods=['POST'])
def get_instance_filters():
    if request.data:
        instance_ids = loads(request.data).pop('instance_ids', None)
        return jsonify(_get_instance_filter(instance_ids))
    return make_response('', status.HTTP_404_NOT_FOUND)


@bp.route("/inputs/<type>/<uuid:instance_id>", methods=['GET'])
def get_inputs(instance_id, type):
    return jsonify(_get_inputs(instance_id, type))


@bp.route("/instance_filters/byinstanceidsandtypes", methods=['POST'])
def get_instance_filters_by_ids_and_types():
    if request.data:
        instances_ids_and_types = loads(request.data).pop('instances_and_types', None)
        return jsonify(_get_instances_filters_by_ids_and_types(instances_ids_and_types))
    return make_response('', status.HTTP_404_NOT_FOUND)


def get_memory_part(instance_id, collection):
    header_query = {"header.instanceId": str(instance_id)}
    db = get_database()
    data = db[collection].find_one(header_query)
    if data:
        data.pop('_id')
        return data


def _get_event_by_name_and_dates(name, date_from, date_until):
    date_format = '%Y-%m-%dT%H:%M:%S.%f'
    date_from = convert_to_utc(date_from, date_format)
    date_until = convert_to_utc(date_until, date_format) if date_until else convert_to_utc(
        datetime.now().strftime(date_format), date_format)
    header_query = {
        "name": name,
        'referenceDate': {
            '$gte': date_from,
            '$lte': date_until,
        },
    }
    db = get_database()
    data = db['event'].find(header_query)
    return data


def _get_maps(instance_id):
    header_query = {"header.instanceId": str(instance_id)}

    db = get_database()
    items = [item for item in db['maps'].find(header_query)]
    ret = dict()
    for item in items:
        ret[item['type']] = item['data']

    return ret


def _get_entities(instance_id):
    header_query = {"header.instanceId": str(instance_id)}

    db = get_database()
    items = [item for item in db['entities'].find(header_query)]
    ret = dict()
    for item in items:
        if not item['type'] in ret.keys():
            ret[item['type']] = []
        ret[item['type']].append(item['data'])

    return ret


def _get_instance_filter(instance_ids):
    if not isinstance(instance_ids, list):
        instance_ids = [str(instance_ids)]

    header_query = {"header.instanceId": {'$in': instance_ids}}
    return (item for item in get_database()['instance_filter'].find(header_query))


def _get_inputs(instance_id, type=None):
    header_query = {'header.instanceId': {'$eq': str(instance_id)}}
    if type:
        header_query['_metadata.type'] = {'$eq': type}

    return (item for item in get_database()['inputs'].find(header_query))


def _get_instances_filters_by_ids_and_types(instances_ids_and_types):
    filters = []

    for k, v in instances_ids_and_types.items():
        [filters.append(item) for item in _get_instance_filters_by_id_and_types(k, v)]

    return filters


def _get_instance_filters_by_id_and_types(instance_id, types):
    header_query = {
        "header.instanceId": {'$eq': instance_id},
        "type": {'$in': list(types)}
    }

    return (item for item in get_database()['instance_filter'].find(header_query))
