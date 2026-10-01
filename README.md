Chatbot WhatsApp — Projeto Facultativo
Chatbot integrado ao WhatsApp Business Platform (API oficial da Meta). Ele recebe mensagens por webhook, processa com regras próprias e/ou Inteligência Artificial, responde automaticamente e registra todas as interações em banco de dados.
Sem automação da conta pessoal: toda a comunicação passa pela API oficial.
Sumário
Funcionalidades
Tecnologias
Arquitetura
Estrutura do projeto
Pré-requisitos
Instalação
Configuração da Meta
Variáveis de ambiente
Execução
Endpoints da API
Banco de dados
Testes
Segurança
Deploy
Funcionalidades futuras
Autor
Funcionalidades
Recebe mensagens do WhatsApp via webhook e identifica o número do usuário
Gera respostas com regras próprias e, opcionalmente, com IA (OpenAI)
Envia a resposta automaticamente pela API oficial
Registra mensagem, resposta, tipo, status e data/hora no banco
Anti-duplicidade: o mesmo evento nunca é respondido duas vezes
Trata tipos não suportados (imagem, áudio, documento) com resposta amigável
Consulta do histórico de conversas por API protegida
Logs, tratamento de erros e testes automatizados
Tecnologias
Camada
Tecnologia
Linguagem
Python 3.10+
Backend
FastAPI + Uvicorn
Banco de dados
SQLAlchemy + SQLite (desenvolvimento) / PostgreSQL (produção)
WhatsApp
WhatsApp Business Platform (Meta)
IA (opcional)
OpenAI
Cliente HTTP
httpx
Testes
pytest
Versionamento
Git / GitHub
Arquitetura
Usuário → WhatsApp → API da Meta → POST /webhook → FastAPI
                                                      │
                                       ┌──────────────┼──────────────┐
                                       ▼              ▼              ▼
                                 chat_service     ai_service    Banco (messages)
                                       │
                                       ▼
                               whatsapp_service → API da Meta → WhatsApp → Usuário
Fluxo do chat_service.process_incoming:
Verifica se a mensagem já foi processada (message_id)
Salva a mensagem recebida
Gera a resposta (regras → IA)
Salva a resposta e o status
Envia pelo WhatsApp (atualiza o status se falhar)
O webhook responde 200 imediatamente e processa em segundo plano, evitando reenvios da Meta por timeout.
Estrutura do projeto
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
│   ├── conftest.py
│   ├── test_webhook.py
│   └── test_chat.py
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
├── run.py
└── README.md
Pré-requisitos
Python 3.10 ou superior
Git
Conta de desenvolvedor na Meta (gratuita)
ngrok (ou similar) para testes locais
Chave da OpenAI (opcional)
Instalação
git clone https://github.com/jonapro23/ChatBot.git
cd ChatBot

python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env              # depois preencha os valores
Configuração da Meta (WhatsApp Business Platform)
Acesse developers.facebook.com e crie um aplicativo com o produto WhatsApp.
Em WhatsApp → Configuração da API, anote:
o token de acesso (o temporário expira em ~24h);
o Phone number ID do número de teste.
Adicione o seu número como destinatário autorizado e confirme o código recebido.
Invente um verify token (qualquer texto secreto) e use o mesmo valor no .env e no painel.
Após subir o servidor e o túnel (veja Execução), em WhatsApp → Configuração → Webhook:
URL de callback: https://SEU-TUNEL/webhook
Token de verificação: o valor de WHATSAPP_VERIFY_TOKEN
Clique em Verificar e salvar e assine o campo messages.
Variáveis de ambiente
Variável
Obrigatória
Descrição
WHATSAPP_ACCESS_TOKEN
✅
Token de acesso da Meta
WHATSAPP_PHONE_NUMBER_ID
✅
ID do número do WhatsApp Business
WHATSAPP_VERIFY_TOKEN
✅
Texto secreto usado na verificação do webhook
WHATSAPP_APP_SECRET
recomendada
Segredo do app; ativa a validação da assinatura X-Hub-Signature-256
GRAPH_API_VERSION
não
Versão da Graph API (padrão v21.0)
OPENAI_API_KEY
não
Vazia = o bot usa apenas as regras próprias
OPENAI_MODEL
não
Modelo da IA (padrão gpt-4o-mini)
DATABASE_URL
não
Padrão sqlite:///./chatbot.db
ADMIN_API_KEY
não
Chave do histórico. Vazia = rota /chat/history desativada
MAX_MESSAGE_LENGTH
não
Tamanho máximo aceito por mensagem (padrão 1000)
⚠️ Nunca envie o .env ao GitHub. Use o .env.example como modelo.
Execução
1. Inicie o servidor:
python run.py
API: http://localhost:8000
Documentação interativa (Swagger): http://localhost:8000/docs
2. Em outro terminal, exponha a porta:
ngrok http 8000
3. Configure a URL do ngrok no webhook da Meta (veja Configuração da Meta).
4. Teste: envie Olá para o número de teste e aguarde Olá! Como posso ajudar?.
Endpoints da API
Método
Rota
Descrição
GET
/webhook
Verificação do webhook pela Meta
POST
/webhook
Recebe os eventos do WhatsApp
GET
/chat/history
Histórico de conversas (requer X-API-Key)
GET
/health
Verificação de saúde
Histórico de conversas
Parâmetros: phone_number (filtro), limit (1–200, padrão 50) e offset.
curl -H "X-API-Key: SUA_CHAVE" \
  "http://localhost:8000/chat/history?limit=10"
[
  {
    "id": 1,
    "message_id": "wamid.XXXX",
    "phone_number": "5581999990000",
    "user_name": "Maria",
    "user_message": "Olá",
    "bot_response": "Olá! Como posso ajudar?",
    "message_type": "text",
    "status": "replied",
    "created_at": "2026-10-01T22:51:00Z"
  }
]
Banco de dados
Tabela messages, criada automaticamente ao iniciar o servidor:
Campo
Descrição
id
Identificador interno
message_id
ID da mensagem no WhatsApp (único, base da anti-duplicidade)
phone_number
Número do usuário
user_name
Nome disponível no evento
user_message
Texto recebido
bot_response
Resposta enviada
message_type
text, image, audio, document…
status
Status do processamento (abaixo)
created_at
Data/hora do registro
Status do processamento:
Status
Significado
received
Mensagem salva, resposta ainda em andamento
replied
Respondida com sucesso
unsupported
Tipo de mensagem não suportado
invalid
Mensagem vazia ou acima do limite
ai_error
Falha na IA (usuário recebeu mensagem genérica)
send_failed
A resposta foi gerada, mas o envio falhou
error
Erro inesperado no processamento
Testes
pytest
Os testes não usam a rede (o envio ao WhatsApp é simulado) e cobrem:
verificação do webhook (token correto e incorreto)
validação da assinatura da Meta
payload inválido e eventos de status
resposta a saudação
mensagens duplicadas
tipo de mensagem não suportado e mensagem muito longa
histórico: autenticação, listagem e filtro por número
Segurança
Credenciais somente em variáveis de ambiente (.env fora do Git)
Verificação do token do webhook e da assinatura X-Hub-Signature-256
Histórico protegido por chave de API
Limite de tamanho das mensagens
Telefones mascarados nos logs; detalhes técnicos só nos logs, nunca para o usuário
Armazenamento mínimo de dados pessoais
HTTPS obrigatório em produção
Deploy
Para produção, use um servidor com HTTPS (Render, Railway, AWS, Azure, Google Cloud…). Comando de inicialização:
uvicorn app.main:app --host 0.0.0.0 --port $PORT
Pontos de atenção:
Configure todas as variáveis de ambiente no provedor e defina WHATSAPP_APP_SECRET.
Em plataformas com disco efêmero o SQLite é perdido a cada deploy. Use PostgreSQL via DATABASE_URL (e instale o driver, ex.: pip install psycopg2-binary).
Troque o token temporário da Meta por um token permanente (usuário do sistema).
Atualize a URL do webhook no painel da Meta para o domínio definitivo.
Funcionalidades futuras
[ ] Menu automático e comandos (menu, ajuda, sair)
[ ] IA com contexto das mensagens anteriores
[ ] Painel administrativo (usuários, conversas, erros, atendimentos)
[ ] Autenticação de administradores
[ ] Suporte a imagem, áudio, PDF e documentos
[ ] Migrações de banco com Alembic
Autor
Desenvolvido por Jonathan Freitas — @jonapro23.