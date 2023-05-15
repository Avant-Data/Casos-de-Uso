<p align="center">
    <a href="" rel="noopener">
    <img width=250px height=82px src="https://i.imgur.com/zHVh1RJ.png" alt="Project logo"></a>
</p>
<h3 align="center">Painel 1 - Governaça</h3>
<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
</div>


---
<p align="center"> Tabela de itens de controle sobre as regras do Firewall.
    <br> 
</p>

## <p style="color:yellow" >Índice</p>

- [Sobre](#about)
- [Estrutura](#structure)
- [Pesquisa](#search)
- [Aplicando DataTable](#DataTable)
- [Filas AvantFlow](#AvantFlowQueues)
- [Precauções](#precaution)
- [Construído Utilizando](#built_using)

## <a style="color:yellow" name = "about"> Sobre</a>
<br>

![Governança](https://i.imgur.com/W4PnaZg.png)

No modelo oferecido, é feita uma divisão de contexto para cada painel, onde o primeiro traz uma ideia geral de governança. Alguns paineis contem um cabeçalho, criado em formulário seguindo o padrão apresentado no [manual de Caceçalho](https://github.com/Avant-Data/Dashboards/tree/master/Header).

É apresentado um cartão do tipo formulário com uma tabela. As informações dessa tabela são diretrizes que se aplicam as regras de Firewall. São órdens que toda a gerência de regras deve obedecer. 

```
Ex: Um dos itens tem o controle "Geração de log obrigatória", ou seja, caso esse item esteja marcado como 'ativo' todas as regras do Firewall devem obrigatóriamente estar gerando log, caso contrário será executada a 'ação', que é uma saída, podendo ser mandar um email, gerar um ticket no AvantFlow, abrir um alerta entre outros.
```

A estrutura de criação da tabela segue o mesmo modelo apresentado no [tutorial de DataTable ](https://github.com/Avant-Data/Dashboards/tree/master/Datatable).

Essa tabela deve receber as informações do banco de dados que foi vinculado, por isso o nome do Conector que foi criado deve ser informado, bem como o nome das tabelas criadas nele. Essa informação deve ser passada através de algumas variáveis que ficam no início da parte de JavaScript do código fontefornecido. Nesse caso, o modelo traz um Conector com o nome "FirewallGovernance", mas deve ser alterado com o nome criado pelo usuário.

```js
    var connector = "FirewallGovernance"        // NOME DO CONECTOR
    var table = 'public."controlitens"'         // NOME DA TABELA DE ITENS DE CONTROLE
    var tableAction = 'public."actions"'        // NOME DA TABELA DE AÇÕES
    var tablePriority = 'public."priorities"'   // NOME DA TABELA DE PRIORIDADES
```

Cada item de controle tem uma prioridade, palavra chave e uma configuração básica para cada tipo diferente de ação de saída, bem como um campo de Expressão, onde podem ser usadas expressões regulares (regex) para determinar algum contexto. É possivel editar todos os campos inclusive alguns que não estão apresentados na tabela, como o de palavra chave, através do menu de contexto.

A modal (janela) de edição automaticamente se adapta conforme o usuário escolha diferentes opções do campo "Ação". Observe que quando a opção está em 'Ticket' existe uma caixa de opções de 'Fila' onde são buscadas automaticamente as filas do AvantFlow disponíveis. É possível alterar o estatis de "Ativo" sem precisar abrir a modal de edição, pois na própria tabela existe o botão que faz essa alteração para agilizar os processos do gestor.<p name = "modaleditar"></p>

![editar](https://i.imgur.com/k0O5V5H.png)

```
Obs: Caso o gestor queira criar outro item de controle além dos já existentes, é possível através do menu de contexto existente no título ou cabeçalho da tabela, que vai abrir uma modal igual a de edição.
```

## <a style="color:yellow" name = "structure"> Estrutura</a>
<br>

A estrutura do código fonte é dividida em três partes. A primeira é escrito em uma linguagem CSS3, onde acontece a estilização dos elementos, isto é, escolha de cores, margens, tamanho de fonte entre outras coisas. Esse manual não vai se aprofundar sobre o funcionamento dessa parte, mas caso deseje fazer alguma alteração, é possivel encontrar vários tutoriais pela internet como [esse](https://www.w3schools.com/css/).

A segunda parte é a composição em HTML5, que é formada por dois blocos. Um para o título e outro para a tabela. Observe que o bloco da tabela está vazio, pois será preenchido pela criação dinâmica utilizando funções de JavaScript.

```html
<div >
    <!-- Bloco do Título -->
    <div class="row divTitleCrud menuCreate">
        <div class="col-1">
            <div class="row">
                <div class="col-12 line2"></div>
                <div class="col-12 line1"></div>
            </div>
        </div>
        
        <div class="col-10 ">
            <h3 >CONFORMIDADE DE CONFIGURAÇÃO DE FIREWALL</h3>
        </div>

        <div class="col-1">
            <div class="row">
                <div class="col-12 line2"></div>
                <div class="col-12 line1"></div>
            </div>
        </div>
    </div>
    
    <!-- Bloco da tabela -->
    <div class="mapd" id="divTableCrudFirewall">        
       
    </div>   
    
</div>
```


##  <a style="color:yellow" name = "search">Pesquisa</a>

A partir daqui, todo o código fonte está na linguagem JavaScript. Dividido em funções e blocos de lógica.

Esse modelo realiza as pesquisas através de uma função 'Ajax" que está vinculado a biblioteca JQuery nativa do AvantData. Nesse cartão, todos os dados buscados são provenientes do banco de dados que vinculamos como Conector, dessa forma utilizaremos rotas da AvantAPI já preparada para fazer consulta nos conectores cadastrados.

Exitem várias buscas de dados utilizando esse sistema no código fonte, todas elas usam a mesma rota de API. A função <b>'executeFirewallQuery(query, option)'</b> é responsável por fazer todas as pesquisas. Ela tem dois argumentos, um deles é o mais importante: 'query' que vai ser o comando de busca de acordo com a documentação da rota usada.

No exemplo abaixo, vemos um recorte de código fonte onde armazena-se um json contendo a query de pesquisa dentro de uma variável e depois envia essa variável como argumento da função <b>'executeFirewallQuery'</b> para ser buscada. Observe que dentro do json existe um campo que comunica qual é o Conector que será usado e outro que descreve qual será a query. Importante observar também que os fragmentos '${tableAction}' e 'conector' estão utilizando outras variáveis com os nomes da tabela e Conector que foram criadas no começo do código JavaScript

```js

            var querySelect = {
                "conector": connector,
                "query": `SELECT id, type from ${tableAction}`
            }       
            
            executeFirewallQuery( querySelect )    

```

Ao ser enviado para a função <b>'executeFirewallQuery'</b>, por sua vez vai chamar a API por meio do AJAX, sempre com a URL, segundo o exemplo do recorte a seguir.


```js

        function executeFirewallQuery( query, option ) {
            
                $.ajax({
                    url: `/avantapi/sql/selectQuery`,
                    method: 'POST',
                    async: false,
                    data: JSON.stringify(query),
                    success: (resposta) => {
                    
                        // Verifica qual é a 'option' e assim fazer algo com a resposta da pesquisa
                    }
                })
        }
```

Observe que existe um segundo argumento 'option' que serve de palavra chave para saber o que será feito com o resultado da busca. Isso acontece pois todas as pesquisas utilizam dessa mesma função e cada uma delas tem uma utilidade diferente. Ex: Ao fazer a busca na tabela dos itens de controle, o que deve ser feito com o resultado é montar a tabela, mas ao trazer os resultados da tabela de ações, o que deve ser feito é criar um campo com as opções para serem escolhidas.

<br>

##  <a style="color:yellow" name = "DataTAble">Construindo tabela</a>
<br>

Ainda dentro da função 'executeFirewallQuery' existe uma verificação para caso seja uma busca cujo objetivo é usar o resultado para criação de tabela ('filTable'). Nesse momento é executada a função de apoio <b>'createBodyTable()'</b> que controi o esqueleto da tabela, ainda sem conteúdo.

```js
function createBodyTable() {
        $('#divTableCrudFirewall').html('')
        $('#divTableCrudFirewall').html(`
        <table class="tableCrudFirewall table table-striped" id="tableFirewallRules">
            <thead class="theadCrud menuCreate">
                <tr class='text-center p-3'>
                                          
                    <th class="percentNum" >N°</th>
                    <th class="" >ÍTEM DE CONTROLE</th>
                    <th class="percentAtivo" >ATIVO</th>
                    <th class="" >EXPRESSÃO</th>
                    <th class="" >AÇÃO</th>              
                    <th class="" >PRIORIDADE</th>
                    
                </tr>
            </thead>
            
            <tbody id="bodyTableCrudFirewall"></tbody>
        </table>
        `)
}
```
Observe que é nesse momento que são construídas as colunas da tabela, então caso o usuário queira alterar o nome, a órdem ou até a quantidade de colunas, deve-se alterar os elementos 'th'.

Após isso começa um loop que percorre todo os resultados da pesquisa e cria uma linha da tabela por vêz. Caso tenha feito alguma alteração nas colunas, a linha deve ser editada também para acompanhar as mudanças. Observe que ao final do loop, é chamado uma função 'contextMenuTableFirewall()' que é responsável por criar um menu de contexto em cada linda, sendo possível editar item por item.

Em seguida é aplicada a biblioteca DataTable por meio da função 'setDataTableLib'.

Para mais informaçãoes de como montar a estrutura e aplicar a biblioteca DataTable, acesse o [manual de Tabela](https://github.com/Avant-Data/Dashboards/tree/master/Datatable#search) com mais detalhes seguindo outro exemplo; E para maiores informações de como funciona a aplicação do menu de contexto acesse o [manual de ContextMenu](https://github.com/Avant-Data/Dashboards/tree/master/ContextMenu#about).

<br>

##  <a style="color:yellow" name = "AvantFlowQueues">Filas AvantFlow</a>
<br>

Uma das facilidades desse modelo é poder escolher a fila do AvantFlow para abrir tickets no caso do campo "ação" for "ticket". Isso é feito em uma das funções, exemplificada abaixo, que também utiliza da AvantAPI e uma requisição 'ajax'. A resposta dessa busca, ou seja, a lista de filas, será armazenada em uma variável global de apoio que foi criada no começo do código. Posteriormente, ao abrir a janela de criação ou edição dos itens de controle, essa lista será colocada como opções do campo fila que só aparece quando o capo 'ação' for mudado para 'ticket'. Essa função é executada no início da carregação da página apenas uma vez.

```js

        function getQueuesAvantFlow() {
                $.ajax({
                    url: '/avantapi/avantFlow/queues',
                    method: 'GET',
                    success: (filas) => {
                        objQueue = filas
                    },
                    error: (er) => {               
                        console.log({er})
                    }
                })
            }
```

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
