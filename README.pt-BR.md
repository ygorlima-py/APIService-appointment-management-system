[English](README.md)

# API REST - Sistema de Agendamento de Serviços

Uma aplicação completa desenvolvida em Django REST Framework para gerenciamento de clientes, agendamentos de serviços e acompanhamento de métricas diárias. Este sistema foi projetado para facilitar o controle de negócios que trabalham com agendamentos, como clínicas, salões de beleza, consultórios e prestadores de serviços em geral.

##  O que é esta aplicação?

Esta é uma **API RESTful** (Interface de Programação de Aplicações) que permite gerenciar:

- **Clientes**: Cadastro completo com informações de contato, documentos e notas
- **Agendamentos**: Controle de serviços agendados com horários, locais e status
- **Dashboard**: Relatórios diários com métricas de atendimentos e faturamento

###  Para que serve?

O sistema foi desenvolvido para resolver problemas comuns de negócios que trabalham com agendamentos:

1- Organizar informações de clientes de forma centralizada  
2- Agendar serviços evitando conflitos de horário no mesmo local  
3- Controlar o status dos agendamentos (Agendado, Confirmado, Cancelado, Concluído)  
4- Gerenciar múltiplas unidades/locais de atendimento  
5- Registrar formas de pagamento e valores  
6- Visualizar métricas diárias de atendimentos e faturamento  

##  Arquitetura da Aplicação

A aplicação utiliza tecnologias modernas e profissionais:

- **Django 5.2.8**: Framework web robusto e seguro
- **Django REST Framework**: Para construção da API RESTful
- **PostgreSQL 17**: Banco de dados profissional e confiável
- **Docker**: Containerização para facilitar instalação e deploy
- **Python 3.11.14**: Linguagem de programação moderna

###  Estrutura de Dados

**Modelo de Cliente (`Customer`)**
- Nome completo, telefone, e-mail e documento
- Campo de notas para observações importantes
- Status ativo/inativo
- Data de criação

**Modelo de Agendamento (`Appointment`)**
- Vinculado a um cliente
- Nome do serviço prestado
- Localização (Unidade 1, 2, 3 ou 4)
- Data/hora de início e término
- Status (Agendado, Confirmado, Cancelado, Concluído)
- Valor do serviço
- Forma de pagamento (Dinheiro, PIX, Cartão, Transferência)

###  Endpoints da API

A API oferece os seguintes endpoints:

**Clientes:**
- `GET /api/customers/` - Listar todos os clientes (com busca por nome, telefone ou e-mail usando `?q=termo`)
- `POST /api/customers/` - Criar novo cliente
- `GET /api/customers/{id}/` - Obter detalhes de um cliente específico
- `PUT/PATCH /api/customers/{id}/` - Atualizar dados de um cliente
- `DELETE /api/customers/{id}/` - Desativar um cliente (soft delete)

**Agendamentos:**
- `GET /api/appointment/` - Listar todos os agendamentos (com filtros por data, cliente e status)
- `POST /api/appointment/` - Criar novo agendamento
- `GET /api/appointment/{id}/` - Obter detalhes de um agendamento
- `PUT/PATCH /api/appointment/{id}/` - Atualizar um agendamento
- `DELETE /api/appointment/{id}/` - Cancelar um agendamento

**Dashboard:**
- `GET /api/dashboard/daily-summary/?date=YYYY-MM-DD` - Obter resumo do dia com métricas

##  Estrutura do Projeto

```
.
├── djangoapp/                 # Aplicação Django principal
│   ├── api_rest/             # App da API REST
│   │   ├── models.py         # Modelos de dados (Cliente, Agendamento)
│   │   ├── serializers.py    # Serialização de dados para JSON
│   │   ├── views.py          # Lógica dos endpoints da API
│   │   ├── urls.py           # Rotas da API
│   │   └── migrations/       # Migrações do banco de dados
│   ├── project/              # Configurações do Django
│   │   ├── settings.py       # Configurações principais
│   │   └── urls.py           # Rotas principais do projeto
│   ├── manage.py             # Utilitário de linha de comando do Django
│   └── requirements.txt      # Dependências Python
├── scripts/                   # Scripts auxiliares
│   ├── commands.sh           # Orquestrador de comandos de inicialização
│   ├── wait_psql.sh          # Aguarda PostgreSQL ficar pronto
│   ├── collectstatic.sh      # Coleta arquivos estáticos
│   ├── makemigrations.sh     # Gera migrações do banco
│   ├── migrate.sh            # Aplica migrações no banco
│   └── runserver.sh          # Inicia o servidor de desenvolvimento
├── dotenv_files/             # Arquivos de configuração de ambiente
│   └── .env                  # Variáveis de ambiente (criar este arquivo)
├── data/                     # Dados persistentes (criado automaticamente)
│   └── postgres/data/        # Dados do PostgreSQL
├── docker-compose.yml        # Configuração dos serviços Docker
├── Dockerfile                # Definição do container Django
└── readme.md                 # Este arquivo
```

##  Como Inicializar a Aplicação

### Pré-requisitos

Antes de começar, você precisa ter instalado em seu computador:

- **Docker**: Plataforma de containerização - [Instalar Docker](https://docs.docker.com/get-docker/)
- **Docker Compose**: Ferramenta para orquestrar múltiplos containers - [Instalar Docker Compose](https://docs.docker.com/compose/install/)

> **O que é Docker?** Docker é uma ferramenta que permite executar aplicações em "containers" - ambientes isolados que contêm tudo que a aplicação precisa para funcionar. Isso elimina problemas como "funciona na minha máquina mas não na sua".

### Passo 1: Configurar Variáveis de Ambiente

Primeiro, você precisa criar um arquivo de configuração que contém informações sensíveis como senhas do banco de dados.

1. **Crie a pasta** `dotenv_files` caso não exista
2. **Crie um arquivo** chamado `.env` dentro da pasta `dotenv_files`
3. **Adicione o seguinte conteúdo** ao arquivo `.env`:

```bash
# Configuração do Banco de Dados PostgreSQL
POSTGRES_DB=appointments_db
POSTGRES_USER=admin
POSTGRES_PASSWORD=sua_senha_segura_aqui

# Configuração do Django
SECRET_KEY=sua-chave-secreta-django-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

> **⚠️ Importante:** Altere `sua_senha_segura_aqui` e `sua-chave-secreta-django-aqui` para valores seguros antes de usar em produção.

### Passo 2: Construir e Iniciar os Containers

Abra um terminal na pasta raiz do projeto (onde está o arquivo `docker-compose.yml`) e execute:

```bash
docker-compose up --build
```

**O que este comando faz:**

1.  Constrói a imagem Docker da aplicação Django
2.  Baixa a imagem do PostgreSQL 17
3.  Inicia os containers `djangoapp` e `psql`
4.  Aguarda o PostgreSQL ficar pronto
5.  Coleta arquivos estáticos do Django
6.  Cria as tabelas no banco de dados (migrations)
7.  Inicia o servidor de desenvolvimento na porta 8001

**Aguarde a mensagem:**
```
Starting development server at http://0.0.0.0:8000/
```

Quando esta mensagem aparecer, sua aplicação está rodando! 

**Acesse a aplicação em:** http://localhost:8001

### Passo 3: Criar um Superusuário (Administrador)

Para acessar o painel administrativo do Django e gerenciar dados pela interface gráfica, você precisa criar um usuário administrador.

**Em um novo terminal**, execute:

```bash
docker-compose exec djangoapp python manage.py createsuperuser
```

O sistema vai solicitar as seguintes informações:

```
Username (deixe em branco para usar 'duser'): admin
Email address: seu-email@exemplo.com
Password: "sua senha aqui"
Password (again): "sua senha aqui"
```

> **Dica:** A senha precisa ter pelo menos 8 caracteres e não pode ser muito comum.

Após criar o superusuário, acesse o painel administrativo em: **http://localhost:8001/admin**

### Passo 4: Testando a API

Você pode testar os endpoints da API usando ferramentas como:

- **Navegador Web**: Para requisições GET simples
- **Postman**: Ferramenta gráfica para testar APIs - [Download Postman](https://www.postman.com/downloads/)
- **cURL**: Ferramenta de linha de comando (já vem instalada no Linux/Mac)

**Exemplo de teste com o navegador:**
- Acesse http://localhost:8001/api/customers/ para ver a lista de clientes

**Exemplo de teste com cURL:**
```bash
# Listar clientes
curl http://localhost:8001/api/customers/

# Criar um novo cliente
curl -X POST http://localhost:8001/api/customers/ \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "João Silva",
    "phone": "(11) 98765-4321",
    "email": "joao.silva@email.com",
    "id_document": "123.456.789-00"
  }'
```

## 🎮 Comandos Úteis

### Gerenciamento dos Containers

```bash
# Iniciar a aplicação (primeira vez ou após alterações)
docker-compose up --build

# Iniciar a aplicação em modo "background" (segundo plano)
docker-compose up -d

# Parar a aplicação
docker-compose down

# Parar e REMOVER todos os dados (cuidado: apaga o banco de dados)
docker-compose down -v

# Ver logs da aplicação em tempo real
docker-compose logs -f djangoapp

# Ver logs do banco de dados
docker-compose logs -f psql
```

### Comandos Django

Todos os comandos do Django devem ser executados **dentro do container** usando o prefixo `docker-compose exec djangoapp`:

```bash
# Criar um superusuário (administrador)
docker-compose exec djangoapp python manage.py createsuperuser

# Acessar o shell do Django (console Python interativo)
docker-compose exec djangoapp python manage.py shell

# Criar migrações após alterar models.py
docker-compose exec djangoapp python manage.py makemigrations

# Aplicar migrações no banco de dados
docker-compose exec djangoapp python manage.py migrate

# Coletar arquivos estáticos
docker-compose exec djangoapp python manage.py collectstatic

# Executar testes
docker-compose exec djangoapp python manage.py test

# Acessar o terminal do container
docker-compose exec djangoapp sh
```

##  Funcionalidades Principais

### 1. Gerenciamento de Clientes

O sistema armazena informações completas de clientes:
- Dados de contato (nome, telefone, e-mail)
- Documentos de identificação
- Campo de notas para observações
- Status ativo/inativo (soft delete)
- Validação de e-mail único

**Pesquisa inteligente**: Use o parâmetro `?q=` para buscar clientes por nome, telefone ou e-mail.

### 2. Sistema de Agendamentos

Controle completo de agendamentos com:
- **Prevenção de conflitos**: O sistema impede agendamentos simultâneos no mesmo local
- **Múltiplos status**: Acompanhe o ciclo de vida (Agendado → Confirmado → Concluído/Cancelado)
- **Múltiplas unidades**: Suporte para até 4 locais diferentes
- **Controle financeiro**: Registro de valores e formas de pagamento
- **Validações automáticas**: 
  - Horário de término deve ser posterior ao início
  - Cliente deve estar ativo para agendar

### 3. Dashboard de Métricas

O endpoint de dashboard fornece um resumo completo do dia:
- Total de agendamentos
- Quantidade por status (Agendado, Confirmado, Cancelado, Concluído)
- Faturamento total dos serviços concluídos

**Exemplo de uso:**
```
GET /api/dashboard/daily-summary/?date=2026-01-08
```

##  Segurança

### Boas Práticas Implementadas

✅ Usuário não-root no container Docker (`duser`)  
✅ Validação de dados nos serializers  
✅ Soft delete para clientes (dados preservados)  
✅ Validação de conflitos de agendamento  
✅ Campos obrigatórios e validações de modelo  

###  Antes de Usar em Produção

- [ ] Alterar o `SECRET_KEY` do Django
- [ ] Definir `DEBUG = False`
- [ ] Configurar `ALLOWED_HOSTS` corretamente
- [ ] Usar senhas fortes no banco de dados
- [ ] Implementar HTTPS
- [ ] Adicionar autenticação JWT ou Token
- [ ] Configurar backup automático do banco de dados
- [ ] Implementar rate limiting
- [ ] Revisar permissões e autorizações

## � Deploy em Produção com Nginx em VPS

Esta seção fornece um guia completo e didático para fazer o deploy da aplicação em um servidor VPS (Virtual Private Server) usando Nginx como proxy reverso.

### 📋 O que você vai precisar

- **VPS**: Um servidor virtual (ex: DigitalOcean, AWS EC2, Linode, Contabo)
- **Sistema Operacional**: Ubuntu 20.04+ ou Debian 11+ (Ubuntu recomendado)
- **Domínio**: Um nome de domínio apontando para o IP do seu VPS (opcional, mas recomendado)
- **Acesso SSH**: Para conectar no servidor

### 🔄 Fluxograma do Processo de Deploy

```
┌─────────────────────────────────────────────────────────┐
│  1. PREPARAR O SERVIDOR VPS                             │
│  ├─ Conectar via SSH                                    │
│  ├─ Atualizar sistema operacional                       │
│  └─ Instalar dependências (Docker, Docker Compose, Git) │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  2. CLONAR E CONFIGURAR A APLICAÇÃO                     │
│  ├─ Clonar repositório do projeto                       │
│  ├─ Configurar variáveis de ambiente (.env)             │
│  └─ Ajustar configurações de segurança                  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  3. CONFIGURAR DOCKER PARA PRODUÇÃO                     │
│  ├─ Modificar docker-compose.yml                        │
│  ├─ Construir e iniciar containers                      │
│  └─ Criar superusuário Django                           │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  4. INSTALAR E CONFIGURAR NGINX                         │
│  ├─ Instalar Nginx                                      │
│  ├─ Criar arquivo de configuração do site               │
│  ├─ Configurar proxy reverso para Django                │
│  └─ Ativar configuração                                 │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  5. CONFIGURAR SSL/HTTPS (CERTBOT)                      │
│  ├─ Instalar Certbot                                    │
│  ├─ Obter certificado SSL gratuito                      │
│  └─ Configurar renovação automática                     │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  6. TESTAR E MONITORAR                                  │
│  ├─ Testar acesso via HTTPS                             │
│  ├─ Verificar logs                                      │
│  └─ Configurar monitoramento                            │
└─────────────────────────────────────────────────────────┘
```

### 📝 Passo a Passo Detalhado

#### **Passo 1: Preparar o Servidor VPS**

**1.1 - Conectar no servidor via SSH**

No seu computador local, abra o terminal e conecte ao servidor:

```bash
ssh usuario@SEU_IP_DO_SERVIDOR

# Exemplo:
# ssh root@192.168.1.100
```

**1.2 - Atualizar o sistema operacional**

```bash
# Atualizar lista de pacotes
sudo apt update

# Atualizar pacotes instalados
sudo apt upgrade -y
```

**1.3 - Instalar Docker**

```bash
# Instalar dependências
sudo apt install apt-transport-https ca-certificates curl software-properties-common -y

# Adicionar chave GPG oficial do Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Adicionar repositório do Docker
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Atualizar lista de pacotes novamente
sudo apt update

# Instalar Docker
sudo apt install docker-ce docker-ce-cli containerd.io -y

# Verificar se está rodando
sudo systemctl status docker
```

**1.4 - Instalar Docker Compose**

```bash
# Baixar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Dar permissão de execução
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalação
docker-compose --version
```

**1.5 - Instalar Git**

```bash
sudo apt install git -y
```

#### **Passo 2: Clonar e Configurar a Aplicação**

**2.1 - Criar diretório para aplicações**

```bash
# Criar pasta para projetos
sudo mkdir -p /var/www
cd /var/www
```

**2.2 - Clonar o repositório**

```bash
# Clonar seu projeto (substitua pela URL do seu repositório)
sudo git clone https://github.com/seu-usuario/django-api-rest.git
cd django-api-rest
```

**2.3 - Configurar variáveis de ambiente**

```bash
# Criar pasta dotenv_files se não existir
sudo mkdir -p dotenv_files

# Criar arquivo .env
sudo nano dotenv_files/.env
```

Adicione as seguintes configurações **de produção**:

```bash
# Configuração do Banco de Dados PostgreSQL
POSTGRES_DB=appointments_prod
POSTGRES_USER=admin_prod
POSTGRES_PASSWORD=SuaSenhaSuperSegura123!@#

# Configuração do Django (PRODUÇÃO)
SECRET_KEY=sua-chave-secreta-super-longa-e-complexa-aqui-12345678
DEBUG=False
ALLOWED_HOSTS=seudominio.com,www.seudominio.com,SEU_IP_VPS
```

> **IMPORTANTE:** 
> - Troque `SuaSenhaSuperSegura123!@#` por uma senha forte
> - Gere uma nova `SECRET_KEY` única (use: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`)
> - Defina `DEBUG=False` em produção
> - Substitua `seudominio.com` pelo seu domínio real

Para salvar no nano: `Ctrl+O`, `Enter`, `Ctrl+X`

#### **Passo 3: Configurar Docker para Produção**

**3.1 - Ajustar docker-compose.yml**

Edite o arquivo para mudar a porta:

```bash
sudo nano docker-compose.yml
```

Modifique a linha da porta para:

```yaml
ports:
  - "127.0.0.1:8000:8000"  # Apenas local, Nginx vai fazer o proxy
```

**3.2 - Iniciar a aplicação**

```bash
# Construir e iniciar containers em background
sudo docker-compose up --build -d

# Verificar se os containers estão rodando
sudo docker-compose ps

# Ver logs
sudo docker-compose logs -f
```

**3.3 - Criar superusuário**

```bash
sudo docker-compose exec djangoapp python manage.py createsuperuser
```

#### **Passo 4: Instalar e Configurar Nginx**

**4.1 - Instalar Nginx**

```bash
sudo apt install nginx -y

# Verificar status
sudo systemctl status nginx
```

**4.2 - Criar configuração do site**

```bash
# Criar arquivo de configuração
sudo nano /etc/nginx/sites-available/django-api
```

Adicione a seguinte configuração:

```nginx
# Configuração Nginx para Django API REST
server {
    listen 80;
    server_name seudominio.com www.seudominio.com;  # Substitua pelo seu domínio

    # Logs
    access_log /var/log/nginx/django_access.log;
    error_log /var/log/nginx/django_error.log;

    # Tamanho máximo de upload
    client_max_body_size 100M;

    # Proxy para a aplicação Django
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # Arquivos estáticos (se necessário)
    location /static/ {
        alias /var/www/django-api-rest/data/web/static/;
    }

    # Arquivos de mídia (se necessário)
    location /media/ {
        alias /var/www/django-api-rest/data/web/media/;
    }
}
```

> **💡 Explicação:**
> - `listen 80`: Nginx escuta na porta 80 (HTTP)
> - `server_name`: Seu domínio (ou IP do servidor)
> - `proxy_pass`: Redireciona requisições para Django na porta 8000
> - `proxy_set_header`: Preserva informações da requisição original
> - `location /static/` e `/media/`: Servir arquivos estáticos diretamente pelo Nginx (mais eficiente)

Para salvar: `Ctrl+O`, `Enter`, `Ctrl+X`

**4.3 - Ativar configuração**

```bash
# Criar link simbólico para ativar o site
sudo ln -s /etc/nginx/sites-available/django-api /etc/nginx/sites-enabled/

# Remover configuração padrão (opcional)
sudo rm /etc/nginx/sites-enabled/default

# Testar configuração do Nginx
sudo nginx -t

# Se o teste passar, recarregar Nginx
sudo systemctl reload nginx
```

**4.4 - Configurar Firewall (UFW)**

```bash
# Permitir Nginx Full (HTTP e HTTPS)
sudo ufw allow 'Nginx Full'

# Permitir SSH (importante para não perder acesso!)
sudo ufw allow OpenSSH

# Ativar firewall
sudo ufw enable

# Verificar status
sudo ufw status
```

**Neste ponto, sua aplicação já deve estar acessível via:** `http://seudominio.com`

#### **Passo 5: Configurar SSL/HTTPS com Certbot**

HTTPS é **essencial** para segurança em produção. Vamos usar o Let's Encrypt (gratuito).

**5.1 - Instalar Certbot**

```bash
# Instalar Certbot e plugin do Nginx
sudo apt install certbot python3-certbot-nginx -y
```

**5.2 - Obter certificado SSL**

```bash
# Obter e configurar certificado automaticamente
sudo certbot --nginx -d seudominio.com -d www.seudominio.com

# Durante o processo, você será perguntado:
# - Email: Seu email para notificações
# - Termos: Aceite os termos de serviço
# - Redirecionamento: Escolha opção 2 (redirecionar HTTP para HTTPS)
```

> **💡 O Certbot vai:**
> - Obter o certificado SSL gratuitamente
> - Modificar automaticamente a configuração do Nginx
> - Configurar redirecionamento de HTTP para HTTPS

**5.3 - Testar renovação automática**

```bash
# Testar renovação (sem realmente renovar)
sudo certbot renew --dry-run

# Se passar, a renovação automática está configurada!
```

O Certbot configura automaticamente um cronjob para renovar os certificados antes de expirarem (a cada 90 dias).

**5.4 - Verificar configuração final do Nginx**

```bash
sudo nano /etc/nginx/sites-available/django-api
```

Após o Certbot, seu arquivo deve ter algo assim:

```nginx
server {
    server_name seudominio.com www.seudominio.com;

    # ... suas configurações anteriores ...

    listen 443 ssl;  # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/seudominio.com/fullchain.pem;  # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/seudominio.com/privkey.pem;  # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf;  # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;  # managed by Certbot
}

# Redirecionar HTTP para HTTPS
server {
    if ($host = www.seudominio.com) {
        return 301 https://$host$request_uri;
    }

    if ($host = seudominio.com) {
        return 301 https://$host$request_uri;
    }

    listen 80;
    server_name seudominio.com www.seudominio.com;
    return 404;
}
```

#### **Passo 6: Testar e Monitorar**

**6.1 - Testar a aplicação**

Acesse no navegador:
- `https://seudominio.com/api/customers/` ✅
- `https://seudominio.com/admin/` ✅

**6.2 - Verificar logs**

```bash
# Logs do Nginx
sudo tail -f /var/log/nginx/django_access.log
sudo tail -f /var/log/nginx/django_error.log

# Logs do Django
cd /var/www/django-api-rest
sudo docker-compose logs -f djangoapp
```

**6.3 - Comandos úteis para gerenciamento**

```bash
# Reiniciar Nginx
sudo systemctl restart nginx

# Reiniciar aplicação Django
sudo docker-compose restart

# Ver status dos containers
sudo docker-compose ps

# Fazer backup do banco de dados
sudo docker-compose exec psql pg_dump -U admin_prod appointments_prod > backup_$(date +%Y%m%d).sql

# Atualizar a aplicação (após git pull)
cd /var/www/django-api-rest
sudo git pull
sudo docker-compose up --build -d
sudo docker-compose exec djangoapp python manage.py migrate
sudo docker-compose exec djangoapp python manage.py collectstatic --noinput
sudo systemctl reload nginx
```

### 🎯 Checklist Final de Deploy

- [ ] Servidor VPS provisionado e atualizado
- [ ] Docker e Docker Compose instalados
- [ ] Aplicação clonada e configurada
- [ ] Variáveis de ambiente configuradas (DEBUG=False)
- [ ] SECRET_KEY alterada para valor único
- [ ] Containers Docker rodando corretamente
- [ ] Nginx instalado e configurado
- [ ] Firewall (UFW) configurado
- [ ] Certificado SSL instalado via Certbot
- [ ] HTTPS funcionando corretamente
- [ ] Redirecionamento HTTP → HTTPS ativo
- [ ] Admin Django acessível
- [ ] Endpoints da API funcionando
- [ ] Logs sendo gerados corretamente
- [ ] Backup do banco de dados configurado

### 🛡️ Dicas de Segurança Adicionais

1. **Altere a porta SSH padrão**
   ```bash
   sudo nano /etc/ssh/sshd_config
   # Mude: Port 22 para Port 2222
   sudo systemctl restart sshd
   ```

2. **Configure fail2ban** (protege contra ataques de força bruta)
   ```bash
   sudo apt install fail2ban -y
   sudo systemctl enable fail2ban
   ```

3. **Desabilite login root via SSH**
   ```bash
   sudo nano /etc/ssh/sshd_config
   # PermitRootLogin no
   ```

4. **Configure backups automáticos**
   ```bash
   # Criar script de backup
   sudo nano /usr/local/bin/backup-django.sh
   ```

### 📊 Monitoramento e Manutenção

**Configurar logs rotativos:**
```bash
sudo nano /etc/logrotate.d/django-api
```

```
/var/log/nginx/django_*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
}
```

**Verificar uso de recursos:**
```bash
# CPU e memória
htop

# Espaço em disco
df -h

# Status dos containers
sudo docker stats
```

### 🆘 Resolução de Problemas Comuns

**Problema: Nginx retorna 502 Bad Gateway**
```bash
# Verificar se Django está rodando
sudo docker-compose ps
sudo docker-compose logs djangoapp

# Verificar conectividade
curl http://127.0.0.1:8000
```

**Problema: Certificado SSL não renova automaticamente**
```bash
# Forçar renovação
sudo certbot renew --force-renewal
sudo systemctl reload nginx
```

**Problema: Aplicação lenta**
```bash
# Verificar recursos
sudo docker stats

# Aumentar workers do Django (se necessário)
# Adicionar Gunicorn ao projeto para melhor performance
```

## �🐳 Detalhes da Configuração Docker

### Serviços

**djangoapp**
- **Imagem base**: Python 3.11.14 Alpine
- **Porta exposta**: 8001 → 8000 (container)
- **Volumes**: Código da aplicação, arquivos estáticos e mídia
- **Usuário**: duser (não-root)

**psql**
- **Imagem**: postgres:17-alpine
- **Volume persistente**: `./data/postgres/data`
- **Porta**: 5432 (apenas interna)

### Volumes Docker

- `static_volume`: Arquivos estáticos do Django (CSS, JS, imagens)
- `media_volume`: Arquivos enviados pelos usuários
- `./data/postgres/data`: Dados do banco PostgreSQL

##  Tecnologias e Conceitos

### O que é uma API REST?

REST (Representational State Transfer) é um estilo de arquitetura para APIs que usa:
- **HTTP como protocolo**: Métodos GET, POST, PUT, PATCH, DELETE
- **URLs como recursos**: Cada URL representa um recurso (clientes, agendamentos)
- **JSON como formato**: Dados trafegam em formato JSON (JavaScript Object Notation)
- **Stateless**: Cada requisição é independente

### Por que Django REST Framework?

- Framework maduro e estável
- Documentação automática da API
- Serialização automática de dados
- Validação robusta
- Suporte a autenticação e permissões
- Amplamente utilizado na indústria

### Por que PostgreSQL?

- Banco de dados relacional robusto e confiável
- Suporte a transações ACID
- Performance em alta escala
- Open source e amplamente utilizado
- Excelente integração com Django

##  Resolução de Problemas

### A aplicação não inicia

1. Verifique se o Docker está rodando: `docker --version`
2. Verifique se o arquivo `.env` existe em `dotenv_files/.env`
3. Verifique os logs: `docker-compose logs`

### Erro de conexão com o banco de dados

1. Aguarde alguns segundos - o PostgreSQL pode demorar para iniciar
2. Verifique se o container do PostgreSQL está rodando: `docker-compose ps`
3. Reinicie os containers: `docker-compose restart`

### Erro "port is already in use"

A porta 8001 já está sendo usada por outro programa:
1. Pare o programa que está usando a porta
2. Ou altere a porta no `docker-compose.yml` (linha `ports: - 127.0.0.1:8001:8000`)

### Como resetar o banco de dados

```bash
#  CUIDADO: Isto apaga todos os dados!
docker-compose down -v
docker-compose up --build
```

##  Suporte

Para dúvidas ou problemas:

**Desenvolvedor:** Ygor Lima  
**Email:** ygor.limarsx@gmail.com

---

**Nota Educacional:** Este projeto foi desenvolvido seguindo as melhores práticas de desenvolvimento web moderno, utilizando padrões da indústria e arquitetura profissional. É uma excelente base para aprendizado e para construção de sistemas reais de agendamento.

