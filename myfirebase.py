import requests
import json
from kivy.app import App


class MyFirebase():
    wak = "AIzaSyBUwNUyw4lN--2tzupP0ypeaspTkqL2zrA"  # Web Api Key

    def sign_up(self, email, password):
        app = App.get_running_app()
        # Firebase will return localId, authToken (idToken), refreshToken
        signup_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key=" + self.wak
        signup_payload = {"email": email, "password": password, "returnSecureToken": True}
        sign_up_request = requests.post(signup_url, data=signup_payload)
        print("sign_up check: ", sign_up_request.ok)
        sign_up_data = json.loads(sign_up_request.content.decode())

        if sign_up_request.ok == True:
            refresh_token = sign_up_data['refreshToken']
            localId = sign_up_data['localId']
            idToken = sign_up_data['idToken']
            # Save refreshToken to a file
            with open('refresh_token.txt', 'w') as f:
                f.write(refresh_token)
            # Save localID to a variable in main app class
            app.local_id = localId
            # Save idToken to a variable in main app class
            app.id_token = idToken

            # Create new key in db from localId
            #Default information - name, drill, location
            my_data = '{"Name": "", "Drill": "", "Loc": "", "Protocols": {"fnb": "","mup": "","olaf": ""},' \
                      '"PastOlaf": {"Previous BP": 0}}'
            post_request = requests.patch("https://protocol-app-hdd-default-rtdb.europe-west1.firebasedatabase.app/" + localId + '.json?auth=' + idToken, data=my_data)
            #print(post_request.ok)
            #print(post_request.content.decode())
            app.root.current = 'main'

        if sign_up_request.ok == False:
            error_data = json.loads(sign_up_request.content.decode())
            error_message = error_data['error']['message']
            app.root.ids['login_screen'].ids['login_message'].text = error_message


    def exchange_refresh_token(self, refresh_token):
        refresh_url = "https://securetoken.googleapis.com/v1/token?key=" + self.wak
        refresh_payload = '{"grant_type": "refresh_token", "refresh_token": "%s"}' % refresh_token
        refresh_req = requests.post(refresh_url, data=refresh_payload)
        #print("REFRESH OK", refresh_req.ok)
        #print(refresh_req.json())
        local_id = refresh_req.json()['user_id']
        id_token = refresh_req.json()['id_token']

        return id_token, local_id