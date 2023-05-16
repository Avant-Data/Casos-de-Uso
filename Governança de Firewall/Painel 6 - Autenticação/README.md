<p align="center">
    <a href="" rel="noopener">
    <img width=250px height=82px src="https://i.imgur.com/zHVh1RJ.png" alt="Project logo"></a>
</p>
<h3 align="center">Painel 6 - Autenticação</h3>
<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
</div>


---
<p align="center"> Painel que traz as principais informações de autenticação do Firewall.
    <br> 
</p>

## <p style="color:yellow" >Índice</p>

- [Sobre](#about)
- [Precauções](#precaution)
- [Construído Utilizando](#built_using)

<br>

## <a style="color:yellow" name = "about"> Sobre</a>
<br>

![permission table](https://i.imgur.com/xItF0BH.png)

Esse painel traz uma visão geral dos dados do índice de <b>auth</b>, que trata da autenticação e permissões do Firewall.Começando com um cabeçalho, criado em formulário seguindo o padrão apresentado no [manual de Cabeçalho](https://github.com/Avant-Data/Dashboards/tree/master/Header).

Logo abaixo temos a criação de uma tabela com os usuários e suas permissões, como forma de entender, fiscalizar e auditar quem tem acesso restrito. Para maior detalhes de como criar uma tabela utilizando o formulário do dashboard veja o [manual de DataTable](https://github.com/Avant-Data/Dashboards/tree/master/Datatable).

Após, alguns gráficos trazem informações importantes sobre os tipos de usuários.

![charts permission](https://i.imgur.com/ZGIO7Eb.png)

<br>

##  <a style="color:yellow" name = "precaution">Precauções</a>
<br>

O modelo disponibilizado pelo código fonte conta com alguns elementos HTML com atributo "id" e por isso, para usar em outros paineis, é necessário alterar todos os atributos "id" e todos os lugares onde ele é utilizado.

Os atributos "id" são uma identidade ÚNICA de cada elemento, caso contrário ele pode ter problemas para funcionar gerando conflitos na leitura do código pelo navegador.

O mesmo acontece com os nomes de cada 'function' JavaScript, cada nome deve ser único para cada cópia desse modelo em uma visualização, tanto na criação, quando na hora de executar.

<br>

##  <a style="color:yellow" name = "built_using">Construído Utilizando</a>

- [AvantData](https://www.avantdata.com.br/) - Plataforma de análise, correlacionamento e gestão de dados em redes corporativas
- [AvantApi](https://avantapi.avantsec.com.br/) - Família de endpoints RESTFUL API para customização de ações no AvantData
- [MDBootstrap](https://mdbootstrap.com/) - Biblioteca de aparências e estilos 
- [DataTable](https://datatables.net/) - Biblioteca de montagem e formatação de tabelas. 
