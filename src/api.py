import requests, json, hashlib, time, simplejson, urllib, base64
from src.util import write_directory, delete_file, relative_path, join_path
from definitions import CONFIGURATION_DIR, COOKIES_DIR, OUTPUT_REQUESTS_DIR, terminal
from src.terminal import Terminal

BASE_URL = 'https://graph.facebook.com'
BASE_ME = BASE_URL + '/me'
LOGIN_ENPOINT = 'https://api.facebook.com/restserver.php'

PATH_COOKIE_ACCESS_TOKEN = join_path(COOKIES_DIR, 'access_token.cookie.log')
PATH_CONFIGURATION_JSON = join_path(CONFIGURATION_DIR, 'api.json')

CONFIGURATION_JSON = json.load(open(PATH_CONFIGURATION_JSON))
API_SECRET = CONFIGURATION_JSON['api_secret']
API_KEY = CONFIGURATION_JSON['api_key']

BASE_DATA_LOGIN_REQUEST = {
	"api_key":"882a8490361da98702bf97a021ddc14d",
	"credentials_type":"password",
	"email":"",
	"format":"JSON",
	"generate_machine_id":"1",
	"generate_session_cookies":"1",
	"locale":"en_US",
	"method":"auth.login",
	"password":"",
	"return_ssl_resources":"0",
	"v":"1.0"
}
BASE_SIGNATURE = 'api_key={0}credentials_type=passwordemail={1}format=JSONgenerate_machine_id=1generate_session_cookies=1locale=en_USmethod=auth.loginpassword={2}return_ssl_resources=0v=1.0{3}'

class Request:
	@staticmethod
	def get(url):
		response = requests.get(url)
		text = response.text
		file_name = join_path(OUTPUT_REQUESTS_DIR, 'get_request[%s].json' % time.time())
		fr = open(file_name, 'w')
		fr.write('{0}'.format(text))
		fr.close()
		try:
			json_response = simplejson.loads(text, encoding='utf-8')
			return json_response
		except simplejson.errors.JSONDecodeError as ex:
			terminal.write(str(ex))
			return None
class Facebook:
	def login(self):
		terminal.set_message_type(Terminal.MessageType.LOG)
		terminal.write('[*] login to your facebook account         ')
		self.id = terminal.read(message = '[?] Username | Email | Phone : ')
		self.pwd = terminal.read(message = '[?] Password : ', hide_input = True)
		self.data = BASE_DATA_LOGIN_REQUEST
		self.data['email'] = self.id
		self.data['password'] = self.pwd
		sig = BASE_SIGNATURE.format(API_KEY, self.id, self.pwd, API_SECRET)
		md5_hash = hashlib.new('md5')
		md5_hash.update(sig)
		self.data.update({'sig': md5_hash.hexdigest()})

	def write_access_token(self):
		terminal.write('[*] Generate access token ')
		b = open(PATH_COOKIE_ACCESS_TOKEN,'w')
		try:
			response = requests.get(LOGIN_ENPOINT,params=self.data)
			json_response = json.loads(response.text)

			b.write(json_response['access_token'])
			b.close()
			terminal.set_message_type(Terminal.MessageType.SUCCESS)
			terminal.write('[*] Successfully generate access token')
			terminal.set_message_type(Terminal.MessageType.LOG)
			terminal.write('[*] Your access token is stored in ' + relative_path(PATH_COOKIE_ACCESS_TOKEN))
			# success
		except KeyError:
			terminal.set_message_type(Terminal.MessageType.ERROR)
			terminal.write('[!] Failed to generate access token')
			terminal.write('[!] Check your connection / email or password')
			b.close()
			delete_file(PATH_COOKIE_ACCESS_TOKEN)
			# failed
		except requests.exceptions.ConnectionError:
			terminal.set_message_type(Terminal.MessageType.ERROR)
			terminal.write('[!] Failed to generate access token')
			terminal.write('[!] Connection error !!!')
			b.close()
			delete_file(PATH_COOKIE_ACCESS_TOKEN)

	def access_token(self):
		return open(PATH_COOKIE_ACCESS_TOKEN, 'r').read()
	
	def get_friends(self):
		url = '%s/friends?access_token=%s' % (BASE_ME, self.access_token())
		json_response = Request.get(url)
		friends = json_response['data']
		return friends
	
	def get_profile_data(self, profile_id):
		url = '%s/%s?access_token=%s' % (BASE_URL, profile_id, self.access_token())
		profile = Request.get(url)
		return profile['data']
	
	def get_profile_of(self, profile_id):
		url = '%s/%s/friends?access_token=%s' % (BASE_URL, profile_id, self.access_token())
		profile = Request.get(url)
		return profile['data']
	
	def get_profile_picture(self, profile_id):
		url = '%s/%s/picture?access_token=%s&height=300' % (BASE_URL, profile_id, self.access_token())
		contents = urllib.urlopen(url).read()
		picture = base64.b64encode(contents)
		return picture
		
	