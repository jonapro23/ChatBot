<h1 align="center">🤖 Chatbot WhatsApp</h1>

<p align="center">
  Chatbot integrado à <b>API oficial do WhatsApp</b>, com regras próprias, IA opcional e histórico de conversas.
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white">
  <img alt="SQLAlchemy" src="https://img.shields.io/badge/SQLAlchemy-2.0-D71F00">
  <img alt="WhatsApp" src="https://img.shields.io/badge/WhatsApp-Business%20Platform-25D366?logo=whatsapp&logoColor=white">
  <img alt="Testes" src="https://img.shields.io/badge/testes-pytest-0A9EDC?logo=pytest&logoColor=white">
</p>

---

## 📌 Sobre o projeto

Projeto facultativo que implementa um chatbot para WhatsApp usando a **WhatsApp Business Platform** da Meta (sem automação da conta pessoal). O sistema recebe mensagens por **webhook**, decide a resposta com regras próprias e/ou **Inteligência Artificial**, responde automaticamente e **registra cada interação** em banco de dados.

O código é modular (rotas, serviços e modelos separados), fácil de evoluir e coberto por testes automatizados.

## 💬 Exemplo de conversa

```text
Usuário: Olá
Bot:     Olá! Como posso ajudar?

Usuário: [envia uma imagem]
Bot:     No momento consigo processar apenas mensagens de texto.
```

<!-- Adicione prints do bot funcionando: salve em docs/ e descomente as linhas abaixo
![Conversa no WhatsApp](docs/conversa.png)
![Documentação da API](docs/swagger.png)
-->

## ✨ Funcionalidades

- 📥 Recebimento de mensagens via webhook, com identificação do usuário
- 🧠 Respostas por **regras próprias** e/ou **IA** (OpenAI, opcional)
- 📤 Envio automático da resposta pela API oficial
- 🗄️ Registro de mensagem, resposta, tipo, status e data/hora
- 🔁 **Anti-duplicidade** por `message_id` (o mesmo evento nunca é respondido duas vezes)
- 🖼️ Tratamento amigável de tipos não suportados (imagem, áudio, documento)
- 📜 **Histórico de conversas** via API protegida por chave
- 🔐 Validação da assinatura do webhook, logs com telefones mascarados e limite de tamanho das mensagens

## 🧩 Como funciona

```text
Usuário → WhatsApp → API da Meta → POST /webhook → FastAPI
                                                      │
                                       ┌──────────────┼──────────────┐
                                       ▼              ▼              ▼
                                 chat_service     ai_service    Banco (messages)
                                       │
                                       ▼
                               whatsapp_service → API da Meta → WhatsApp → Usuário
```

O webhook responde `200` imediatamente e processa em segundo plano, evitando reenvios da Meta por timeout.

## 🛠️ Tecnologias

| | |
| --- | --- |
| **Linguagem** | Python 3.10+ |
| **Backend** | FastAPI · Uvicorn |
| **Banco de dados** | SQLAlchemy · SQLite (dev) / PostgreSQL (produção) |
| **WhatsApp** | WhatsApp Business Platform (Meta) |
| **IA** | OpenAI (opcional) |
| **HTTP** | httpx |
| **Testes** | pytest |

## 🚀 Começando

### Pré-requisitos

- Python 3.10 ou superior e Git
- Conta de desenvolvedor na [Meta](https://developers.facebook.com)
- [ngrok](https://ngrok.com) (ou similar) para testes locais

### Instalação

```bash
git clone https://github.com/jonapro23/ChatBot.git
cd ChatBot

python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env              # preencha com seus valores
```

### Executando

```bash
python run.py
```

- API em `http://localhost:8000`
- Documentação interativa (Swagger) em `http://localhost:8000/docs`

Em outro terminal, exponha a porta para a Meta alcançar o webhook:

```bash
ngrok http 8000
```

<details>
<summary><b>📱 Configurando a Meta (WhatsApp Business Platform)</b></summary>

<br>

1. Em [developers.facebook.com](https://developers.facebook.com), crie um **aplicativo** com o produto **WhatsApp**.
2. Em **WhatsApp → Configuração da API**, anote o **token de acesso** (o temporário expira em ~24h) e o **Phone number ID** do número de teste.
3. Adicione o seu número como **destinatário autorizado** e confirme o código recebido.
4. Invente um **verify token** (texto secreto) e use o mesmo valor no `.env` e no painel.
5. Em **WhatsApp → Configuração → Webhook**:
   - **URL de callback:** `https://SEU-TUNEL.ngrok-free.app/webhook`
   - **Token de verificação:** o valor de `WHATSAPP_VERIFY_TOKEN`
   - Clique em **Verificar e salvar** e assine o campo **`messages`**.
6. Envie `Olá` para o número de teste e aguarde a resposta.

</details>

## ⚙️ Variáveis de ambiente

Copie o `.env.example` para `.env` e preencha:

| Variável | Obrigatória | Descrição |
| --- | :---: | --- |
| `WHATSAPP_ACCESS_TOKEN` | ✅ | Token de acesso da Meta |
| `WHATSAPP_PHONE_NUMBER_ID` | ✅ | ID do número do WhatsApp Business |
| `WHATSAPP_VERIFY_TOKEN` | ✅ | Texto secreto da verificação do webhook |
| `WHATSAPP_APP_SECRET` | recomendada | Ativa a validação da assinatura `X-Hub-Signature-256` |
| `OPENAI_API_KEY` | — | Vazia = o bot usa apenas as regras próprias |
| `OPENAI_MODEL` | — | Modelo da IA (padrão `gpt-4o-mini`) |
| `DATABASE_URL` | — | Padrão `sqlite:///./chatbot.db` |
| `ADMIN_API_KEY` | — | Chave do histórico; vazia = rota desativada |
| `MAX_MESSAGE_LENGTH` | — | Limite de caracteres por mensagem (padrão `1000`) |

> ⚠️ **Nunca** envie o `.env` ao GitHub. Ele já está no `.gitignore`.

## 🔌 API

| Método | Rota | Descrição |
| --- | --- | --- |
| `GET` | `/webhook` | Verificação do webhook pela Meta |
| `POST` | `/webhook` | Recebe os eventos do WhatsApp |
| `GET` | `/chat/history` | Histórico de conversas (header `X-API-Key`) |
| `GET` | `/health` | Verificação de saúde |

**Consultando o histórico** (filtros opcionais: `phone_number`, `limit`, `offset`):

```bash
curl -H "X-API-Key: SUA_CHAVE" "http://localhost:8000/chat/history?limit=10"
```

<details>
<summary><b>🗄️ Banco de dados e status de processamento</b></summary>

<br>

Tabela `messages`, criada automaticamente ao iniciar:

| Campo | Descrição |
| --- | --- |
| `id` | Identificador interno |
| `message_id` | ID da mensagem no WhatsApp (único) |
| `phone_number` | Número do usuário |
| `user_name` | Nome disponível no evento |
| `user_message` | Texto recebido |
| `bot_response` | Resposta enviada |
| `message_type` | `text`, `image`, `audio`, `document`… |
| `status` | Status do processamento |
| `created_at` | Data/hora do registro |

Status possíveis: `received` · `replied` · `unsupported` · `invalid` · `ai_error` · `send_failed` · `error`

</details>

<details>
<summary><b>📁 Estrutura do projeto</b></summary>

<br>

```text
chatbot-whatsapp/
├── app/
│   ├── main.py                  # aplicação FastAPI
│   ├── config.py                # variáveis de ambiente
│   ├── database.py              # engine, sessão e criação das tabelas
│   ├── security.py              # assinatura do webhook, chave admin, máscara de telefone
│   ├── models/
│   │   └── message.py           # tabela messages
│   ├── routes/
│   │   ├── webhook_routes.py    # GET/POST /webhook
│   │   └── chat_routes.py       # GET /chat/history
│   └── services/
│       ├── whatsapp_service.py  # extrai o payload e envia mensagens
│       ├── ai_service.py        # integração com a IA
│       └── chat_service.py      # orquestra o fluxo principal
├── tests/
├── .env.example
├── requirements.txt
└── run.py
```

</details>

## 🧪 Testes

```bash
pytest
```

Os testes não usam a rede e cobrem verificação do webhook, assinatura, payload inválido, eventos de status, saudação, mensagens duplicadas, tipos não suportados, mensagens longas e o histórico.

## 🔒 Segurança

- Credenciais somente em variáveis de ambiente
- Verificação do token do webhook e da assinatura `X-Hub-Signature-256`
- Histórico protegido por chave de API
- Telefones mascarados nos logs; erros técnicos nunca são enviados ao usuário
- Armazenamento mínimo de dados pessoais
- HTTPS obrigatório em produção

## ☁️ Deploy

Use um servidor com HTTPS (Render, Railway, AWS, Azure, Google Cloud…):

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Em produção, use **PostgreSQL** via `DATABASE_URL` (o SQLite se perde em discos efêmeros), configure `WHATSAPP_APP_SECRET`, troque o token temporário por um **token permanente** da Meta e atualize a URL do webhook.

## 🗺️ Roadmap

- [ ] Menu automático e comandos (`menu`, `ajuda`, `sair`)
- [ ] IA com contexto das mensagens anteriores
- [ ] Painel administrativo
- [ ] Autenticação de administradores
- [ ] Suporte a imagem, áudio e documentos
- [ ] Migrações com Alembic

## 👤 Autor

**Jonathan Freitas** — [@jonapro23](https://github.com/jonapro23)