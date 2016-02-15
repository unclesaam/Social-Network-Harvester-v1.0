from .commonThread import *

class TwFriendshipUpdater(CommonThread):

    userLookupBatchSize = 200

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.twUserList = kwargs['twUser']

    @twitterLogger.debug()
    def execute(self):
        newTwUsers = []
        allFriendsIds = []
        log('twUser: %s'%self.twUser)
        cursor = tweepy.Cursor(self.client.friends_ids, screen_name=self.twUser.screen_name).items()
        twid = True
        while twid:
            twid = self.getNextFromCursor(cursor)
            allFriendsIds.append(twid)
            twFriend, new = TWUser.objects.get_or_create(_ident=twid)
            if new:
                newTwUsers.append(twFriend)
            if not self.twUser.friends.filter(value=twFriend, ended__isnull=True).exists():
                friendship = friend.objects.create(value=twFriend, twuser=self.twUser)
                self.twUser.friends.add(friendship)
                self.twUser.save()
            page = self.getNextFromCursor(cursor)

        self.endOldFriendships(allFriendsIds)

        twUserUpdater = twUserListUpdater(client, newTwUsers)
        twUserUpdater.launchUpdate()

    @twitterLogger.debug()
    def endOldFriendships(self, allFriendsIds):
        for friendship in self.twUser.friends.filter(ended__isnull=True):
            if friendship.value._ident not in allFriendsIds:
                friendship.ended = today()
                friendship.save()
