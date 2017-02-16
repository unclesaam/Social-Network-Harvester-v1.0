from django.shortcuts import *
from django.http import StreamingHttpResponse
from Twitter.models import TWUser, Tweet, Hashtag, follower, HashtagHarvester
from datetime import datetime
from django.contrib.auth.decorators import login_required
from AspiraUser.models import getUserSelection, resetUserSelection
import re, json
from django.db.models.query import QuerySet

from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG
log = lambda s: viewsLogger.log(s) if DEBUG else 0
pretty = lambda s: viewsLogger.pretty(s) if DEBUG else 0


#@viewsLogger.debug(showArgs=True)
def ajaxResponse(queryset, request, selecteds):
    selecteds = selecteds.distinct()
    if 'download' in request.GET and request.GET['download'] == 'true':
        userSelection = getUserSelection(request)
        if request.GET['fileType'] == 'csv':
            return generateCSVDownload(request, selecteds, userSelection)
        elif request.GET['fileType'] == 'json':
            return generateJSONDownload(request, selecteds, userSelection)
    else:
        response = generateAjaxTableResponse(queryset, request, selecteds)
        return HttpResponse(json.dumps(response), content_type='application/json')


def generateAjaxTableResponse(queryset, request, selecteds):
    params = request.GET
    response = {
        "recordsTotal": queryset.count(),
        "recordsFiltered": queryset.count(),
        'fullURL': request.get_full_path(),
    }
    fields = []
    if 'fields' in params:
        fields = params['fields'].split(',')
        if "iSortCol_0" in params:
            ordering_column = int(params['iSortCol_0']) - 1
            if ordering_column >= 0:
                queryset = orderQuerySet(queryset, fields[ordering_column], params['sSortDir_0'])

        if 'sSearch' in params and params['sSearch'] != '':
            searchables_keys = [value for key, value in sorted(params.items()) if key.startswith("bSearchable_")][1:]
            searchable_fields = [pair[0] for pair in zip(fields, searchables_keys) if pair[1] == 'true']
            queryset = filterQuerySet(queryset, searchable_fields, params['sSearch'])
            response['recordsFiltered'] = queryset.count()

        if "iDisplayStart" in params and "iDisplayLength" in params:
            start = int(params['iDisplayStart'])
            length = int(params['iDisplayLength'])
            queryset = queryset[start:start + length]

    response["data"] = [getValuesAsJson(item, fields) for item in queryset.iterator()]
    response['selecteds'] = [item.get_obj_ident() for item in queryset if item in selecteds]
    response['selectedCount'] = selecteds.count()
    return response


def orderQuerySet(queryset, field, order):
    orderingBy = field
    if order == 'desc':
        orderingBy = '-' + orderingBy
    ret = queryset.order_by(orderingBy).exclude(**{field + "__isnull": True})
    try:
        ret = ret.exclude(**{field: ""})
    except:
        pass
    return ret


def filterQuerySet(queryset, fields, term):
    filteredQueryset = queryset.filter(id=-1)
    for field in fields:
        subFields = field.split('__')
        type = queryset.model._meta.get_field(subFields[0])
        if len(subFields) > 1:
            type = type.rel.to
            for subfield in subFields[1:]:
                type = type._meta.get_field(subfield)
        if type == Tweet.user.field:
            filteredQueryset = filteredQueryset | queryset.filter(**{field + "__screen_name__contains": '%s' % term})
            filteredQueryset = filteredQueryset | queryset.filter(**{field + "__name__contains": '%s' % term})
        else:
            filteredQueryset = filteredQueryset | queryset.filter(**{field + "__icontains": '%s' % term})
    return filteredQueryset


def getValuesAsJson(obj, attrs):
    l = {}
    for attr in attrs:
        if attr == '': break
        subAttrs = attr.split('__')
        value = getattr(obj, subAttrs[0])
        if hasattr(value, 'all'):
            value = value.all()
        elif callable(value):
            value = value()
        # log("%s: %s"%(subAttrs[0], value))
        if len(subAttrs) > 1:
            for subAttr in subAttrs[1:]:
                if not value:
                    value = ''
                    break
                value = getattr(value, subAttr)
                if hasattr(value, 'all'):
                    value = value.all()
                elif callable(value):
                    value = value()
                    # log("%s: %s"%(subAttr, value))
        if isinstance(value, TWUser):
            value = value.screen_name
        if isinstance(value, datetime):
            # value = datetime.strftime(value, '%b %d %Y %H:%M')
            value = datetime.strftime(value, '%b %d %Y')
        if isinstance(value, QuerySet):
            value = [str(obj) for obj in value]
        if '_ident' in attr:
            l[attr] = "_%s" % value
        else:
            l[attr] = value
    l['DT_RowId'] = obj.get_obj_ident()
    return l


# @viewsLogger.debug(showArgs=True)
def getValuesAsList(obj, fields):
    json = getValuesAsJson(obj, fields)
    ret = []
    for field in fields:
        ret.append(json[field])
    return ret


#@viewsLogger.debug(showArgs=True)
def getColumnsDescriptions(model, fields, infoType):
    columns = []
    fieldsDescription = model.get_fields_description()
    #pretty(fieldsDescription)
    for field in fields:
        if '__' not in field:
            columns.append("%s"%fieldsDescription[field][infoType])
        else:
            subfields = field.split('__')
            submodel = getattr(model, subfields[0])
            for subfield in subfields[1:-1]:
                submodel = getattr(submodel, subfield)
            fieldsDescription = submodel.get_fields_description()
            columns.append("%s"%fieldsDescription[subfields[-1]][infoType])
    return columns


################### TABLE STREAMS ###################
import io, csv, types, binascii, codecs


#@viewsLogger.debug(showArgs=True)
def generateCSVDownload(request, queryset, userSelection):
    def dataStream():
        sent = 0
        lastPercent = 0
        count = queryset.count()
        tableId = request.GET['tableId']
        csvfile = io.StringIO()
        csvfile.write('\uFEFF')
        csvwriter = csv.writer(csvfile)
        fields = request.GET['fields'].split(',')
        model = queryset.model
        temp = queryset.model.objects.all()[0]
        csvwriter.writerow(getColumnsDescriptions(temp, fields, 'name'))
        csvwriter.writerow(getColumnsDescriptions(temp, fields, 'description'))
        if count <= 0:
            csvfile.seek(0)
            yield csvfile.read()
            userSelection.setQueryOption()
        itterCount = 0
        for obj in queryset.iterator():
            percent = (int)(sent * 100 / count)
            itterCount += 1
            if percent > lastPercent or itterCount > 100:
                itterCount = 0
                lastPercent = percent
                userSelection.setQueryOption(tableId, 'downloadProgress', percent)
                userSelection.setQueryOption(tableId, 'linesTransfered', sent)
                #log("sent: %s lines. (%i %%)"%(sent, percent))
            csvwriter.writerow(getValuesAsList(obj, fields))
            csvfile.seek(0)
            data = csvfile.read()
            csvfile.seek(0)
            csvfile.truncate()
            sent += 1
            try:
                yield data
            except:
                logerror("Error occured in generateCSVDownload")
        log('completed download')
        userSelection.setQueryOption(tableId, 'downloadProgress', 100)
    try:
        response = StreamingHttpResponse(dataStream(), content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=%s" % request.GET['filename'] + '.csv'
        return response
    except:
        logerror("Error occured in generateCSVDownload")


# @viewsLogger.debug(showArgs=True)
def generateJSONDownload(request, selecteds, userSelection):
    return HttpResponse('Work in progess')
