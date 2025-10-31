# Sistema de Monitoramento de Processos Judiciais

Sistema completo de backend para mineração, processamento e monitoramento de processos judiciais de tribunais brasileiros, desenvolvido com foco em alta performance, escalabilidade e processamento assíncrono de grandes volumes de dados.

## 🎯 Visão Geral

O projeto implementa uma solução robusta para:
- **Web Scraping**: Mineração automatizada de dados de tribunais (TJSP, TJRJ, STJ, etc.)
- **API RESTful**: Interface completa para gerenciamento de processos
- **Processamento Assíncrono**: Workers Celery para tarefas em background
- **Armazenamento Estruturado**: PostgreSQL com SQLAlchemy ORM
- **Cache**: Redis para otimização de performance
- **Monitoramento**: Métricas e logs de todas as operações

## 🚀 Tecnologias Utilizadas

### Core
- **Python 3.11+**
- **FastAPI**: Framework web assíncrono de alta performance
- **SQLAlchemy 2.0**: ORM com suporte assíncrono
- **PostgreSQL**: Banco de dados relacional
- **Redis**: Cache e broker de mensagens

### Web Scraping
- **aiohttp**: Cliente HTTP assíncrono
- **BeautifulSoup4**: Parse de HTML
- **lxml**: Parser XML/HTML de alta performance
- **tenacity**: Retry automático com backoff exponencial

### Processamento Assíncrono
- **Celery**: Fila de tarefas distribuída
- **asyncio**: Programação assíncrona nativa Python

### Qualidade de Código
- **pytest**: Framework de testes
- **pytest-asyncio**: Suporte a testes assíncronos
- **pytest-cov**: Cobertura de código
- **black**: Formatação de código
- **flake8**: Linting
- **mypy**: Type checking

### DevOps
- **Docker & Docker Compose**: Containerização
- **GitHub Actions**: CI/CD
- **Alembic**: Migrações de banco de dados

## 📁 Estrutura do Projeto

```
judicial-process-monitor/
├── src/
│   ├── api/              # Endpoints FastAPI
│   ├── config/           # Configurações
│   ├── models/           # Modelos SQLAlchemy
│   ├── schemas/          # Schemas Pydantic
│   ├── scrapers/         # Robôs de mineração
│   ├── services/         # Lógica de negócio
│   ├── repositories/     # Padrão Repository
│   ├── workers/          # Celery workers
│   └── utils/            # Utilitários
├── tests/                # Testes unitários e integração
├── docker/               # Configurações Docker
├── alembic/              # Migrações de banco
└── docs/                 # Documentação
```

## 🏗️ Arquitetura

### Padrões de Projeto Implementados

1. **Repository Pattern**: Abstração da camada de dados
2. **Factory Pattern**: Criação dinâmica de scrapers
3. **Dependency Injection**: Injeção de dependências via FastAPI
4. **Service Layer**: Separação da lógica de negócio

### Fluxo de Dados

```
API Request → Controller → Service → Repository → Database
                              ↓
                         Scraper → External Site
                              ↓
                         Worker (Celery) → Background Processing
```

## 🔧 Instalação e Configuração

### Pré-requisitos

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (opcional)

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/judicial-process-monitor.git
cd judicial-process-monitor
```

### 2. Configuração do Ambiente

```bash
# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale dependências
pip install -r requirements.txt
```

### 3. Configure Variáveis de Ambiente

```bash
cp .env.example .env
# Edite .env com suas configurações
```

### 4. Execute Migrações

```bash
alembic upgrade head
```

### 5. Inicie a Aplicação

```bash
# API
uvicorn src.main:app --reload

# Worker Celery
celery -A src.workers.tasks worker --loglevel=info

# Beat (scheduler)
celery -A src.workers.tasks beat --loglevel=info

# Flower (monitoramento)
celery -A src.workers.tasks flower
```

## 🐳 Docker

### Usando Docker Compose

```bash
# Inicia todos os serviços
docker-compose -f docker/docker-compose.yml up -d

# Verifica logs
docker-compose logs -f api

# Para todos os serviços
docker-compose down
```

### Serviços Disponíveis

- **API**: http://localhost:8000
- **Docs (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Flower**: http://localhost:5555
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## 📚 Uso da API

### Autenticação

```bash
# Atualmente não implementada, mas preparada para JWT
```

### Exemplos de Requisições

#### 1. Criar Tribunal

```bash
curl -X POST "http://localhost:8000/api/v1/courts/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tribunal de Justiça de São Paulo",
    "acronym": "TJSP",
    "court_type": "TJ",
    "state": "SP",
    "base_url": "https://esaj.tjsp.jus.br",
    "search_url": "https://esaj.tjsp.jus.br/cpopg/search.do"
  }'
```

#### 2. Fazer Scraping de Processo

```bash
curl -X POST "http://localhost:8000/api/v1/scraping/process/12345678920241234567" \
  -H "Content-Type: application/json" \
  -d '{
    "court_id": "uuid-do-tribunal",
    "force_update": false
  }'
```

#### 3. Buscar Processos

```bash
curl -X GET "http://localhost:8000/api/v1/processes/?query=ação&page=1&page_size=50"
```

#### 4. Scraping em Lote

```bash
curl -X POST "http://localhost:8000/api/v1/scraping/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "process_numbers": [
      "12345678920241234567",
      "98765432120241234567"
    ],
    "court_id": "uuid-do-tribunal",
    "priority": 5,
    "force_update": false
  }'
```

## 🧪 Testes

### Executar Testes

```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=src --cov-report=html

# Apenas testes unitários
pytest tests/unit/

# Apenas testes de integração
pytest tests/integration/

# Verbose
pytest -v
```

### Estrutura de Testes

- `tests/unit/`: Testes unitários (repositories, services, scrapers)
- `tests/integration/`: Testes de integração (API endpoints)
- `tests/fixtures/`: Dados de exemplo para testes

## 📊 Monitoramento e Logs

### Logs

Os logs são configurados com níveis:
- **DEBUG**: Desenvolvimento
- **INFO**: Produção (padrão)
- **WARNING**: Avisos
- **ERROR**: Erros

### Métricas

- Tempo de resposta das APIs
- Taxa de sucesso/falha do scraping
- Performance de workers Celery
- Utilização de recursos

### Flower (Celery Monitoring)

Acesse http://localhost:5555 para:
- Visualizar tasks em execução
- Histórico de execuções
- Métricas de workers
- Retry de tasks falhas

## 🔐 Segurança

### Implementado

- Validação de entrada com Pydantic
- SQL Injection protection (SQLAlchemy)
- Rate limiting preparado
- Secrets em variáveis de ambiente

### A Implementar

- Autenticação JWT
- Authorization (RBAC)
- API Keys para integração
- Criptografia de dados sensíveis

## 📈 Performance

### Otimizações Implementadas

1. **Async/Await**: Operações I/O não bloqueantes
2. **Connection Pooling**: PostgreSQL e Redis
3. **Batch Processing**: Scraping em lote
4. **Caching**: Redis para dados frequentes
5. **Indexes**: Otimização de queries SQL
6. **Lazy Loading**: SQLAlchemy relationships

### Benchmarks

- API: ~100-200 req/s (single worker)
- Scraping: ~5-10 processos/segundo
- Database: Suporta milhões de registros

## 🚦 CI/CD

### Pipeline GitHub Actions

1. **Test**: Linting, testes, cobertura
2. **Build**: Docker images
3. **Deploy**: Automático em main branch

### Qualidade de Código

- Cobertura mínima: 80%
- Black formatação
- Flake8 linting
- MyPy type checking

## 📝 Contribuindo

### Workflow

1. Fork o projeto
2. Crie branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para branch (`git push origin feature/nova-funcionalidade`)
5. Abra Pull Request

### Code Style

- Seguir PEP 8
- Usar Black para formatação
- Type hints em todas as funções
- Docstrings em classes e métodos públicos
- Testes para novas funcionalidades

## 🗺️ Roadmap

### v1.1
- [ ] Autenticação JWT
- [ ] WebSockets para notificações em tempo real
- [ ] Suporte a mais tribunais (TJRJ, STJ, STF)
- [ ] Dashboard administrativo

### v1.2
- [ ] Machine Learning para classificação de processos
- [ ] API GraphQL
- [ ] Exportação de relatórios (PDF, Excel)
- [ ] Integração com sistemas externos

### v2.0
- [ ] Microserviços architecture
- [ ] Kubernetes deployment
- [ ] ElasticSearch para busca full-text
- [ ] Análise preditiva de processos

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👥 Autores

- Seu Nome - [GitHub](https://github.com/seu-usuario)

## 🙏 Agradecimentos

- Comunidade FastAPI
- Documentação dos tribunais brasileiros
- Contributors do projeto

## 📞 Suporte

- Issues: [GitHub Issues](https://github.com/Meichl/judicial-process-monitor/issues)
- Email: suporte@example.com
- Documentação: [Wiki](https://github.com/Meichl/judicial-process-monitor/wiki)

---

**Nota**: Este é um projeto educacional/demonstrativo. Sempre verifique os termos de uso dos sites que serão minerados e respeite as políticas.