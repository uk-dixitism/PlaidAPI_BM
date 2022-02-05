This project is made using Django REST Framework, PlaidAPI and celery

user -> This app makes API calls for User Register, Login, Logout. Token Authentication has been used.
plaid_api -> This app has been used for all the API calls and WebHooks. 

Resources used in making the project :
     - Youtube 
	  - Github Repositories
  	- Stackoverflow
	  - REST framework and PlaidAPI documentation

ERROR : (HELP REQUIRED) 
	
	- While trying to get accesstoken in exchange of public_key, getting response as " "detail": "CSRF Failed: CSRF token missing or incorrect."

Measures Taken to Solve the error:
	- Tried csrf_exempt for function based views, but didn't get the correct response.
  	- Used method_decorator with csrf_exempt, again it didn't work.
	- Searched on Github. Installed plaid-python. No luck.

Django rest Apis for signup, login and logout

	POST/api/register/ - Create user using username, email and password

	POST/api/login/ - Login using username and password

	GET/api/logout/ - Logout using token authentication

Fetch and store data from Plaid Apis

	POST/api/get_access_token/ - Exchange public token with access token

	POST/api/get_transactions/ - Get transactions from plaid api

	GET/api/identity/ - Get identity of the singed in user
  
  	GET/api/balance/ - Check the balance of the user
  
  	GET/api/item/ - Gives info about item
  
  	GET/api/accounts/ - Get the information about account
  
  	GET/api/webhook/ - Respond as "Webhook recieved" if success
