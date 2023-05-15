<p align="center">
    <a href="" rel="noopener">
    <img width=250px height=82px src="https://i.imgur.com/zHVh1RJ.png" alt="Project logo"></a>
</p>
<h3 align="center">Painel 2 - Overview</h3>
<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
</div>


---
<p align="center"> Painel de visualização geral, apresentando alguns gráficos sobre a visão geral do Firewall.
    <br> 
</p>

## <p style="color:yellow" >Índice</p>

- [Sobre](#about)
- [Precauções](#precaution)
- [Construído Utilizando](#built_using)

<br>

## <a style="color:yellow" name = "about"> Sobre</a>
<br>



Esse painel traz uma visão geral das regras de firewall, com gráficos que apresentam as principais regras e suas conformidades com os ítens estipulados no painel anterior. Começando com um cabeçalho, criado em formulário seguindo o padrão apresentado no [manual de Cabeçalho](https://github.com/Avant-Data/Dashboards/tree/master/Header).

Os gráficos buscam no índice "rules" criado pelo script os dados de Firewall para evidenciar se existem regras em desconformidade com o padrão previamente estabelecido.

![graficos overview](https://i.imgur.com/jowALAL.png)


Ao final, é paresentado um cartão em formulário, onde é montada uma tabela apresentando todas as regras de Firewall cujo nome está em desacordo com o padrão criado no painel anterior. O campo de expressão (REGEX) vai determinar qual é o modelo a ser seguido.


![Tabela nomesfora do padrão](https://i.imgur.com/4ywrQb4.png)

O código fonte fornecido traz inicialmente uma configuração de variáveis globais para auxciliar na pesquisa.

```js
var conn = "FirewallGovernance"             // NOME DO CONECTOR
var tableControl = 'public.controlitens'    // NOME DA TABELA DE ITENS DE CONTROLE
var keytermName = 'name'                    // TERMO CHAVE DO ITEM SOBRE PADRÃO DE NOME         
var regexName = ''                                          
```

Essas variáveis serão usadas para fazer a primeira busca no Conector, filtrando pela palavra chave determinada. Essa palavra chave é a mesma que foi configurada no 'painel 1 - Governancia', no ítem de controle sobre a padronização da nomenclatura das regras de firewall. Ao fazer a busca, o campo de 'Expressão' será salvo dentro da variável 'regexName'.

```js
//Faz a busca Pelo conector previamente configurado e traz o padrão
    function getNameRule() {
        let querySelect = {
            "conector": conn,
            "query": `SELECT expression FROM ${tableControl} WHERE keyterm = '${keytermName}'`
        }
        $.ajax({
            url: `/avantapi/sql/selectQuery`,
            method: 'POST',
            async: false,
            data: JSON.stringify(querySelect),
            success: (resp) => {                
              
                regexName = '';
                regexName = resp[0].expression;
                $('#regexSubtitle').html(`Padrão: ${regexName}`)
            },
            error: (er) => {
                console.log(er)
            }
        })
    }  
```

A segunda pesquisa é feita no índice "rules" criado pelo script, trazendo todos os nomes das regras que foram encontradas para construir a tabela. Para maior detalhes de como criar uma tabela utilizando o formulário do dashboard veja o [manual de DataTable](https://github.com/Avant-Data/Dashboards/tree/master/Datatable). A única diferença desse modelo, além da fonte de pesquisa, é que cada linha da tabela recebe uma verificação: caso o nome da regra encontrada se encaixe com o padrão de REGEX, ela não aparece na tabela. Ou seja, somente as regras fora do padrão vão ser apresentadas.

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
