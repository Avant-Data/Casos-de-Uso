<p align="center">
  <a href="" rel="noopener">
 <img width=250px height=82px src="https://i.imgur.com/zHVh1RJ.png" alt="Project logo"></a>
</p>

<h3 align="center">Governança de Firewall</h3>

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()

</div>

---

<p align="center"> Exemplo de visualização no Dashboard sobre Governança de Firewall.
    <br> 
</p>

## <p style="color:yellow" >Índice</p>
- [Sobre](#about)
- [Conector](#conector)
- [Criando dashboard](#starting)
- [Script](#script)
- [Construído Utilizando](#built_using)


## <a style="color:yellow" name = "about">Sobre</a>
Monitorar o Firewall é uma das atividades constantes das empresas, por isso o AvantData oferece uma ideia de vigilância sobre os dados coletados que facilita o trabalho do gestor de forma prática e rápida.

Esse é um modelo de uma utilização completa da ferramenta para criar uma visualização feita no dashboard que exibem dados sobre o Firewall coletados através de um script que grava o resultado no banco não relacional nativo do AvantData. Alguns dados de configuração que serão criados no decorrer do modelo são salvos num banco relacional (SQL). Recomenda-se a utilização de um banco protegido, visto que essa atividade deve ser exclusiva de gestor, por isso nesse modelo será feito através de um <i>conector</i>.

O código fonte do script para indexação dos dados é feito na linguagem python, enquanto toda a visualização é feita em linguagem frontEnd de programação web (HTML5, CSS3 e JavaScript).

```
Obs: Esse modelo é criado para ser usado nos cartões de formulário no Dashboard do AvantData, visto que depende de bibliotecas ja instaladas no programa.
```

## <a style="color:yellow" name = "conector">Conector</a>

No AvantData existe a possibilidade do usuário vincular outros bancos de dados externos para serem acessados pela ferramenta, quando configuramos uma fonte dessas chamamos de <i>Conector</i>. Isso se aplica também para composições de banco interno protegidos de alguma forma, seja por senha ou certificado.

Para criar um Conector, é necessário ir até a pagina de Banco de Dados do AvantDAta, conforme a imagem da barra de navegação a seguir.

![barra de navegação](https://i.imgur.com/lERoZkC.png)

Na página, existe um bloco de configurações onde é possível passar todas as informaçãoes do banco que será vinculado. Os campos trazem a possibilidade de acessar modelos de vários tipos tais quais: <b>MySql, PostgreSQL, Oracle, SQLserver, MariaDB, LDAP e Drill</b>. Nesse modelo será utilizado um exemplo de PostgreSQL.

```
Obs: Na mesma página é possivel também criar querys de pesquisa utilizando a aba de configuração de query. 
```

![Configuração do Conector](https://i.imgur.com/KJrguF4.png)

Após a configuração, para testar se o conector está funcionando basta fazer uma pesquisa na Tela Principal. Ao clicar no campo de texto, uma opção de "conector" vai aparecer e utilizando a tecla "espaço" é possivel buscar as opções subsequentes para compor o texto de busca. Escolha o Conector criado e faça uma query (ou escolha alguma ja configurada) para fazer a busca, conforme o exemplo abaixo.

![Exemplo de pesquisa com conector](https://i.imgur.com/kGk908r.png)

Nesse modelo, o Conector será usado para armazenar configurações que serão utilizadas na visualização do dashboard. Para isso é preciso a prévia criação de algumas tabelas e dados padrão que já estão disponíveis no arquivo <i>scriptBanco.txt</i>. Esse arquivo contém uma sequência de comandos SQL (linguagem do banco de dados relacional) que vai criar as tabelas base e inserir alguns dados iniciais, mas para funcionar o usuário deve executar esses comandos no banco de dados que foi vinculado.

<br>

## <a style="color:yellow" name = "starting">Criando dashboard</a>
<br>


Inicialmente, para montar uma visualização vá até a tela de Dashboard. A tela inicial do dashboard é uma navegação de pastas e visualizações onde é possível criar uma <b>nova visualização</b> dentro do item escolhido através do menu de contexto.

![criando visualização](https://i.imgur.com/XCNafe6.png)

As visualizações são subdivididas em paineis, que por sua vez são subdivididos em cartões. Os cartões podem conter vários tipos diferentes de apresentação de dados, nesse modelo trabalharemos com gráficos e formulários. A criação dos cartões é feita através do menu de contexto dentro do espaço de cada painel, como na imagem a seguir.

![Criando Cartão](https://i.imgur.com/Sx9hPLC.png)

Ao abrir a modal de edição, cole o código fonte no espaço de texto. Atente-se às dimensões desejadas. Todos os cartões de formulário feitos nessa visualização serão formados dessa forma.

## <a  style="color:yellow" name = "script">Script</a>

O script responsável por buscar e indexar os dados do firewall no AvantData automaticamente separa os dados em contextos para facilitar a leitura dos dados.


- `Session  ⮕ Agrupa dados de sessão da máquina do Firewall`
- `Health   ⮕ Agrupa dados sobre a saúde do Firewall`
- `Auth     ⮕ Agrupa dados sobre as autorizações e autenticações do Firewall`
- `Network  ⮕ Agrupa dados de acesso na rede pelo Firewall`
- `Rules    ⮕ Agrupa dados das regras de Firewall`
- `Backup   ⮕ Agrupa dados de backup do Firewall`

<br>

## <a  style="color:yellow" name = "built_using">Construído Utilizando </a>

- [AvantData](https://www.avantdata.com.br/) - Plataforma de análise, correlacionamento e gestão de dados em redes corporativas.
- [AvantApi](https://avantapi.avantsec.com.br/) - Família de endpoints RESTFUL API para customização de ações no AvantData.
- [MDBootstrap](https://mdbootstrap.com/) - Biblioteca de aparências e estilos.
- [FusionCharts](https://www.fusioncharts.com/) - Biblioteca de criação de gráficos.
- [DataTable](https://datatables.net/) - Biblioteca de montagem e formatação de tabelas.
