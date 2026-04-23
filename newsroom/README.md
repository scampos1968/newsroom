# Newsroom — Backend

Backend em Python (FastAPI) que busca artigos dos seus autores favoritos via RSS, scraping e feeds filtrados.

## Autores pré-configurados

| Autor | Veículo | Modo |
|---|---|---|
| Mark Gurman | Bloomberg | RSS direto |
| Martin Wolf | Financial Times | RSS direto |
| Thomas Friedman | The New York Times | Filtro no feed de Opinião |
| Editorial | Estadão | RSS direto |
| Malu Gaspar | O Globo | Scraping da página |

---

## Rodar localmente

### 1. Instalar dependências

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Criar o banco e popular autores

```bash
python seed.py
```

### 3. Buscar os artigos pela primeira vez

```bash
python -c "from app.fetcher import fetch_all_feeds; fetch_all_feeds()"
```

### 4. Iniciar a API

```bash
uvicorn app.main:app --reload --port 8000
```

Acesse `http://localhost:8000/docs` para ver a documentação interativa.

### 5. (Opcional) Iniciar o agendador de busca automática

Em outro terminal:

```bash
python scheduler.py
```

---

## Endpoints principais

| Método | Rota | Descrição |
|---|---|---|
| GET | `/authors/` | Lista todos os autores |
| POST | `/authors/` | Adiciona novo autor |
| PATCH | `/authors/{id}` | Atualiza autor |
| DELETE | `/authors/{id}` | Remove autor |
| GET | `/articles/` | Lista artigos (com filtros) |
| PATCH | `/articles/{id}/read` | Marca como lido |
| PATCH | `/articles/{id}/favorite` | Favorita/desfavorita |
| POST | `/fetch` | Dispara busca manual |

### Parâmetros de `/articles/`

```
?author_id=1          filtra por autor
?tag=Tecnologia       filtra por tag
?unread_only=true     só não lidos
?favorites_only=true  só favoritos
?limit=50&offset=0    paginação
```

---

## Adicionar novo autor via API

```bash
curl -X POST http://localhost:8000/authors/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sérgio Vale",
    "venue": "MB Associados",
    "page_url": "https://www.mba.com.br/blog",
    "rss_url": "https://www.mba.com.br/feed",
    "fetch_mode": "rss",
    "tags": ["Macro", "Mercados"]
  }'
```

### Modos de busca (`fetch_mode`)

- **`rss`** — usa o `rss_url` diretamente
- **`filter`** — filtra um feed grande pelo nome do autor (ex: NYT Opinion) — precisa de `filter_feed_url` e `filter_byline`
- **`scrape`** — faz scraping da página do autor — precisa de `scrape_url`

---

## Deploy no Railway (quando quiser)

1. Crie uma conta em [railway.com](https://railway.com)
2. Conecte seu repositório GitHub com esta pasta
3. Railway detecta Python automaticamente
4. Adicione as variáveis de ambiente:
   - `DATABASE_URL` (opcional — por padrão usa SQLite local)
   - `FETCH_INTERVAL` = `3600` (busca a cada 1 hora)
5. O `Procfile` já configura API + scheduler automaticamente

---

## Variáveis de ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./newsroom.db` | URL do banco |
| `FETCH_INTERVAL` | `3600` | Intervalo de busca em segundos |
| `PORT` | `8000` | Porta da API (Railway define automaticamente) |
