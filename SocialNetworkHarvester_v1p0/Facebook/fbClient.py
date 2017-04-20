import io, types, time, requests, csv, re


class FBClient:
    baseURL = 'https://graph.facebook.com/v2.8/'

    def __init__(self, appToken):
        self.token = appToken

    def get(self, node, **kwargs):
        url = self.baseURL + node + '?access_token=' + self.token
        if 'fields' in kwargs:
            strFields = self.fieldify(kwargs['fields'])
            url += '&fields=' + strFields
            kwargs.pop('fields')
        for kwarg in kwargs.keys():
            url += '&%s=%s' % (kwarg, kwargs[kwarg])
        response = requests.get(url).json()
        self.lastRequestAt = time.time()
        if 'error' in response.keys():
            raise Exception(response['error'])
        return response

    def fieldify(self, jfields):
        s = ''
        for item in jfields:
            if isinstance(item, dict):
                for key in item.keys():
                    s += key
                    if isinstance(item[key], list):
                        s += '{' + self.fieldify(item[key]) + '}'
            else:
                s += item
            s += ','
        return s[:-1]

    def getNext(self, response):
        nextResponse = None
        if 'paging' in response and 'next' in response['paging']:
            url = response['paging']['next']
            nextResponse = requests.get(url)
            nextResponse = nextResponse.json()
        return nextResponse

    def removeEmojis(self, text, replacement=''):
        return self.antiEmojiRegex.sub(replacement, text)


    def collectWallPostsAndComments(self, id, since=None, until=None, keywords=[]):

        csvfile = open('Facebook - Equiterre - energie EST.csv', 'w')
        fields = ('id', 'type', 'parent', 'message', 'author_id', 'author_name', 'created_time')
        csvwriter = csv.writer(csvfile, lineterminator='\n')
        csvwriter.writerow(fields)
        response = self.get(id, fields=[
            {"posts.limit(50).since(%s).until(%s)" % (since, until): [
                {"comments.limit(100)": [
                    'message',
                    'id',
                    'from',
                    'created_time',
                ]},
                "message",
                "id",
                "from",
                'created_time',
            ],
            }
        ])
        response = response['posts']
        while response:
            if 'data' not in response: pretty(response)
            for post in response['data']:
                if not 'message' in post or not any([keyword in post['message'] for keyword in KEYWORDS]):
                    continue
                try:
                    pMessage = self.removeEmojis(post['message'], '[?]')
                    csvwriter.writerow(
                            [post['id'], 'status', 'None', pMessage, "_%s" % post['from']['id'], post['from']['name'],
                             post['created_time']])
                except:
                    pretty(post)
                    raise
                if 'comments' in post:
                    comments = post['comments']
                    while comments:
                        for comment in comments['data']:
                            try:
                                cMessage = self.removeEmojis(comment['message'], '[?]')
                                csvwriter.writerow([comment['id'], 'comment', post['id'], cMessage,
                                                    "_%s" % comment['from']['id'], comment['from']['name'],
                                                    comment['created_time']])
                            except:
                                pretty(comment)
                                pretty(cMessage)
                                raise
                        comments = self.getNext(comments)
            response = self.getNext(response)
