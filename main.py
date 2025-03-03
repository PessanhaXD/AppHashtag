from turtle import onrelease
from kivy.app import App
from kivy.lang import Builder
from banner_venda import BannerVenda
from banner_vendedores import BannerVendedores
from myfirebase import MyFirebase
from telas import *
from botoes import *
from functools import partial
from datetime import date
import requests
import certifi
import os

os.environ["SSL_CERT_FILE"] = certifi.where()

GUI = Builder.load_file("main.kv")
class MainApp(App):
    cliente = None
    produto = None
    unidade = None

    def build(self):
        self.firebase = MyFirebase()
        return GUI

    def on_start(self):
        # carregar as fotos de perfil
        arquivos = os.listdir('icones/fotos_perfil')
        pagina_fotos_perfil_page = self.root.ids['foto_perfil_page']
        lista_fotos = pagina_fotos_perfil_page.ids["lista_fotos_perfil"]
        for foto in arquivos:
            imagem = ImageButton(source = f'icones/fotos_perfil/{foto}', on_release = partial(self.mudar_foto_perfil, foto))
            lista_fotos.add_widget(imagem)
        
        # carregar fotos clientes
        arquivos = os.listdir('icones/fotos_clientes')
        pagina_adicionar_vendas = self.root.ids['adicionar_vendas_page']
        lista_vendas = pagina_adicionar_vendas.ids["lista_clientes"]
        for foto_cliente in arquivos:
            imagem = ImageButton(source = f'icones/fotos_clientes/{foto_cliente}', 
                                on_release=partial(self.selecionar_cliente, foto_cliente))
            label = LabelButton(text=foto_cliente.replace(".png","").capitalize(),
                                on_release=partial(self.selecionar_cliente, foto_cliente) )
            lista_vendas.add_widget(imagem)
            lista_vendas.add_widget(label)

        # carregar fotos produtos
        arquivos = os.listdir('icones/fotos_produtos')
        lista_produtos = pagina_adicionar_vendas.ids["lista_produtos"]
        for produto in arquivos:
            imagem = ImageButton(source = f'icones/fotos_produtos/{produto}', 
                                on_release=partial(self.selecionar_produto, produto))
            label = LabelButton(text=produto.replace(".png","").capitalize(),
                                on_release=partial(self.selecionar_produto, produto))
            lista_produtos.add_widget(imagem)
            lista_produtos.add_widget(label)

        pagina_adicionar_vendas = self.root.ids['adicionar_vendas_page']
        data = pagina_adicionar_vendas.ids['id_data']

        data.text = f'Data: {date.today().strftime('%d/%m/%Y')}'

        self.carregar_infos_usuario()

    def carregar_infos_usuario(self):
        try:
            with open ("refreshtoken.txt", "r") as arquivo:
                refresh_token = arquivo.read()
            local_id, id_token = self.firebase.trocar_token(refresh_token)
            self.local_id = local_id
            self.id_token = id_token
    
            # pegar informações do usuario
            requisicao = requests.get(f'https://aplicativosvendasaulahash-default-rtdb.firebaseio.com/{self.local_id}/.json?auth={self.id_token}')
            requisicao_dic = requisicao.json()
            # alterar a foto de perfil com a informação pegada anteriormente
            avatar = requisicao_dic['avatar']
            self.avatar = avatar
            foto_perfil = self.root.ids['foto_perfil']
            foto_perfil.source = f'icones/fotos_perfil/{avatar}'

            id_vendedor = requisicao_dic['id_vendedor']
            pag_ajustes = self.root.ids['ajustes_page']
            pag_ajustes.ids['id_vendedor'].text = f'Seu ID Único: {id_vendedor}'

            total_vendas = float(requisicao_dic['total_vendas'])
            home_page = self.root.ids['home_page']
            home_page.ids['label_total_vendas'].text = f'[color=#000000]Total de vendas:[/color] [b]R${total_vendas :,.2f}[/b]'

            # preencher equipe
            self.equipe = requisicao_dic['equipe']

            try:
                vendas = requisicao_dic['vendas']
                pagina_home_page = self.root.ids["home_page"]
                lista_vendas = pagina_home_page.ids["lista_vendas"] 
                for id_venda in vendas:
                    venda = vendas[id_venda]
                    banner = BannerVenda(cliente=venda['cliente'], foto_cliente=venda['foto_cliente'],
                                        produto=venda['produto'], foto_produto=venda['foto_produto'],
                                        preco=venda['preco'], quantidade=venda['quantidade'],
                                        unidade=venda['unidade'], data=venda['data']
                                        )
                    lista_vendas.add_widget(banner)
            except:
                pass

            equipe = requisicao_dic['equipe']
            lista_equipe = equipe.split(',')
            pag_lista_vendedores = self.root.ids['listar_vendedores_page']
            lista_vendedores = pag_lista_vendedores.ids['lista_vendedores']
            self.lista_vendedores = lista_vendedores

            for id_vendedor_equipe in lista_equipe:
                if id_vendedor_equipe != "":
                    banner_vendedor = BannerVendedores(id_vendedor=id_vendedor_equipe)
                    self.lista_vendedores.add_widget(banner_vendedor)

            self.mudar_tela('home_page')

        except:
            pass

    def mudar_tela(self, id_tela):
        gerenciador_telas = self.root.ids['screen_manager']
        gerenciador_telas.current = id_tela

    def mudar_foto_perfil(self, foto, *args):
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = f'icones/fotos_perfil/{foto}'
        info_foto_json = f'{{"avatar": "{foto}"}}'
        requests.patch(f'https://aplicativosvendasaulahash-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}',
                        data = info_foto_json)
        self.mudar_tela('ajustes_page')

    def adicionar_vendedor(self, id_vendedor_adicionado):
        link = f'https://aplicativosvendasaulahash-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"&equalTo="{id_vendedor_adicionado}"'
        requisicao = requests.get(link)
        requisicao_dic = requisicao.json()
        pag_acompanhar_vendedor = self.root.ids['acompanhar_vendedor_page']
        mensagem_texto = pag_acompanhar_vendedor.ids['mensagem_vendedor']

        if requisicao_dic == {}:
            mensagem_texto.text = '[color=#FF0000]Usuário não encontrado![/color]'
        else:
            equipe = self.equipe.split(',')
            if id_vendedor_adicionado in equipe:
                mensagem_texto.text = '[color=#FF0000]Vendedor já faz parte da equipe![/color]'
            else:
                self.equipe = self.equipe + f',{id_vendedor_adicionado}'
                self.equipe = self.equipe.lstrip(',')

                self.equipe = sorted(list(map(int, self.equipe.split(','))))
                self.equipe = ",".join(map(str, self.equipe))


                info = f'{{"equipe": "{self.equipe}"}}'
                requests.patch(f'https://aplicativosvendasaulahash-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}',
                                data=info)
                mensagem_texto.text = 'Vendedor adicionado com sucesso!'

                # adicionar um novo banner na lista vendedores
                self.lista_vendedores.clear_widgets()
                
                requisicao = requests.get(f'https://aplicativosvendasaulahash-default-rtdb.firebaseio.com/{self.local_id}/.json?auth={self.id_token}')
                requisicao_dic = requisicao.json()

                equipe = requisicao_dic['equipe']
                lista_equipe = equipe.split(',')
                pag_lista_vendedores = self.root.ids['listar_vendedores_page']
                lista_vendedores = pag_lista_vendedores.ids['lista_vendedores']
                self.lista_vendedores = lista_vendedores

                for id_vendedor_equipe in lista_equipe:
                    if id_vendedor_equipe != "":
                        banner_vendedor = BannerVendedores(id_vendedor=id_vendedor_equipe)
                        self.lista_vendedores.add_widget(banner_vendedor)

        pag_acompanhar_vendedor.ids['id_outro_vendedor'].text = ''
    
    def selecionar_cliente(self, foto, *args):
        self.cliente = foto.replace('.png','')
        pag_adicionar_vendas = self.root.ids['adicionar_vendas_page']
        lista_cliente = pag_adicionar_vendas.ids['lista_clientes']

        for item in list(lista_cliente.children):
            item.color = (1, 1, 1, 1)

            try:
                texto = item.text 
                texto = texto.lower() + ".png"
                if foto == texto:
                    item.color = (0, 207/255, 219/255)
                    pag_adicionar_vendas.ids['id_selecione_cliente'].color = (1, 1, 1)
            except:
                pass


    def selecionar_produto(self, foto, *args):
        self.produto = foto.replace('.png','')
        pag_adicionar_vendas = self.root.ids['adicionar_vendas_page']
        lista_produtos = pag_adicionar_vendas.ids['lista_produtos']

        for item in list(lista_produtos.children):
            item.color = (1, 1, 1, 1)

            try:
                texto = item.text 
                texto = texto.lower() + ".png"
                if foto == texto:
                    item.color = (0, 207/255, 219/255)
                    pag_adicionar_vendas.ids['id_selecione_produto'].color = (1, 1, 1)
            except:
                pass

    def selecionar_unidade(self, id_label, *args):
        self.unidade = id_label.replace("id_","")

        pag_adicionar_vendas = self.root.ids['adicionar_vendas_page']
        
        pag_adicionar_vendas.ids['id_kg'].color = (1, 1, 1)
        pag_adicionar_vendas.ids['id_unidades'].color = (1, 1, 1)
        pag_adicionar_vendas.ids['id_litros'].color = (1, 1, 1)

        unidade = pag_adicionar_vendas.ids[id_label]
        unidade.color = (0, 207/255, 219/255)

    def adicionar_venda(self):
        cliente = self.cliente
        produto = self.produto
        unidade = self.unidade
        
        pag_adicionar_vendas = self.root.ids['adicionar_vendas_page']
        data = pag_adicionar_vendas.ids['id_data'].text.replace("Data: ",'')
        preco = pag_adicionar_vendas.ids['id_preco_total'].text
        quantidade = pag_adicionar_vendas.ids['id_quantidade'].text

        if not cliente:
            pag_adicionar_vendas.ids['id_selecione_cliente'].color = (1, 0, 0)
        if not produto:    
            pag_adicionar_vendas.ids['id_selecione_produto'].color = (1, 0, 0)
        if not unidade:    
            pag_adicionar_vendas.ids['id_kg'].color = (1, 0, 0)
            pag_adicionar_vendas.ids['id_unidades'].color = (1, 0, 0)
            pag_adicionar_vendas.ids['id_litros'].color = (1, 0, 0)
        if not preco:
            pag_adicionar_vendas.ids['id_label_preco'].color = (1, 0, 0)
        else:
            try:
                preco = float(preco)
            except:
                pag_adicionar_vendas.ids['id_label_preco'].color = (1, 0, 0)

        if not quantidade:
            pag_adicionar_vendas.ids['id_label_quantidade'].color = (1, 0, 0)
        else:
            try:
                quantidade = float(preco)
            except:
                pag_adicionar_vendas.ids['id_label_quantidade'].color = (1, 0, 0)

        if cliente and produto and unidade and preco and quantidade and type(preco == float) and type(quantidade == float):
            foto_cliente = cliente + '.png'
            foto_produto = produto + '.png'


            link = f'https://aplicativosvendasaulahash-default-rtdb.firebaseio.com/{self.local_id}/vendas.json?auth={self.id_token}'
            info = f'{{"cliente": "{cliente}", "produto": "{produto}", "foto_cliente": "{foto_cliente}", "foto_produto": "{foto_produto}",'\
                    f'"data": "{data}", "preco": "{preco}", "unidade": "{unidade}", "quantidade": "{quantidade}"}}' 

            requests.post(link, data=info)

            banner = BannerVenda(cliente= cliente, produto= produto, foto_cliente= foto_cliente, foto_produto= foto_produto,
                    data= data, preco= preco, unidade= unidade, quantidade= quantidade)
            
            pagina_home_page = self.root.ids["home_page"]
            lista_vendas = pagina_home_page.ids["lista_vendas"] 
            lista_vendas.add_widget(banner)

            requisicao = requests.get(f'https://aplicativosvendasaulahash-default-rtdb.firebaseio.com/{self.local_id}/total_vendas.json?auth={self.id_token}')
            total_vendas = requisicao.json()

            total_vendas = float(total_vendas)
            total_vendas += preco

            info_total_vendas =  f'{{"total_vendas": "{total_vendas}"}}'
            requests.patch(f'https://aplicativosvendasaulahash-default-rtdb.firebaseio.com/{self.local_id}/.json?auth={self.id_token}', 
                           data=info_total_vendas)

            home_page = self.root.ids['home_page']
            home_page.ids['label_total_vendas'].text = f'[color=#000000]Total de vendas:[/color] [b]R${total_vendas:,.2f}[/b]'

            self.mudar_tela('home_page')

        self.cliente = None
        self.produto = None
        self.unidade = None

    def carregar_todas_vendas(self):
    #prencher a pagina todas as vendas

        # pegar informações da empresa
        requisicao = requests.get(f'https://aplicativosvendasaulahash-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"')
        requisicao_dic = requisicao.json()
        # alterar a foto de perfil com a informação pegada anteriormente
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = f'icones/fotos_perfil/hash.png'

        pagina_todas_vendas = self.root.ids["todas_vendas_page"]
        lista_vendas = pagina_todas_vendas.ids["lista_vendas"] 

        #limpar vendas anteriores
        lista_vendas.clear_widgets()

        total_vendas = 0
        for local_id_usuario in requisicao_dic:
            try:
                vendas = requisicao_dic[local_id_usuario]['vendas']
                for id_venda in vendas:
                    venda = vendas[id_venda]
                    banner = BannerVenda(cliente=venda['cliente'], foto_cliente=venda['foto_cliente'],
                                    produto=venda['produto'], foto_produto=venda['foto_produto'],
                                    preco=venda['preco'], quantidade=venda['quantidade'],
                                    unidade=venda['unidade'], data=venda['data']
                                    )
                    lista_vendas.add_widget(banner)
                    total_vendas += float(venda['preco'])
                    pagina_todas_vendas.ids['label_total_vendas'].text = f'[color=#000000]Total de vendas:[/color] [b]R${total_vendas :,.2f}[/b]'
            except Exception as e:
                print(e)

        self.mudar_tela('todas_vendas_page')
    
    def sair_vendas(self, pagina):
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = f'icones/fotos_perfil/{self.avatar}'

        self.mudar_tela(pagina)

    def acessar_vendedor(self, infos_vendedores, *args):
        self.mudar_tela('vendas_outro_vendedor_page')
        
        # #avatar outro vendedor
        foto_perfil = self.root.ids['foto_perfil']
        avatar = infos_vendedores['avatar']
        foto_perfil.source = f'icones/fotos_perfil/{avatar}'

        total_vendas = 0

        #vendas outro vendedor
        try:
            vendas = infos_vendedores['vendas']
            pagina_outro_vendedor = self.root.ids["vendas_outro_vendedor_page"]
            lista_vendas = pagina_outro_vendedor.ids["lista_vendas"] 
            #limpar vendas anteriores
            lista_vendas.clear_widgets()
            for id_venda in vendas:
                venda = vendas[id_venda]
                banner = BannerVenda(cliente=venda['cliente'], foto_cliente=venda['foto_cliente'],
                                produto=venda['produto'], foto_produto=venda['foto_produto'],
                                preco=venda['preco'], quantidade=venda['quantidade'],
                                unidade=venda['unidade'], data=venda['data']
                                )
                lista_vendas.add_widget(banner)
                total_vendas += float(venda['preco'])
            pagina_outro_vendedor.ids['label_total_vendas'].text = f'[color=#000000]Total de vendas:[/color] [b]R${total_vendas :,.2f}[/b]'
        except Exception as e:
            print(e)

MainApp().run()