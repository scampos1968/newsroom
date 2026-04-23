Newsroom

Leitor pessoal de notícias, elegante e mobile-first, criado para centralizar artigos de jornalistas, colunistas e editoriais específicos que o usuário acompanha com assinatura.

O objetivo é substituir a necessidade de abrir múltiplos sites, newsletters e apps separados, reunindo tudo em uma única interface limpa, rápida e pensada para iPhone e iPad.

⸻

Visão geral

O Newsroom é um app pessoal para acompanhar autores, e não apenas veículos. Ele reúne artigos de diferentes fontes em uma experiência unificada, permitindo:

* acompanhar textos de colunistas específicos;
* visualizar rapidamente o que é novo;
* marcar artigos como lidos;
* salvar favoritos;
* acessar tudo em uma interface simples e agradável no celular.

⸻

Arquitetura

O projeto é dividido em duas partes independentes:

Backend

Responsável por buscar, armazenar e servir os artigos.

* Linguagem: Python 3.10+
* Framework: FastAPI + Uvicorn
* Banco de dados: SQLite via SQLModel
* Bibliotecas principais: feedparser, httpx, beautifulsoup4

O backend roda localmente no Mac Mini e expõe uma API REST consumida pelo frontend.

Frontend

Interface do app.

* Formato: arquivo HTML único
* Tecnologias: HTML + CSS + JavaScript inline
* Dependências: sem framework, bundler ou build step
* Entrega: servido pelo próprio backend
* Uso: Safari no iPhone e iPad

⸻

Conectividade

A comunicação entre frontend e backend é feita via Tailscale, funcionando como uma VPN pessoal entre o iPhone/iPad e o Mac Mini.

Vantagens

* custo zero;
* sem necessidade de IP fixo;
* sem abertura de portas no roteador;
* acesso remoto seguro;
* controle total dos dados.

Limitação

* o Mac Mini precisa estar ligado;
* o Tailscale precisa estar ativo no iPhone/iPad para uso fora de casa.

⸻

Estratégias de busca de artigos

O sistema suporta três modos de ingestão por autor, configuráveis individualmente.

1. RSS direto

Usado quando o veículo oferece feed RSS específico por autor.

Exemplos:

* Bloomberg / Mark Gurman
* Financial Times / Martin Wolf
* The Economist / The Telegram

Fluxo: parse do feed e salvamento de artigos novos.

2. Filtro de feed

Usado quando o feed é compartilhado entre vários autores.

Exemplos:

* New York Times / Thomas Friedman
* Estadão / Editorial

Fluxo: baixa o feed geral e filtra pelo byline configurado.

3. Scraping de página

Usado quando não existe feed RSS por autor.

Exemplos:

* O Globo / Thaís Oyama, Fernando Gabeira
* Estadão / colunistas semanais

Fluxo: acessa a página do autor, extrai os links dos artigos e salva os novos.

⸻

Extração de datas

A origem da data depende do tipo de fonte:

* RSS: a data vem diretamente do feed;
* Scraping O Globo: o sistema extrai ano e mês do padrão de URL, como /2026/04/;
* Scraping Estadão: o sistema faz uma requisição adicional ao artigo e extrai datePublished do JSON-LD.

⸻

Configuração por autor

Cada autor possui parâmetros próprios no banco:

* fetch_mode — estratégia de busca (rss, filter, scrape)
* max_articles — limite de artigos armazenados
* ignore_date_filter — ignora o filtro de 2 dias, útil para colunistas semanais
* active — ativa ou desativa o autor sem deletá-lo
* filter_byline — texto para filtrar feeds compartilhados; também pode ser reutilizado como padrão de URL no scraping do Estadão

Essa modelagem dá flexibilidade para expandir a base de autores sem alterar a lógica central do sistema.

⸻

API REST

Endpoints principais

* GET /authors/ — lista autores
* POST /authors/ — cria autor
* PATCH /authors/{id} — atualiza autor, inclusive ativo/inativo
* GET /articles/ — lista artigos com filtros
* PATCH /articles/{id}/read — marca como lido
* PATCH /articles/{id}/favorite — favorita ou desfavorita
* POST /fetch — dispara busca manual de todos os feeds

⸻

Scheduler

Um processo separado, scheduler.py, roda em loop e chama fetch_all_feeds() periodicamente.

* frequência padrão: 1 hora
* configuração via variável de ambiente: FETCH_INTERVAL

Isso mantém a base atualizada sem intervenção manual.

⸻

Frontend

O frontend foi desenhado para ser simples, bonito e altamente funcional no mobile.

Características principais

* interface mobile-first;
* tema claro/escuro com persistência;
* tipografia elegante;
* sem dependência de frameworks;
* carregamento leve e rápido.

Tipografia

* Playfair Display para títulos
* DM Sans para interface

⸻

Telas

Feed

* lista de artigos;
* hero card para o mais recente;
* filtros por tag;
* pills de navegação.

Detalhe

* título;
* autor;
* data;
* botão para abrir o artigo no site original.

Autores

* lista de autores;
* toggle ativo/inativo;
* contagem de artigos;
* badge de não lidos.

Artigos do autor

Ao tocar em um autor, abre a lista filtrada com todos os artigos daquele nome.

Favoritos

Reúne os artigos salvos pelo usuário.

⸻

Funcionalidades

* marcar artigo como lido;
* favoritar ou desfavoritar;
* ativar ou desativar autor sem deletar;
* adicionar novo autor pelo app;
* filtrar por tag;
* mostrar a hora da última atualização no header;
* reduzir opacidade de artigos lidos;
* aplicar itálico ao título de artigos já lidos;
* limpar sufixos como - O GLOBO e - Estadão dos títulos;
* favicon SVG com N dourado.

Tags atuais

* Tecnologia
* IA
* Mercados
* Política
* Macro

⸻

Autores configurados

* Mark Gurman — Bloomberg
* Martin Wolf — Financial Times
* Thomas Friedman — The New York Times
* Editorial — Estadão
* Malu Gaspar — O Globo
* Elena Landau — Estadão
* Guy Perelmuter — Estadão
* William Waack — Estadão
* Lourival Sant’Anna — Estadão
* Carlos A. Di Franco — Estadão
* Thaís Oyama — O Globo
* Fernando Gabeira — O Globo
* The Telegram — The Economist

⸻

Infraestrutura

Ambiente atual

* servidor local em Mac Mini;
* acesso remoto via Tailscale;
* custo operacional: zero.

Trade-off principal

A disponibilidade do produto depende do Mac Mini estar ligado e acessível.

⸻

Como rodar

# 1. Instalar dependências
pip3 install -r requirements.txt
# 2. Criar banco e popular autores
python3 seed.py
# 3. Buscar artigos pela primeira vez
python3 -c "from app.fetcher import fetch_all_feeds; fetch_all_feeds()"
# 4. Iniciar API
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
# 5. Iniciar scheduler (em outro terminal)
python3 scheduler.py

⸻

Estrutura conceitual do sistema

[iPhone / iPad Safari]
        |
        |  via Tailscale
        v
[FastAPI backend no Mac Mini]
        |
        +--> [SQLite / SQLModel]
        |
        +--> [Fetchers RSS / Filter / Scrape]
        |
        +--> [HTML único servido pelo backend]

⸻

Pontos fortes do projeto

1. Arquitetura enxuta e eficiente
    * FastAPI + SQLite + HTML único formam uma base extremamente leve para esse caso de uso.
2. Foco em autores, não só em veículos
    * Isso dá identidade clara ao produto.
3. Boa flexibilidade de ingestão
    * O sistema aceita fontes com RSS direto, RSS compartilhado e scraping.
4. Baixo custo operacional
    * Sem necessidade de cloud obrigatória.
5. Experiência mobile muito adequada ao uso real
    * O app foi pensado para consumo rápido e recorrente.

⸻

Riscos e pontos de atenção

1. Fragilidade de scraping
    * Mudanças no HTML dos sites podem quebrar coletores.
2. Dependência de fontes externas
    * Feeds, páginas de autor e estruturas de sites podem mudar sem aviso.
3. Disponibilidade do servidor
    * O produto depende do Mac Mini estar online.
4. Escalabilidade futura
    * Se o número de autores crescer muito, pode ser necessário reforçar cache, logs e retries.
5. Ausência de autenticação formal
    * Hoje isso faz sentido para uso pessoal, mas exigiria reforço se o app evoluir além disso.

⸻

Próximos passos possíveis

* script de inicialização automática no boot do Mac;
* deploy opcional em cloud para independência do hardware local;
* expansão da base de autores e veículos;
* notificações push para artigos novos;
* logs e monitoramento de falhas de fetch.

⸻

Posicionamento do produto

O Newsroom não é um agregador genérico de notícias. Ele é um reader pessoal de colunistas, desenhado para quem quer acompanhar vozes específicas com mais conforto, organização e velocidade.
