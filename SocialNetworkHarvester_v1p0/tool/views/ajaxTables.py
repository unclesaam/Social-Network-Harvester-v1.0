from django.shortcuts import *
from django.http import StreamingHttpResponse
from datetime import datetime
from django.contrib.auth.decorators import login_required
import re, json
from django.db.models.query import QuerySet
from SocialNetworkHarvester_v1p0.jsonResponses import *
from AspiraUser.models import getUserSelection, resetUserSelection, UserProfile
from Twitter.models import TWUser, Tweet, Hashtag, follower, HashtagHarvester, favorite_tweet, follower
from Facebook.models import FBPost, FBPage,FBComment,FBReaction,FBUser
from Youtube.models import YTChannel, YTVideo
from functools import reduce

from SocialNetworkHarvester_v1p0.settings import viewsLogger, DEBUG

log = lambda s: viewsLogger.log(s) if DEBUG else 0
pretty = lambda s: viewsLogger.pretty(s) if DEBUG else 0
logerror = lambda s: viewsLogger.exception(s) if DEBUG else 0

MODEL_WHITELIST = ['FBPage', 'FBPost','FBComment','FBReaction',
                   'Tweet','TWUser',"HashtagHarvester","Hashtag","favorite_tweet","follower",
                   'YTChannel','YTVideo']

@login_required()
def ajaxBase(request):
    try:
        if not request.user.is_authenticated(): return jsonUnauthorizedError()
        if not 'tableId' in request.GET: return missingParam('tableId')
        if not 'modelName' in request.GET: return missingParam('modelName')
        if not 'srcs' in request.GET: return missingParam('srcs')
        tableId = request.GET['tableId']
        modelName = request.GET['modelName']
        if modelName not in MODEL_WHITELIST: return jsonForbiddenError()
        queryset = getQueryset(request)
        userSelection = getUserSelection(request)
        selecteds = userSelection.getSavedQueryset(modelName, tableId).distinct()
        if 'download' in request.GET and request.GET['download'] == 'true':
            if request.GET['fileType'] == 'csv':
                return generateCSVDownload(request, selecteds, userSelection)
            elif request.GET['fileType'] == 'json':
                return generateJSONDownload(request, selecteds, userSelection)
        else:
            response = generateAjaxTableResponse(queryset, request, selecteds)
            return HttpResponse(json.dumps(response), content_type='application/json')
    except:
        logerror("Exception occured in tool/views/ajaxTables:ajaxBase")
        return jsonUnknownError()


def getQueryset(request):
    updateQueryOptions(request)
    modelName = request.GET['modelName']
    queryset = globals()[modelName].objects.none()
    srcs = request.GET['srcs']
    userSelection = getUserSelection(request)
    for src in json.loads(srcs):
        srcModel = request.user.userProfile
        attrs = src['attr'].split('__')
        if 'modelName' in src:
            srcModelName = src['modelName']
            if "tableId" in src:
                selectedSrcs = userSelection.getSavedQueryset(srcModelName, src["tableId"])
                for selected in selectedSrcs:
                    queryset = queryset | reduce(getattr, attrs, selected).all()
            else:
                srcModel = get_object_or_404(globals()[srcModelName], pk=src['id'])
                queryset = queryset | reduce(getattr, attrs, srcModel).all()
        else:
            queryset = queryset | reduce(getattr, attrs, srcModel).all()
    options = userSelection.getQueryOptions(request.GET['tableId'])
    if "exclude_retweets" in options.keys() and options['exclude_retweets']:
        queryset = queryset.filter(retweet_of__isnull=True)
    if 'search_term' in options.keys():
        queryset = filterQuerySet(queryset, options['search_fields'].split(','), options['search_term'])
    if 'ord_field' in options.keys():
        queryset = orderQueryset(queryset, options['ord_field'], options['ord_direction'])
    return queryset


def updateQueryOptions(request):
    params = request.GET
    userSelection = getUserSelection(request)
    selecteds = userSelection.getSavedQueryset(params['modelName'], params['tableId'])
    if 'fields' in params:
        fields = params['fields'].split(',')
        if "iSortCol_0" in params:
            ordering_column = int(params['iSortCol_0']) - 1
            if ordering_column >= 0:
                userSelection.setQueryOption(request.GET['tableId'], "ord_field", fields[ordering_column])
                userSelection.setQueryOption(request.GET['tableId'], "ord_direction", params['sSortDir_0'])
                if selecteds.count():
                    selecteds = orderQueryset(selecteds, fields[ordering_column], params['sSortDir_0'])
                    userSelection.saveQuerySet(selecteds, params['tableId'])

        if 'sSearch' in params: # and params['sSearch'] != '':
            searchables_keys = [value for key, value in sorted(params.items()) if key.startswith("bSearchable_")][1:]
            search_fields = [pair[0] for pair in zip(fields, searchables_keys) if pair[1] == 'true']
            userSelection.setQueryOption(request.GET['tableId'], 'search_fields', ",".join(search_fields))
            userSelection.setQueryOption(request.GET['tableId'], "search_term", params['sSearch'])



def generateAjaxTableResponse(queryset, request, selecteds):
    params = request.GET
    queryset = queryset.distinct() | selecteds.distinct()
    queryset = queryset.distinct()
    response = {
        "recordsTotal": queryset.count(),
        "recordsFiltered": queryset.count(),
        'fullURL': request.get_full_path(),
    }
    fields = []
    if 'fields' in params:
        fields = params['fields'].split(',')
        if "iDisplayStart" in params and "iDisplayLength" in params:
            start = int(params['iDisplayStart'])
            length = int(params['iDisplayLength'])
            queryset = queryset[start:start + length]

    response["data"] = [getValuesAsJson(item, fields) for item in queryset.iterator()]
    response['selecteds'] = [item.get_obj_ident() for item in queryset if item in selecteds]
    response['selectedCount'] = selecteds.count()
    return response


def orderQueryset(queryset, field, order):
    #log("ordering by: %s (%s)"%(field,order))
    orderingBy = field
    if order == 'desc':
        orderingBy = '-' + orderingBy
    ret = queryset.order_by(orderingBy)#.exclude(**{field + "__isnull": True})
    #try:
    #    ret = ret.exclude(**{field: ""})
    #except:
    #   pass
    return ret


def filterQuerySet(queryset, fields, term):
    filteredQueryset = queryset.filter(id=-1)
    for field in fields:
        subFields = field.split('__')
        #type = queryset.model._meta.get_field(subFields[0])
        #if len(subFields) > 1:
        #    type = type.rel.to
        #    for subfield in subFields[1:]:
        #        type = type._meta.get_field(subfield)
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
    tableId = request.GET['tableId']
    userSelection.setQueryOption(tableId, 'downloadProgress', 0)
    userSelection.setQueryOption(tableId, 'linesTransfered', 0)
    def dataStream():
        sent = 0
        lastPercent = 0
        count = queryset.count()
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
        #log('completed download')
        userSelection.setQueryOption(tableId, 'downloadProgress', 100)
        userSelection.setQueryOption(tableId, 'linesTransfered', 1)
    try:
        response = StreamingHttpResponse(dataStream(), content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=%s" % request.GET['filename'] + '.csv'
        return response
    except:
        logerror("Error occured in generateCSVDownload")


# @viewsLogger.debug(showArgs=True)
def generateJSONDownload(request, selecteds, userSelection):
    return HttpResponse('Work in progess')


@viewsLogger.debug(showArgs=True)
def readLinesFromCSV(request):
    file = request.FILES['Browse']
    rows = []
    errors = []
    i = 0
    for row in file:
        i += 1
        try:
            decodedRow = row.decode('utf8')
            decodedRow = re.sub('[\\r\\n]', '', decodedRow)
            rows.append(decodedRow)
        except UnicodeDecodeError:
            errors.append("Invalid statement on line %i of the file"%i)
    return [row for row in rows if row != ""], errors




######### TABLE ROWS SELECTION MANAGEMENT ##########

@login_required()
def setUserSelection(request):
    response = {}
    try:
        selection = getUserSelection(request)
        tableId = request.GET['tableId']
        if ('selected' in request.GET and request.GET['selected'] == '_all') or \
                ('unselected' in request.GET and request.GET['unselected'] == '_all'):
            selectUnselectAll(request)
        else:
            if 'selected' in request.GET:
                queryset = getItemQueryset(request.GET['selected'])
                selection.selectRow(tableId, queryset)
            elif 'unselected' in request.GET:
                queryset = getItemQueryset(request.GET['unselected'])
                selection.unselectRow(tableId, queryset)

        options = [(name[4:], request.GET[name]) for name in request.GET.keys() if 'opt_' in name]
        for option in options:
            selection.setQueryOption(tableId, option[0], option[1])
        response['selectedCount'] = selection.getSelectedRowCount()
        response['status'] = 'completed'
    except:
        viewsLogger.exception("AN ERROR OCCURED IN setUserSelection")
        response = {'status': 'error', 'error': {'description': 'An error occured in views'}}
    return HttpResponse(json.dumps(response), content_type='application/json')


def getItemFromRowId(rowId):
    className, itemPk = rowId.split('_')
    type = globals()[className]
    return get_object_or_404(type, pk=itemPk)


def getItemQueryset(rowId):
    className, itemPk = rowId.split('__')
    return globals()[className].objects.filter(pk=itemPk)


# @viewsLogger.debug(showArgs=True)
def selectUnselectAll(request):
    if not 'modelName' in request.GET: return missingParam('modelName')
    modelName = request.GET['modelName']
    if modelName not in MODEL_WHITELIST: return jsonForbiddenError()
    queryset = globals()[request.GET['modelName']].objects.none()
    if 'selected' in request.GET:
        queryset = getQueryset(request)
    getUserSelection(request).saveQuerySet(queryset, request.GET['tableId'])

