from django.db import models

# Create your models here.

class AccessToken(models.Model):

    class Meta:
        app_label = "Facebook"

    _token = models.CharField(max_length=255)






def setFBToken(newToken):
    token = None
    if AccessToken.objects.count() > 1 :
        raise Exception('More than one AccessToken exists!')
    elif AccessToken.objects.count() > 0:
        token = AccessToken.objects.all()[0]
    if not token:
        token = AccessToken.objects.create()
    token._token = newToken
    token.save()



def getFBToken():
    token = None
    if AccessToken.objects.count() > 1:
        raise Exception('More than one AccessToken exists!')
    elif AccessToken.objects.count() > 0:
        token = AccessToken.objects.all()[0]
    return token._token


class FBUser(models.Model):
	id = models.CharField(max_length=225)
	about = models.TextField(null=True)
	age_range = models.CharField(max_length=100, null=True)
	bio = models.TextField(null=True)
	birthday = models.DateTimeField(null=True)
	cover = models.CharField(max_length = 500, null=True)
	currency = models.CharField(max_length=225, null=True)
	devices = models.CharField(max_length=225, null=True)
	education = models.CharField(max_length=225, null=True)
	email = models.CharField(max_length=225, null=True)
	favorite_athletes = models.TextField(null=True)
	favorite_teams = models.TextField(null=True)
	first_name = models.CharField(max_length=100, null=True)
	gender = models.CharField(max_length=50, null=True)
	hometown = models.CharField(max_length=225, null=True)
	inspirational_people = models.TextField(null=True)
	interested_in = models.TextField(null=True)
	is_verified = models.BooleanField(default=False)
	languages = models.CharField(max_length=225, null=True)
	last_name = models.CharField(max_length=100, null=True)
	link = models.CharField(max_length=225, null=True)
	location = models.CharField(max_length=225, null=True)
	meeting_for = models.TextField(null=True)
	middle_name = models.CharField(max_length=100, null=True)
	name = models.CharField(max_length=300, null=True)
	name_format = models.CharField(max_length=225, null=True)
	political = models.CharField(max_length=225, null=True)
	public_key =  models.CharField(max_length=500, null=True)
	quotes = models.TextField(null=True)
	relationship_status = models.CharField(max_length=225, null=True)
	religion = models.CharField(max_length=225, null=True)
	significant_other = models.CharField(max_length=225, null=True)
	sports = models.TextField(null=True)
	timezone = models.IntegerField(null=True)
	updated_time = models.DateTimeField(null=True)
	website = models.CharField(max_length=500, null=True)
	work = models.TextField(null=True)



	def get_fields_description(self):
        return {
            "id": {
                "description": "Identifier of a person's account.",
                "name": "Identifier"},
            "about": {
            	"description": "The About Me section of this person's profile.",
            	"name": "About Me"},
            "age_range": {
            	"description": "The age segment for this person.",
            	"name": "Age Range"},
            "bio": {
            	"description": "This person's biographie.",
            	"name": "Biographie"},
            "birthday": {
            	"description": "The person's birthday.",
            	"name": "Birthday"},
            "cover": {
            	"description": "The person's cover photo.",
            	"name": "Cover Photo"},
            "currency": {
            	"description": "The person's local currency information.",
            	"name": "Currency"},
            "devices" : {
            	"description": "List of used devices by the person.",
            	"name" : "Devices"},
            "education" : {
            	"description": "List of the person's education experiences.",
            	"name" : "Education"},
            "email" : {
            	"description": "Email to contact the person.",
            	"name" : "Email"},
            "favorite_athletes" : {
            	"description": "Person's favorite athletes.",
            	"name" : "Favorite Athletes"},
            "favorite_teams" : {
            	"description": "Person's favorite teams.",
            	"name" : "Favorite Teams"},
            "first_name" : {
            	"description": "Person's first name.",
            	"name" : "First Name"},
            "gender" : {
            	"description": "Person's gender.",
            	"name" : "Gender"},
            "hometown" : {
            	"description": "Person's hometown.",
            	"name" : "Hometown"},
            "inspirational_people" : {
            	"description": "Person's inspirational people.",
            	"name" : "Inspirational People"},
            "interested_in" : {
            	"description": "Person's interests.",
            	"name" : "Interests"},
            "is_verified" : {
            	"description": "Person has been manually verified by Facebook.",
            	"name" : "Is Verified"},
            "languages" : {
            	"description": "Person's known languages.",
            	"name" : "Languages"},
            "last_name" : {
            	"description": "Person's last name.",
            	"name" : "Last Name"},
            "link" : {
            	"description": "Link to person's Timeline.",
            	"name" : "Timeline"},
            "location" : {
            	"description": "Person's current location as entered by them.",
            	"name" : "Location"},
            "meeting_for" : {
            	"description": "What the person is interested in meeting for.",
            	"name" : "Meeting For"},
            "middle_name" : {
            	"description": "Person's middle name.",
            	"name" : "Middle Name"},
            "name" : {
            	"description": "Person's name.",
            	"name" : "Name"},
            "name_format" : {
            	"description": "Person's name format.",
            	"name" : "Name Format"},
            "political" : {
            	"description": "Person's political views.",
            	"name" : "Political Views"},
            "public_key" : {
            	"description": "Person's PGP public key.",
            	"name" : "Public Key"},
            "quotes" : {
            	"description": "Person's favorite quotes.",
            	"name" : "Favorite Quotes"},
            "relationship_status" : {
            	"description": "Person's relationship status.",
            	"name" : "Relationship Status"},
            "religion" : {
            	"description": "Person's religion.",
            	"name" : "Religion"},
            "significant_other" : {
            	"description": "Person's significant other.",
            	"name" : "Significant Other"},
            "sports" : {
            	"description": "Sports played by the person.",
            	"name" : "Sports"},
            "timezone" : {
            	"description": "Person's current timezone offset from UTC.",
            	"name" : "Timezone"},
            "updated_time" : {
            	"description": "Updated time.",
            	"name" : "Updated Time"},
            "website" : {
            	"description": "Person's website.",
            	"name" : "Website"},
            "work" : {
            	"description": "Details of a person's work experience.",
            	"name" : "Work"}
            }


class FBAgeRange(models.Model)