from tarfile import data_filter
from kivy.app import App

import requests


class MyFirebase():
    API_KEY = 'AIzaSyC1JHoCNvZD2fh4AaZ_rOJrEtlCE-MoDJg'

    def criar_conta(self, email, senha):
        link = f'https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.API_KEY}'
        info = {
            'email': email,
            'password': senha,
            'returnSecureToken': True
        }

        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()

        if requisicao.ok:
            print('Usuario Criado')

            refresh_token = requisicao_dic['refreshToken']
            id_token = requisicao_dic['idToken']
            local_id = requisicao_dic['localId']

            meu_aplicativo = App.get_running_app()
            meu_aplicativo.id_token = id_token
            meu_aplicativo.local_id = local_id

            with open("refreshtoken.txt", "w") as arquivo:
                arquivo.write(refresh_token)

            link_prox_id = f'https://aplicativosvendasaulahash-default-rtdb.firebaseio.com/prox_id_vendedor.json?auth={id_token}'
            req_id_vendedor = requests.get(link_prox_id)
            req_id_vendedor_dic = req_id_vendedor.json()
            id_vendedor = req_id_vendedor_dic['prox_id_vendedor']

            link = f'https://aplicativosvendasaulahash-default-rtdb.firebaseio.com/{local_id}.json?auth={id_token}'
            info = f'{{"avatar": "foto1.png","equipe": "", "total_vendas": "0", "vendas": "","id_vendedor": "{id_vendedor}"}}'
            requisicao = requests.patch(link, data=info)

            prox_id_vendedor = int(id_vendedor) + 1
            info_id_vendedor = f'{{"prox_id_vendedor": "{prox_id_vendedor}"}}'
            requests.patch(link_prox_id, data=info_id_vendedor)

            meu_aplicativo.carregar_infos_usuario()
            meu_aplicativo.mudar_tela('home_page')

        else:
            mensagem_erro = requisicao_dic['error']['message']
            meu_aplicativo = App.get_running_app()
            pagina_login = meu_aplicativo.root.ids['login_page']
            pagina_login.ids['mensagem_login'].text = mensagem_erro
            pagina_login.ids['mensagem_login'].color = (1, 0, 0, 1)

    def fazer_login(self, email, senha):
        link = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.API_KEY}'
        info = {"email": email, "password": senha, 'returnSecureToken': True}
        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()
        
        if requisicao.ok:
            refresh_token = requisicao_dic['refreshToken']
            id_token = requisicao_dic['idToken']
            local_id = requisicao_dic['localId']

            meu_aplicativo = App.get_running_app()
            meu_aplicativo.id_token = id_token
            meu_aplicativo.local_id = local_id

            with open("refreshtoken.txt", "w") as arquivo:
                arquivo.write(refresh_token)

            meu_aplicativo.carregar_infos_usuario()
            meu_aplicativo.mudar_tela('home_page')

        else:
            mensagem_erro = requisicao_dic['error']['message']
            meu_aplicativo = App.get_running_app()
            pagina_login = meu_aplicativo.root.ids['login_page']
            pagina_login.ids['mensagem_login'].text = mensagem_erro
            pagina_login.ids['mensagem_login'].color = (1, 0, 0, 1)

    def trocar_token(self, refresh_token):
        link = f'https://securetoken.googleapis.com/v1/token?key={self.API_KEY}'
        info = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()
        local_id = requisicao_dic['user_id']
        id_token = requisicao_dic['id_token']
        return local_id, id_token
    



        